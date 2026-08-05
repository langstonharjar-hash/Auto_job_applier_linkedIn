"""
Auto Job Applier LinkedIn - Ultra-Modern Dashboard GUI
Features:
- Premium Dark Obsidian & Slate Aesthetics
- Live KPI Metrics Header Bar (Jobs Count, Current Mode, Status)
- Mode Selector: Interactive Mode (Default) vs Auto Mode (Delays <30s)
- Process Controls: Start Automation & Terminate Process
- Card-Based Live Feed for Successfully Applied Jobs
- Redesigned Settings Modal Window for all automation preferences
- Embedded Chrome Browser View Container via Win32 API
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

# Set Modern Appearance Theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

# Design Tokens
COLOR_BG = "#0B0F19"           # Deep Obsidian Navy
COLOR_PANEL = "#151C2C"        # Dark Slate Panel
COLOR_CARD = "#1E293B"         # Card Background
COLOR_CARD_HOVER = "#2D3B53"   # Card Hover Highlight
COLOR_BORDER = "#2A364F"       # Subtle Border
COLOR_TEXT_MAIN = "#F8FAFC"    # Off-white main text
COLOR_TEXT_MUTED = "#94A3B8"   # Slate muted text

COLOR_PRIMARY = "#6366F1"      # Indigo Accent
COLOR_SUCCESS = "#10B981"      # Emerald Green
COLOR_WARNING = "#F59E0B"      # Amber
COLOR_DANGER = "#EF4444"       # Coral Crimson
COLOR_CYAN = "#06B6D4"         # Electric Cyan


class ModernSettingsWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Automation Preferences & Settings")
        self.geometry("720x760")
        self.resizable(False, False)
        self.configure(fg_color=COLOR_BG)
        self.grab_set()  # Modal window

        self.current_settings = load_all_settings()
        self._build_ui()

    def _build_ui(self):
        # Header Bar
        header = ctk.CTkFrame(self, fg_color=COLOR_PANEL, corner_radius=12, border_width=1, border_color=COLOR_BORDER)
        header.pack(fill="x", padx=20, pady=(20, 10))

        title_label = ctk.CTkLabel(
            header, text="⚙️  Automation Preferences", 
            font=ctk.CTkFont(size=18, weight="bold"), text_color=COLOR_TEXT_MAIN
        )
        title_label.pack(side="left", padx=15, pady=12)

        subtitle_label = ctk.CTkLabel(
            header, text="Configure your search parameters, salary target & bot options", 
            font=ctk.CTkFont(size=11), text_color=COLOR_TEXT_MUTED
        )
        subtitle_label.pack(side="right", padx=15, pady=12)

        # Scrollable Form Body
        form = ctk.CTkScrollableFrame(self, fg_color=COLOR_PANEL, corner_radius=12, border_width=1, border_color=COLOR_BORDER)
        form.pack(fill="both", expand=True, padx=20, pady=10)

        # --- SECTION 1: SEARCH PREFERENCES ---
        sec1_frame = ctk.CTkFrame(form, fg_color="transparent")
        sec1_frame.pack(fill="x", padx=10, pady=(10, 15))

        sec1_lbl = ctk.CTkLabel(
            sec1_frame, text="🔍  JOB SEARCH PARAMETERS", 
            font=ctk.CTkFont(size=12, weight="bold"), text_color=COLOR_CYAN
        )
        sec1_lbl.pack(anchor="w", pady=(0, 8))

        # Search Terms
        ctk.CTkLabel(form, text="Search Keywords / Titles (comma separated):", font=ctk.CTkFont(size=12, weight="bold"), text_color=COLOR_TEXT_MAIN).pack(anchor="w", padx=10, pady=(5, 2))
        self.terms_entry = ctk.CTkEntry(form, placeholder_text="e.g. Data Analyst, Software Engineer", height=38, fg_color=COLOR_CARD, border_color=COLOR_BORDER)
        self.terms_entry.pack(fill="x", padx=10, pady=(0, 12))
        self.terms_entry.insert(0, ", ".join(self.current_settings.get("search_terms", [])))

        # Location & Date Posted Row
        loc_row = ctk.CTkFrame(form, fg_color="transparent")
        loc_row.pack(fill="x", padx=10, pady=(0, 12))

        # Search Location
        loc_col = ctk.CTkFrame(loc_row, fg_color="transparent")
        loc_col.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkLabel(loc_col, text="Search Location:", font=ctk.CTkFont(size=12, weight="bold"), text_color=COLOR_TEXT_MAIN).pack(anchor="w", pady=(0, 2))
        self.location_entry = ctk.CTkEntry(loc_col, placeholder_text="e.g. San Francisco or United States", height=38, fg_color=COLOR_CARD, border_color=COLOR_BORDER)
        self.location_entry.pack(fill="x")
        self.location_entry.insert(0, self.current_settings.get("search_location", ""))

        # Date Posted
        date_col = ctk.CTkFrame(loc_row, fg_color="transparent")
        date_col.pack(side="right", width=220)
        ctk.CTkLabel(date_col, text="Date Posted Filter:", font=ctk.CTkFont(size=12, weight="bold"), text_color=COLOR_TEXT_MAIN).pack(anchor="w", pady=(0, 2))
        self.date_posted_menu = ctk.CTkOptionMenu(
            date_col, values=["Past 24 hours", "Past week", "Past month", "Any time", ""],
            height=38, fg_color=COLOR_CARD, button_color=COLOR_PRIMARY, button_hover_color="#4F46E5"
        )
        self.date_posted_menu.pack(fill="x")
        self.date_posted_menu.set(self.current_settings.get("date_posted", "Past week"))

        # Work Modes & Job Types Row
        filters_row = ctk.CTkFrame(form, fg_color=COLOR_CARD, corner_radius=8, border_width=1, border_color=COLOR_BORDER)
        filters_row.pack(fill="x", padx=10, pady=(0, 15))

        f_inner = ctk.CTkFrame(filters_row, fg_color="transparent")
        f_inner.pack(fill="x", padx=12, pady=10)

        # Work Modes Checkboxes
        ctk.CTkLabel(f_inner, text="Work Location Modes:", font=ctk.CTkFont(size=12, weight="bold"), text_color=COLOR_TEXT_MAIN).pack(anchor="w", pady=(0, 5))
        mode_box = ctk.CTkFrame(f_inner, fg_color="transparent")
        mode_box.pack(anchor="w", pady=(0, 10))

        curr_modes = self.current_settings.get("on_site", [])
        self.mode_remote_var = ctk.BooleanVar(value="Remote" in curr_modes)
        self.mode_hybrid_var = ctk.BooleanVar(value="Hybrid" in curr_modes)
        self.mode_onsite_var = ctk.BooleanVar(value="On-site" in curr_modes)

        ctk.CTkCheckBox(mode_box, text="Remote", variable=self.mode_remote_var, fg_color=COLOR_PRIMARY).pack(side="left", padx=(0, 20))
        ctk.CTkCheckBox(mode_box, text="Hybrid", variable=self.mode_hybrid_var, fg_color=COLOR_PRIMARY).pack(side="left", padx=(0, 20))
        ctk.CTkCheckBox(mode_box, text="On-site", variable=self.mode_onsite_var, fg_color=COLOR_PRIMARY).pack(side="left")

        # Job Types Checkboxes
        ctk.CTkLabel(f_inner, text="Job Types:", font=ctk.CTkFont(size=12, weight="bold"), text_color=COLOR_TEXT_MAIN).pack(anchor="w", pady=(0, 5))
        type_box = ctk.CTkFrame(f_inner, fg_color="transparent")
        type_box.pack(anchor="w")

        curr_types = self.current_settings.get("job_type", [])
        self.type_ft_var = ctk.BooleanVar(value="Full-time" in curr_types)
        self.type_contract_var = ctk.BooleanVar(value="Contract" in curr_types)
        self.type_pt_var = ctk.BooleanVar(value="Part-time" in curr_types)

        ctk.CTkCheckBox(type_box, text="Full-time", variable=self.type_ft_var, fg_color=COLOR_PRIMARY).pack(side="left", padx=(0, 20))
        ctk.CTkCheckBox(type_box, text="Contract", variable=self.type_contract_var, fg_color=COLOR_PRIMARY).pack(side="left", padx=(0, 20))
        ctk.CTkCheckBox(type_box, text="Part-time", variable=self.type_pt_var, fg_color=COLOR_PRIMARY).pack(side="left")

        # --- SECTION 2: PERSONAL & SALARY ---
        ctk.CTkFrame(form, height=1, fg_color=COLOR_BORDER).pack(fill="x", padx=10, pady=10)

        sec2_lbl = ctk.CTkLabel(
            form, text="👤  PERSONAL & SALARY TARGETS", 
            font=ctk.CTkFont(size=12, weight="bold"), text_color=COLOR_SUCCESS
        )
        sec2_lbl.pack(anchor="w", padx=10, pady=(5, 10))

        sal_row = ctk.CTkFrame(form, fg_color="transparent")
        sal_row.pack(fill="x", padx=10, pady=(0, 15))

        # Desired Salary
        c1 = ctk.CTkFrame(sal_row, fg_color="transparent")
        c1.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkLabel(c1, text="Target Desired Salary ($):", font=ctk.CTkFont(size=12, weight="bold"), text_color=COLOR_TEXT_MAIN).pack(anchor="w", pady=(0, 2))
        self.salary_entry = ctk.CTkEntry(c1, height=38, fg_color=COLOR_CARD, border_color=COLOR_BORDER)
        self.salary_entry.pack(fill="x")
        self.salary_entry.insert(0, str(self.current_settings.get("desired_salary", 120000)))

        # Experience
        c2 = ctk.CTkFrame(sal_row, fg_color="transparent")
        c2.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkLabel(c2, text="Experience (years):", font=ctk.CTkFont(size=12, weight="bold"), text_color=COLOR_TEXT_MAIN).pack(anchor="w", pady=(0, 2))
        self.exp_entry = ctk.CTkEntry(c2, height=38, fg_color=COLOR_CARD, border_color=COLOR_BORDER)
        self.exp_entry.pack(fill="x")
        self.exp_entry.insert(0, str(self.current_settings.get("current_experience", 7)))

        # Notice Period
        c3 = ctk.CTkFrame(sal_row, fg_color="transparent")
        c3.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(c3, text="Notice Period (days):", font=ctk.CTkFont(size=12, weight="bold"), text_color=COLOR_TEXT_MAIN).pack(anchor="w", pady=(0, 2))
        self.notice_entry = ctk.CTkEntry(c3, height=38, fg_color=COLOR_CARD, border_color=COLOR_BORDER)
        self.notice_entry.pack(fill="x")
        self.notice_entry.insert(0, str(self.current_settings.get("notice_period", 14)))

        # --- SECTION 3: BOT OPTIONS ---
        ctk.CTkFrame(form, height=1, fg_color=COLOR_BORDER).pack(fill="x", padx=10, pady=10)

        sec3_lbl = ctk.CTkLabel(
            form, text="⚡  BOT CONTROLS & DELAYS", 
            font=ctk.CTkFont(size=12, weight="bold"), text_color=COLOR_WARNING
        )
        sec3_lbl.pack(anchor="w", padx=10, pady=(5, 10))

        bot_row = ctk.CTkFrame(form, fg_color="transparent")
        bot_row.pack(fill="x", padx=10, pady=(0, 15))

        bc1 = ctk.CTkFrame(bot_row, fg_color="transparent")
        bc1.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkLabel(bc1, text="Action Delay Gap (seconds):", font=ctk.CTkFont(size=12, weight="bold"), text_color=COLOR_TEXT_MAIN).pack(anchor="w", pady=(0, 2))
        self.gap_entry = ctk.CTkEntry(bc1, height=38, fg_color=COLOR_CARD, border_color=COLOR_BORDER)
        self.gap_entry.pack(fill="x")
        self.gap_entry.insert(0, str(self.current_settings.get("click_gap", 1)))

        bc2 = ctk.CTkFrame(bot_row, fg_color="transparent")
        bc2.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(bc2, text="Chrome Profile:", font=ctk.CTkFont(size=12, weight="bold"), text_color=COLOR_TEXT_MAIN).pack(anchor="w", pady=(0, 2))
        self.profile_entry = ctk.CTkEntry(bc2, height=38, fg_color=COLOR_CARD, border_color=COLOR_BORDER)
        self.profile_entry.pack(fill="x")
        self.profile_entry.insert(0, str(self.current_settings.get("chrome_profile", "Default")))

        # Footer Action Buttons
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(fill="x", padx=20, pady=(5, 20))

        self.save_btn = ctk.CTkButton(
            footer, text="💾  Save & Apply Settings", font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLOR_SUCCESS, hover_color="#059669", height=42, width=180, command=self.save_settings
        )
        self.save_btn.pack(side="right", padx=(10, 0))

        self.cancel_btn = ctk.CTkButton(
            footer, text="Cancel", font=ctk.CTkFont(size=14),
            fg_color="#334155", hover_color="#475569", height=42, width=100, command=self.destroy
        )
        self.cancel_btn.pack(side="right")

    def save_settings(self):
        try:
            raw_terms = self.terms_entry.get().strip()
            terms_list = [t.strip() for t in raw_terms.split(",") if t.strip()]

            modes = []
            if self.mode_remote_var.get(): modes.append("Remote")
            if self.mode_hybrid_var.get(): modes.append("Hybrid")
            if self.mode_onsite_var.get(): modes.append("On-site")

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
                self.parent.log_console("Settings saved cleanly to config files!")
                self.destroy()
            else:
                self.parent.log_console("Notice: Some settings files could not be written.")
        except Exception as e:
            self.parent.log_console(f"Error saving settings: {e}")


class AutoJobApplierApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Auto Job Applier LinkedIn - Pro Dashboard")
        self.geometry("1450x880")
        self.minsize(1150, 720)
        self.configure(fg_color=COLOR_BG)

        self.bot_process = None
        self.is_running = False
        self.applied_jobs_data = []

        # Configure root layout grid
        self.grid_columnconfigure(0, weight=0)  # Left Sidebar
        self.grid_columnconfigure(1, weight=1)  # Main Workspace (Browser View)
        self.grid_rowconfigure(0, weight=0)     # Header Bar
        self.grid_rowconfigure(1, weight=1)     # Content Area

        # Build UI Components
        self._build_header_bar()
        self._build_sidebar()
        self._build_main_panel()

        # Start Polling Loops
        self._start_live_log_polling()
        self._start_browser_docking_loop()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _build_header_bar(self):
        self.header_bar = ctk.CTkFrame(self, fg_color=COLOR_PANEL, height=64, corner_radius=0, border_width=1, border_color=COLOR_BORDER)
        self.header_bar.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.header_bar.grid_columnconfigure(1, weight=1)

        # Branding Logo & Name
        logo_frame = ctk.CTkFrame(self.header_bar, fg_color="transparent")
        logo_frame.pack(side="left", padx=20, pady=10)

        badge_icon = ctk.CTkLabel(
            logo_frame, text="⚡", font=ctk.CTkFont(size=20),
            fg_color=COLOR_PRIMARY, text_color="#FFFFFF", corner_radius=8, width=34, height=34
        )
        badge_icon.pack(side="left", padx=(0, 10))

        title_text = ctk.CTkLabel(
            logo_frame, text="Auto Job Applier Pro", 
            font=ctk.CTkFont(size=18, weight="bold"), text_color=COLOR_TEXT_MAIN
        )
        title_text.pack(side="left")

        # KPI Metrics Cards (Right Side of Header)
        kpi_frame = ctk.CTkFrame(self.header_bar, fg_color="transparent")
        kpi_frame.pack(side="right", padx=20, pady=10)

        # Metric 1: Applied Jobs Counter
        self.kpi_jobs_card = ctk.CTkFrame(kpi_frame, fg_color=COLOR_CARD, corner_radius=8, border_width=1, border_color=COLOR_BORDER)
        self.kpi_jobs_card.pack(side="left", padx=6)

        self.kpi_jobs_lbl = ctk.CTkLabel(
            self.kpi_jobs_card, text="Applied: 0 Jobs", 
            font=ctk.CTkFont(size=12, weight="bold"), text_color=COLOR_SUCCESS, padx=12, pady=6
        )
        self.kpi_jobs_lbl.pack()

        # Metric 2: Active Mode Pill
        self.kpi_mode_card = ctk.CTkFrame(kpi_frame, fg_color=COLOR_CARD, corner_radius=8, border_width=1, border_color=COLOR_BORDER)
        self.kpi_mode_card.pack(side="left", padx=6)

        self.kpi_mode_lbl = ctk.CTkLabel(
            self.kpi_mode_card, text="Mode: Interactive", 
            font=ctk.CTkFont(size=12, weight="bold"), text_color=COLOR_CYAN, padx=12, pady=6
        )
        self.kpi_mode_lbl.pack()

        # Metric 3: Live Status Badge
        self.status_badge = ctk.CTkLabel(
            kpi_frame, text="● IDLE", font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#334155", text_color="#CBD5E1", corner_radius=8, padx=14, pady=6
        )
        self.status_badge.pack(side="left", padx=6)

        # Settings Trigger Button
        self.settings_btn = ctk.CTkButton(
            kpi_frame, text="⚙️ Settings", font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=COLOR_CARD, hover_color=COLOR_CARD_HOVER, border_width=1, border_color=COLOR_BORDER,
            width=90, height=32, corner_radius=8, command=self.open_settings_window
        )
        self.settings_btn.pack(side="left", padx=(10, 0))

    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=440, fg_color=COLOR_PANEL, corner_radius=0)
        self.sidebar.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        self.sidebar.grid_rowconfigure(3, weight=1)  # Applied jobs feed expands

        # Section 1: Mode Selector Frame
        mode_card = ctk.CTkFrame(self.sidebar, fg_color=COLOR_CARD, corner_radius=10, border_width=1, border_color=COLOR_BORDER)
        mode_card.grid(row=0, column=0, padx=16, pady=(16, 10), sticky="ew")

        mode_header = ctk.CTkLabel(
            mode_card, text="EXECUTION MODE", 
            font=ctk.CTkFont(size=11, weight="bold"), text_color=COLOR_TEXT_MUTED
        )
        mode_header.pack(anchor="w", padx=14, pady=(12, 6))

        self.mode_var = ctk.StringVar(value="interactive")

        self.radio_interactive = ctk.CTkRadioButton(
            mode_card, text="🔵 Interactive Mode (Standard / Default)", 
            variable=self.mode_var, value="interactive", font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=COLOR_PRIMARY, command=self._on_mode_change
        )
        self.radio_interactive.pack(anchor="w", padx=14, pady=6)

        self.radio_auto = ctk.CTkRadioButton(
            mode_card, text="⚡ Auto Mode (No prompts, delays <30s)", 
            variable=self.mode_var, value="auto", font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=COLOR_CYAN, command=self._on_mode_change
        )
        self.radio_auto.pack(anchor="w", padx=14, pady=(6, 12))

        # Section 2: Controls Panel (Start / Terminate)
        ctrl_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        ctrl_frame.grid(row=1, column=0, padx=16, pady=6, sticky="ew")

        self.start_btn = ctk.CTkButton(
            ctrl_frame, text="▶  Start Automation", font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLOR_SUCCESS, hover_color="#059669", height=42, corner_radius=10, command=self.start_script
        )
        self.start_btn.pack(side="left", expand=True, fill="x", padx=(0, 6))

        self.terminate_btn = ctk.CTkButton(
            ctrl_frame, text="🛑  Terminate", font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#EF4444", text_color="#FFFFFF", hover_color="#DC2626",
            text_color_disabled="#E2E8F0",
            height=42, corner_radius=10, command=self.terminate_script, state="disabled"
        )
        self.terminate_btn.pack(side="right", expand=True, fill="x", padx=(6, 0))

        # Section 3: Live Applied Jobs Header
        feed_hdr_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        feed_hdr_frame.grid(row=2, column=0, padx=16, pady=(16, 6), sticky="ew")

        feed_title = ctk.CTkLabel(
            feed_hdr_frame, text="APPLIED JOBS FEED", 
            font=ctk.CTkFont(size=11, weight="bold"), text_color=COLOR_TEXT_MUTED
        )
        feed_title.pack(side="left")

        # Section 4: Scrollable Applied Jobs Feed List
        self.jobs_feed = ctk.CTkScrollableFrame(self.sidebar, fg_color=COLOR_BG, corner_radius=10, border_width=1, border_color=COLOR_BORDER)
        self.jobs_feed.grid(row=3, column=0, padx=16, pady=6, sticky="nsew")

        self.empty_label = ctk.CTkLabel(
            self.jobs_feed, text="No job applications logged yet.\nClick 'Start Automation' to begin.", 
            text_color=COLOR_TEXT_MUTED, font=ctk.CTkFont(size=12)
        )
        self.empty_label.pack(pady=50)

        # Section 5: Developer Console Output Textbox
        self.console_box = ctk.CTkTextbox(
            self.sidebar, height=130, font=ctk.CTkFont(family="Consolas", size=10),
            fg_color=COLOR_BG, border_width=1, border_color=COLOR_BORDER, corner_radius=8
        )
        self.console_box.grid(row=4, column=0, padx=16, pady=(6, 16), sticky="ew")
        self.console_box.insert("1.0", "[SYSTEM] Pro Dashboard initialized. Ready to launch.\n")
        self.console_box.configure(state="disabled")

    def _build_main_panel(self):
        self.main_panel = ctk.CTkFrame(self, fg_color=COLOR_BG, corner_radius=0)
        self.main_panel.grid(row=1, column=1, sticky="nsew", padx=0, pady=0)
        self.main_panel.grid_rowconfigure(0, weight=1)
        self.main_panel.grid_columnconfigure(0, weight=1)

        # Embedded Browser Dock Container Frame
        self.browser_frame = ctk.CTkFrame(self.main_panel, fg_color=COLOR_PANEL, corner_radius=12, border_width=1, border_color=COLOR_BORDER)
        self.browser_frame.grid(row=0, column=0, padx=16, pady=16, sticky="nsew")

        # Placeholder inside browser container
        self.browser_placeholder = ctk.CTkLabel(
            self.browser_frame, 
            text="🖥️  Chrome Browser Container\n\n"
                 "When automation starts, Chrome will automatically open and dock into this viewport.\n"
                 "If window reparenting is restricted by OS, Chrome runs side-by-side cleanly.",
            font=ctk.CTkFont(size=14), text_color=COLOR_TEXT_MUTED
        )
        self.browser_placeholder.place(relx=0.5, rely=0.5, anchor="center")

    def _on_mode_change(self):
        mode = self.mode_var.get()
        if mode == "auto":
            self.kpi_mode_lbl.configure(text="Mode: Auto Mode ⚡", text_color=COLOR_CYAN)
        else:
            self.kpi_mode_lbl.configure(text="Mode: Interactive 🔵", text_color=COLOR_PRIMARY)

    def open_settings_window(self):
        ModernSettingsWindow(self)

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
        mode_desc = "Auto Mode (Delays <30s)" if mode == "auto" else "Interactive Mode (Default)"

        self.log_console(f"Launching bot in {mode_desc}...")

        # Update UI state
        self.is_running = True
        self.start_btn.configure(state="disabled")
        self.terminate_btn.configure(state="normal")
        self.status_badge.configure(text="● RUNNING", fg_color=COLOR_SUCCESS, text_color="#FFFFFF")

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

        self.log_console("Terminating process...")
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
            self.status_badge.configure(text="● TERMINATED", fg_color=COLOR_DANGER, text_color="#FFFFFF")
            self.log_console("Process terminated by user.")
        else:
            self.status_badge.configure(text="● FINISHED", fg_color=COLOR_PRIMARY, text_color="#FFFFFF")
            self.log_console("Automation completed successfully.")

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
                                'Link': row.get('Job Link', '')
                            })

                    if len(jobs) != len(self.applied_jobs_data):
                        self.applied_jobs_data = jobs
                        self.after(0, self._render_jobs_feed)
                except Exception:
                    pass

            self.after(2000, poll)

        poll()

    def _render_jobs_feed(self):
        for widget in self.jobs_feed.winfo_children():
            widget.destroy()

        if not self.applied_jobs_data:
            self.empty_label = ctk.CTkLabel(
                self.jobs_feed, text="No job applications logged yet.\nClick 'Start Automation' to begin.", 
                text_color=COLOR_TEXT_MUTED, font=ctk.CTkFont(size=12)
            )
            self.empty_label.pack(pady=50)
            self.kpi_jobs_lbl.configure(text="Applied: 0 Jobs")
            return

        self.kpi_jobs_lbl.configure(text=f"Applied: {len(self.applied_jobs_data)} Jobs")

        # Render cards in reverse chronological order
        for idx, job in enumerate(reversed(self.applied_jobs_data)):
            card = ctk.CTkFrame(self.jobs_feed, fg_color=COLOR_CARD, corner_radius=8, border_width=1, border_color=COLOR_BORDER)
            card.pack(fill="x", padx=4, pady=5)

            # Header Row (Title & Index Badge)
            top_row = ctk.CTkFrame(card, fg_color="transparent")
            top_row.pack(fill="x", padx=10, pady=(8, 2))

            idx_lbl = ctk.CTkLabel(
                top_row, text=f"#{len(self.applied_jobs_data) - idx}", 
                font=ctk.CTkFont(size=11, weight="bold"), fg_color=COLOR_PRIMARY, text_color="#FFFFFF", corner_radius=4, width=28
            )
            idx_lbl.pack(side="left", padx=(0, 8))

            title_lbl = ctk.CTkLabel(
                top_row, text=job['Title'], 
                font=ctk.CTkFont(size=12, weight="bold"), text_color=COLOR_TEXT_MAIN, anchor="w"
            )
            title_lbl.pack(side="left", fill="x", expand=True)

            # Details Row (Company & Timestamp)
            details_lbl = ctk.CTkLabel(
                card, text=f"🏢  {job['Company']}  |  📅  {job['Date_Applied']}", 
                font=ctk.CTkFont(size=11), text_color=COLOR_TEXT_MUTED, anchor="w"
            )
            details_lbl.pack(fill="x", padx=10, pady=(0, 8))

    def _start_browser_docking_loop(self):
        if not HAS_WIN32:
            return

        def dock_check():
            if self.is_running:
                try:
                    def enum_windows_callback(hwnd, extra):
                        if win32gui.IsWindowVisible(hwnd):
                            title = win32gui.GetWindowText(hwnd)
                            if "LinkedIn" in title or "Chrome" in title or "Google Chrome" in title:
                                extra.append((hwnd, title))
                        return True

                    chrome_windows = []
                    win32gui.EnumWindows(enum_windows_callback, chrome_windows)

                    if chrome_windows and hasattr(self, 'browser_frame'):
                        container_hwnd = self.browser_frame.winfo_id()
                        for hwnd, title in chrome_windows:
                            parent = win32gui.GetParent(hwnd)
                            if parent != container_hwnd and "Applier" not in title:
                                win32gui.SetParent(hwnd, container_hwnd)
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
