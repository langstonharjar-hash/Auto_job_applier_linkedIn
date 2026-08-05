"""
Auto Job Applier LinkedIn - Desktop GUI Application
Features:
- Version Selection: Interactive Mode vs Auto Mode (No confirmation, random delays <30s)
- Process Controls: Start Script and Terminate Script
- Sidebar: Real-time Live Log of Successfully Applied Jobs
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
        title_label.pack(side="left", padx=5)

        self.status_badge = ctk.CTkLabel(header_frame, text="IDLE", font=ctk.CTkFont(size=11, weight="bold"),
                                         fg_color="#3A3D40", text_color="#AAAAAA", corner_radius=6, padx=8, pady=2)
        self.status_badge.pack(side="right", padx=5)

        # Divider
        divider1 = ctk.CTkFrame(self.sidebar, height=2, fg_color="#2A2D32")
        divider1.grid(row=1, column=0, padx=15, pady=5, sticky="ew")

        # Script Version Selector Section
        mode_frame = ctk.CTkFrame(self.sidebar, fg_color="#1E2023", corner_radius=8)
        mode_frame.grid(row=2, column=0, padx=15, pady=8, sticky="ew")

        mode_title = ctk.CTkLabel(mode_frame, text="Select Script Mode:", font=ctk.CTkFont(size=13, weight="bold"))
        mode_title.pack(anchor="w", padx=12, pady=(10, 5))

        self.mode_var = ctk.StringVar(value="auto")

        self.radio_auto = ctk.CTkRadioButton(
            mode_frame, text="⚡ Auto Mode (No prompt, delays <30s)", 
            variable=self.mode_var, value="auto", font=ctk.CTkFont(size=12)
        )
        self.radio_auto.pack(anchor="w", padx=15, pady=5)

        self.radio_interactive = ctk.CTkRadioButton(
            mode_frame, text="🔵 Interactive Mode (Standard / As Is)", 
            variable=self.mode_var, value="interactive", font=ctk.CTkFont(size=12)
        )
        self.radio_interactive.pack(anchor="w", padx=15, pady=(5, 10))

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
            self.bot_process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                text=True, bufsize=1, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform.startswith('win') else 0
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
