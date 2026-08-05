"""
Auto Job Applier LinkedIn - Desktop GUI Application
Features:
- Version Selection: Interactive Mode vs Auto Mode (No confirmation, random delays <30s)
- Process Controls: Start Script and Terminate Script
- Sidebar: Real-time Live Log of Successfully Applied Jobs
- Settings Menu: In-app editor for automation parameters (Search terms, location, filters, salary, delays)
- Embedded / Docked Chrome Browser View via Win32 API
"""

import os
import sys
import csv
import time
import signal
import threading
import subprocess
import tkinter as tk
import customtkinter as ctk

from modules.config_manager import load_all_settings, save_all_settings

# Try importing win32 modules for browser window docking
try:
    import win32gui
    import win32process
    import win32con
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Automation Settings & Preferences")
        self.geometry("680x720")
        self.resizable(False, False)
        self.grab_set()  # Modal window

        self.current_settings = load_all_settings()
        self._build_ui()

    def _build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(15, 5))

        title = ctk.CTkLabel(header, text="⚙️ Automation Settings & Preferences", font=ctk.CTkFont(size=18, weight="bold"))
        title.pack(side="left")

        # Scrollable Form
        form = ctk.CTkScrollableFrame(self, fg_color="#161B22", corner_radius=8)
        form.pack(fill="both", expand=True, padx=20, pady=10)

        # SECTION 1: SEARCH PREFERENCES
        sec1_lbl = ctk.CTkLabel(form, text="🔍 Job Search Preferences", font=ctk.CTkFont(size=14, weight="bold"), text_color="#388BFD")
        sec1_lbl.pack(anchor="w", padx=10, pady=(10, 5))

        # Search Terms
        ctk.CTkLabel(form, text="Search Titles / Keywords (comma separated):", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=10, pady=(5, 2))
        self.terms_entry = ctk.CTkEntry(form, placeholder_text="e.g. Data Analyst, Software Engineer", width=580)
        self.terms_entry.pack(anchor="w", padx=10, pady=(0, 10))
        terms_str = ", ".join(self.current_settings.get("search_terms", []))
        self.terms_entry.insert(0, terms_str)

        # Search Location
        ctk.CTkLabel(form, text="Search Location:", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=10, pady=(5, 2))
        self.location_entry = ctk.CTkEntry(form, placeholder_text="e.g. San Francisco or United States", width=580)
        self.location_entry.pack(anchor="w", padx=10, pady=(0, 10))
        self.location_entry.insert(0, self.current_settings.get("search_location", ""))

        # Date Posted Filter
        ctk.CTkLabel(form, text="Date Posted Filter:", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=10, pady=(5, 2))
        self.date_posted_menu = ctk.CTkOptionMenu(
            form, values=["Past 24 hours", "Past week", "Past month", "Any time", ""], width=200
        )
        self.date_posted_menu.pack(anchor="w", padx=10, pady=(0, 10))
        self.date_posted_menu.set(self.current_settings.get("date_posted", "Past week"))

        # On-Site / Remote Checkboxes
        ctk.CTkLabel(form, text="Work Location Modes:", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=10, pady=(5, 2))
        mode_frame = ctk.CTkFrame(form, fg_color="transparent")
        mode_frame.pack(anchor="w", padx=10, pady=(0, 10))

        curr_modes = self.current_settings.get("on_site", [])
        self.mode_remote_var = ctk.BooleanVar(value="Remote" in curr_modes)
        self.mode_hybrid_var = ctk.BooleanVar(value="Hybrid" in curr_modes)
        self.mode_onsite_var = ctk.BooleanVar(value="On-site" in curr_modes)

        ctk.CTkCheckBox(mode_frame, text="Remote", variable=self.mode_remote_var).pack(side="left", padx=(0, 15))
        ctk.CTkCheckBox(mode_frame, text="Hybrid", variable=self.mode_hybrid_var).pack(side="left", padx=(0, 15))
        ctk.CTkCheckBox(mode_frame, text="On-site", variable=self.mode_onsite_var).pack(side="left")

        # Job Types Checkboxes
        ctk.CTkLabel(form, text="Job Types:", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=10, pady=(5, 2))
        type_frame = ctk.CTkFrame(form, fg_color="transparent")
        type_frame.pack(anchor="w", padx=10, pady=(0, 10))

        curr_types = self.current_settings.get("job_type", [])
        self.type_ft_var = ctk.BooleanVar(value="Full-time" in curr_types)
        self.type_contract_var = ctk.BooleanVar(value="Contract" in curr_types)
        self.type_pt_var = ctk.BooleanVar(value="Part-time" in curr_types)

        ctk.CTkCheckBox(type_frame, text="Full-time", variable=self.type_ft_var).pack(side="left", padx=(0, 15))
        ctk.CTkCheckBox(type_frame, text="Contract", variable=self.type_contract_var).pack(side="left", padx=(0, 15))
        ctk.CTkCheckBox(type_frame, text="Part-time", variable=self.type_pt_var).pack(side="left")

        # Divider
        ctk.CTkFrame(form, height=1, fg_color="#2A2D32").pack(fill="x", padx=10, pady=10)

        # SECTION 2: PERSONAL & SALARY
        sec2_lbl = ctk.CTkLabel(form, text="👤 Personal & Salary Target", font=ctk.CTkFont(size=14, weight="bold"), text_color="#2EA043")
        sec2_lbl.pack(anchor="w", padx=10, pady=(5, 5))

        sal_frame = ctk.CTkFrame(form, fg_color="transparent")
        sal_frame.pack(anchor="w", padx=10, pady=(0, 10))

        # Desired Salary
        f1 = ctk.CTkFrame(sal_frame, fg_color="transparent")
        f1.pack(side="left", padx=(0, 20))
        ctk.CTkLabel(f1, text="Target Desired Salary ($):", font=ctk.CTkFont(size=12)).pack(anchor="w")
        self.salary_entry = ctk.CTkEntry(f1, width=170)
        self.salary_entry.pack(anchor="w", pady=(2, 0))
        self.salary_entry.insert(0, str(self.current_settings.get("desired_salary", 120000)))

        # Current Experience
        f2 = ctk.CTkFrame(sal_frame, fg_color="transparent")
        f2.pack(side="left", padx=(0, 20))
        ctk.CTkLabel(f2, text="Current Experience (years):", font=ctk.CTkFont(size=12)).pack(anchor="w")
        self.exp_entry = ctk.CTkEntry(f2, width=170)
        self.exp_entry.pack(anchor="w", pady=(2, 0))
        self.exp_entry.insert(0, str(self.current_settings.get("current_experience", 7)))

        # Notice Period
        f3 = ctk.CTkFrame(sal_frame, fg_color="transparent")
        f3.pack(side="left")
        ctk.CTkLabel(f3, text="Notice Period (days):", font=ctk.CTkFont(size=12)).pack(anchor="w")
        self.notice_entry = ctk.CTkEntry(f3, width=170)
        self.notice_entry.pack(anchor="w", pady=(2, 0))
        self.notice_entry.insert(0, str(self.current_settings.get("notice_period", 14)))

        # Divider
        ctk.CTkFrame(form, height=1, fg_color="#2A2D32").pack(fill="x", padx=10, pady=10)

        # SECTION 3: BOT OPTIONS
        sec3_lbl = ctk.CTkLabel(form, text="⚙️ Bot Controls & Delays", font=ctk.CTkFont(size=14, weight="bold"), text_color="#E3B341")
        sec3_lbl.pack(anchor="w", padx=10, pady=(5, 5))

        bot_frame = ctk.CTkFrame(form, fg_color="transparent")
        bot_frame.pack(anchor="w", padx=10, pady=(0, 10))

        # Click Gap
        bf1 = ctk.CTkFrame(bot_frame, fg_color="transparent")
        bf1.pack(side="left", padx=(0, 20))
        ctk.CTkLabel(bf1, text="Action Click Gap (seconds):", font=ctk.CTkFont(size=12)).pack(anchor="w")
        self.gap_entry = ctk.CTkEntry(bf1, width=170)
        self.gap_entry.pack(anchor="w", pady=(2, 0))
        self.gap_entry.insert(0, str(self.current_settings.get("click_gap", 1)))

        # Chrome Profile
        bf2 = ctk.CTkFrame(bot_frame, fg_color="transparent")
        bf2.pack(side="left")
        ctk.CTkLabel(bf2, text="Chrome Profile Directory:", font=ctk.CTkFont(size=12)).pack(anchor="w")
        self.profile_entry = ctk.CTkEntry(bf2, width=170)
        self.profile_entry.pack(anchor="w", pady=(2, 0))
        self.profile_entry.insert(0, str(self.current_settings.get("chrome_profile", "Default")))

        # Action Buttons Footer
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(fill="x", padx=20, pady=(5, 15))

        self.save_btn = ctk.CTkButton(
            footer, text="💾 Save Settings", font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#2EA043", hover_color="#268637", height=36, width=140, command=self.save_settings
        )
        self.save_btn.pack(side="right", padx=(10, 0))

        self.cancel_btn = ctk.CTkButton(
            footer, text="Cancel", font=ctk.CTkFont(size=14),
            fg_color="#30363D", hover_color="#484F58", height=36, width=100, command=self.destroy
        )
        self.cancel_btn.pack(side="right")

    def save_settings(self):
        try:
            # Parse terms
            raw_terms = self.terms_entry.get().strip()
            terms_list = [t.strip() for t in raw_terms.split(",") if t.strip()]

            # Work modes
            modes = []
            if self.mode_remote_var.get(): modes.append("Remote")
            if self.mode_hybrid_var.get(): modes.append("Hybrid")
            if self.mode_onsite_var.get(): modes.append("On-site")

            # Job types
            types = []
            if self.type_ft_var.get(): types.append("Full-time")
            if self.type_contract_var.get(): types.append("Contract")
            if self.type_pt_var.get(): types.append("Part-time")

            new_data = {
                "search_terms": terms_list if terms_list else ["Data Analyst"],
                "search_location": self.location_entry.get().strip(),
                "date_posted": self.date_posted_menu.get(),
                "on_site": modes,
                "job_type": types,
                "desired_salary": int(float(self.salary_entry.get() or 120000)),
                "current_experience": int(float(self.exp_entry.get() or 7)),
                "notice_period": int(float(self.notice_entry.get() or 14)),
                "click_gap": int(float(self.gap_entry.get() or 1)),
                "chrome_profile": self.profile_entry.get().strip() or "Default"
            }

            if save_all_settings(new_data):
                self.parent.log_console("Settings successfully updated and saved to config files!")
                self.destroy()
            else:
                self.parent.log_console("Failed to save some settings. Please check config file permissions.")
        except Exception as e:
            self.parent.log_console(f"Error saving settings: {e}")


class AutoJobApplierApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Auto Job Applier LinkedIn")
        self.geometry("1400x850")
        self.minsize(1100, 700)

        self.bot_process = None
        self.is_running = False
        self.last_applied_count = 0
        self.applied_jobs_data = []

        # Configure root grid
        self.grid_columnconfigure(0, weight=0)  # Sidebar fixed width
        self.grid_columnconfigure(1, weight=1)  # Main panel (Browser Container)
        self.grid_rowconfigure(0, weight=1)

        # Build UI
        self._build_sidebar()
        self._build_main_panel()

        # Start background polling loops
        self._start_live_log_polling()
        self._start_browser_docking_loop()

        # Protocol for graceful window closing
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=420, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.sidebar.grid_rowconfigure(5, weight=1)  # Scrollable job list expands

        # App Header
        header_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="ew")

        title_label = ctk.CTkLabel(header_frame, text="Auto Job Applier", font=ctk.CTkFont(size=20, weight="bold"))
        title_label.pack(side="left", padx=2)

        self.status_badge = ctk.CTkLabel(header_frame, text="IDLE", font=ctk.CTkFont(size=11, weight="bold"),
                                         fg_color="#3A3D40", text_color="#AAAAAA", corner_radius=6, padx=8, pady=2)
        self.status_badge.pack(side="right", padx=2)

        self.settings_btn = ctk.CTkButton(
            header_frame, text="⚙️ Settings", font=ctk.CTkFont(size=12, weight="bold"),
            width=85, height=28, fg_color="#21262D", hover_color="#30363D", command=self.open_settings_window
        )
        self.settings_btn.pack(side="right", padx=5)

        # Divider
        divider1 = ctk.CTkFrame(self.sidebar, height=2, fg_color="#2A2D32")
        divider1.grid(row=1, column=0, padx=15, pady=5, sticky="ew")

        # Script Version Selector Section
        mode_frame = ctk.CTkFrame(self.sidebar, fg_color="#1E2023", corner_radius=8)
        mode_frame.grid(row=2, column=0, padx=15, pady=8, sticky="ew")

        mode_title = ctk.CTkLabel(mode_frame, text="Select Script Mode:", font=ctk.CTkFont(size=13, weight="bold"))
        mode_title.pack(anchor="w", padx=12, pady=(10, 5))

        self.mode_var = ctk.StringVar(value="interactive")

        self.radio_interactive = ctk.CTkRadioButton(
            mode_frame, text="🔵 Interactive Mode (Standard / Default)", 
            variable=self.mode_var, value="interactive", font=ctk.CTkFont(size=12)
        )
        self.radio_interactive.pack(anchor="w", padx=15, pady=5)

        self.radio_auto = ctk.CTkRadioButton(
            mode_frame, text="⚡ Auto Mode (No prompt, delays <30s)", 
            variable=self.mode_var, value="auto", font=ctk.CTkFont(size=12)
        )
        self.radio_auto.pack(anchor="w", padx=15, pady=(5, 10))

        # Control Buttons (Start / Terminate)
        controls_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        controls_frame.grid(row=3, column=0, padx=15, pady=8, sticky="ew")

        self.start_btn = ctk.CTkButton(
            controls_frame, text="▶  Start Script", font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#2EA043", hover_color="#268637", height=38, command=self.start_script
        )
        self.start_btn.pack(side="left", expand=True, fill="x", padx=(0, 5))

        self.terminate_btn = ctk.CTkButton(
            controls_frame, text="🛑  Terminate Script", font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#DA3633", hover_color="#B82C29", height=38, command=self.terminate_script, state="disabled"
        )
        self.terminate_btn.pack(side="right", expand=True, fill="x", padx=(5, 0))

        # Applied Jobs Log Header
        jobs_header_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        jobs_header_frame.grid(row=4, column=0, padx=15, pady=(15, 5), sticky="ew")

        jobs_title = ctk.CTkLabel(jobs_header_frame, text="Successfully Applied Jobs", font=ctk.CTkFont(size=14, weight="bold"))
        jobs_title.pack(side="left")

        self.job_count_label = ctk.CTkLabel(jobs_header_frame, text="0 Jobs", font=ctk.CTkFont(size=12), text_color="#8B949E")
        self.job_count_label.pack(side="right")

        # Scrollable Applied Jobs Feed
        self.jobs_feed = ctk.CTkScrollableFrame(self.sidebar, fg_color="#161B22", corner_radius=8)
        self.jobs_feed.grid(row=5, column=0, padx=15, pady=(5, 10), sticky="nsew")

        # Initial placeholder label
        self.empty_label = ctk.CTkLabel(
            self.jobs_feed, text="No applied jobs logged yet.\nClick 'Start Script' to begin.", 
            text_color="#8B949E", font=ctk.CTkFont(size=12)
        )
        self.empty_label.pack(pady=40)

        # Terminal Log View Toggle
        self.console_box = ctk.CTkTextbox(self.sidebar, height=120, font=ctk.CTkFont(family="Consolas", size=10), fg_color="#0D1117")
        self.console_box.grid(row=6, column=0, padx=15, pady=(0, 15), sticky="ew")
        self.console_box.insert("1.0", "System initialized. Ready to run.\n")
        self.console_box.configure(state="disabled")

    def _build_main_panel(self):
        self.main_panel = ctk.CTkFrame(self, fg_color="#0D1117", corner_radius=0)
        self.main_panel.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.main_panel.grid_rowconfigure(0, weight=1)
        self.main_panel.grid_columnconfigure(0, weight=1)

        # Embedded Browser Dock Container Frame
        self.browser_frame = ctk.CTkFrame(self.main_panel, fg_color="#161B22", corner_radius=8)
        self.browser_frame.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")

        # Placeholder inside browser container
        self.browser_placeholder = ctk.CTkLabel(
            self.browser_frame, 
            text="🖥️ Chrome Browser View\n\nWhen the script launches, Chrome will be docked & controlled here.\n"
                 "If browser embedding is restricted by Windows, Chrome runs alongside this panel.",
            font=ctk.CTkFont(size=14), text_color="#8B949E"
        )
        self.browser_placeholder.place(relx=0.5, rely=0.5, anchor="center")

    def open_settings_window(self):
        SettingsWindow(self)

    def log_console(self, text):
        self.console_box.configure(state="normal")
        self.console_box.insert("end", f"[{time.strftime('%H:%M:%S')}] {text}\n")
        self.console_box.see("end")
        self.console_box.configure(state="disabled")

    def start_script(self):
        if self.is_running:
            return

        mode = self.mode_var.get()
        script_args = ["--auto"] if mode == "auto" else []
        mode_desc = "Auto Mode (No confirmation, random delays <30s)" if mode == "auto" else "Interactive Mode (Standard)"

        self.log_console(f"Starting script in {mode_desc}...")

        # Update UI state
        self.is_running = True
        self.start_btn.configure(state="disabled")
        self.terminate_btn.configure(state="normal")
        self.status_badge.configure(text="RUNNING", fg_color="#2EA043", text_color="#FFFFFF")

        # Determine python executable & path
        workspace_dir = os.path.dirname(os.path.abspath(__file__))
        venv_python = os.path.join(workspace_dir, ".venv", "Scripts", "python.exe")
        if not os.path.exists(venv_python):
            venv_python = sys.executable

        run_script = os.path.join(workspace_dir, "run.py")

        cmd = [venv_python, run_script] + script_args

        # Launch process in background thread
        threading.Thread(target=self._run_process_thread, args=(cmd,), daemon=True).start()

    def _run_process_thread(self, cmd):
        try:
            creation_flags = (subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP) if sys.platform.startswith('win') else 0
            self.bot_process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                text=True, bufsize=1, creationflags=creation_flags
            )

            for line in iter(self.bot_process.stdout.readline, ''):
                if line:
                    clean_line = line.strip()
                    if clean_line:
                        self.after(0, self.log_console, clean_line)

            self.bot_process.wait()
        except Exception as e:
            self.after(0, self.log_console, f"Process error: {e}")
        finally:
            self.after(0, self._on_process_finished)

    def terminate_script(self):
        if not self.is_running or not self.bot_process:
            return

        self.log_console("Terminating script process...")
        try:
            if sys.platform.startswith('win'):
                subprocess.call(['taskkill', '/F', '/T', '/PID', str(self.bot_process.pid)])
            else:
                self.bot_process.kill()
        except Exception as e:
            self.log_console(f"Error during termination: {e}")

        self._on_process_finished(terminated=True)

    def _on_process_finished(self, terminated=False):
        self.is_running = False
        self.bot_process = None
        self.start_btn.configure(state="normal")
        self.terminate_btn.configure(state="disabled")

        if terminated:
            self.status_badge.configure(text="TERMINATED", fg_color="#DA3633", text_color="#FFFFFF")
            self.log_console("Script terminated by user.")
        else:
            self.status_badge.configure(text="FINISHED", fg_color="#388BFD", text_color="#FFFFFF")
            self.log_console("Script finished execution.")

    def _start_live_log_polling(self):
        def poll():
            csv_path = os.path.join(os.path.dirname(__file__), "all excels", "all_applied_applications_history.csv")
            if os.path.exists(csv_path):
                try:
                    jobs = []
                    with open(csv_path, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            jobs.append({
                                'Job_ID': row.get('Job ID', ''),
                                'Title': row.get('Title', 'Unknown Title'),
                                'Company': row.get('Company', 'Unknown Company'),
                                'Date_Applied': row.get('Date Applied', 'Just now'),
                                'Link': row.get('Job Link', ''),
                                'External': row.get('External Job link', '')
                            })

                    if len(jobs) != len(self.applied_jobs_data):
                        self.applied_jobs_data = jobs
                        self.after(0, self._render_jobs_feed)
                except Exception:
                    pass

            self.after(2000, poll)

        poll()

    def _render_jobs_feed(self):
        # Clear existing feed widgets
        for widget in self.jobs_feed.winfo_children():
            widget.destroy()

        if not self.applied_jobs_data:
            self.empty_label = ctk.CTkLabel(
                self.jobs_feed, text="No applied jobs logged yet.\nClick 'Start Script' to begin.", 
                text_color="#8B949E", font=ctk.CTkFont(size=12)
            )
            self.empty_label.pack(pady=40)
            self.job_count_label.configure(text="0 Jobs")
            return

        self.job_count_label.configure(text=f"{len(self.applied_jobs_data)} Jobs")

        # Render in reverse chronological order (newest first)
        for idx, job in enumerate(reversed(self.applied_jobs_data)):
            card = ctk.CTkFrame(self.jobs_feed, fg_color="#1E2023", corner_radius=6)
            card.pack(fill="x", padx=2, pady=4)

            # Top row: Title & Number
            top_row = ctk.CTkFrame(card, fg_color="transparent")
            top_row.pack(fill="x", padx=8, pady=(6, 2))

            title_lbl = ctk.CTkLabel(top_row, text=f"#{len(self.applied_jobs_data) - idx} {job['Title']}", 
                                     font=ctk.CTkFont(size=12, weight="bold"), anchor="w")
            title_lbl.pack(side="left", fill="x", expand=True)

            # Company & Date row
            details_lbl = ctk.CTkLabel(
                card, text=f"🏢 {job['Company']}  |  📅 {job['Date_Applied']}", 
                font=ctk.CTkFont(size=10), text_color="#8B949E", anchor="w"
            )
            details_lbl.pack(fill="x", padx=8, pady=(0, 6))

    def _start_browser_docking_loop(self):
        if not HAS_WIN32:
            return

        def dock_check():
            if self.is_running:
                try:
                    # Find Chrome window belonging to Selenium/Undetected Chrome
                    def enum_windows_callback(hwnd, extra):
                        if win32gui.IsWindowVisible(hwnd):
                            title = win32gui.GetWindowText(hwnd)
                            if "LinkedIn" in title or "Chrome" in title or "Google Chrome" in title:
                                extra.append((hwnd, title))
                        return True

                    chrome_windows = []
                    win32gui.EnumWindows(enum_windows_callback, chrome_windows)

                    # If found and frame handle exists, set parent to embed
                    if chrome_windows and hasattr(self, 'browser_frame'):
                        container_hwnd = self.browser_frame.winfo_id()
                        for hwnd, title in chrome_windows:
                            parent = win32gui.GetParent(hwnd)
                            if parent != container_hwnd and "Applier" not in title:
                                # Dock window
                                win32gui.SetParent(hwnd, container_hwnd)
                                # Resize chrome to fill frame
                                width = self.browser_frame.winfo_width()
                                height = self.browser_frame.winfo_height()
                                if width > 50 and height > 50:
                                    win32gui.MoveWindow(hwnd, 0, 0, width, height, True)
                                break
                except Exception:
                    pass

            self.after(3000, dock_check)

        dock_check()

    def on_closing(self):
        if self.is_running:
            self.terminate_script()
        self.destroy()

if __name__ == "__main__":
    app = AutoJobApplierApp()
    app.mainloop()
