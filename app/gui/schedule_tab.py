"""
Schedule Tab - Backup scheduling interface
"""

import customtkinter as ctk
from tkinter import filedialog
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app.scheduler.scheduler import BackupScheduler
    SCHEDULER_AVAILABLE = True
except Exception:
    SCHEDULER_AVAILABLE = False


class ScheduleTab:
    """Schedule tab interface"""

    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window

        if SCHEDULER_AVAILABLE:
            self.scheduler = BackupScheduler()
        else:
            self.scheduler = None

        self.source_dir = None
        self.dest_dir = None

        self._create_widgets()
        if SCHEDULER_AVAILABLE:
            self._load_schedules()

    def _create_widgets(self):
        """Create all widgets"""
        # Configure grid
        self.parent.grid_columnconfigure(0, weight=1)
        self.parent.grid_rowconfigure(2, weight=1)

        # Header
        header_label = ctk.CTkLabel(
            self.parent,
            text="Create Backup Schedule",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        header_label.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")

        # Schedule form
        form_frame = ctk.CTkFrame(self.parent)
        form_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")
        form_frame.grid_columnconfigure(1, weight=1)

        # Source directory
        ctk.CTkLabel(
            form_frame,
            text="Source:",
            font=ctk.CTkFont(size=13)
        ).grid(row=0, column=0, padx=15, pady=15, sticky="w")

        source_frame = ctk.CTkFrame(form_frame)
        source_frame.grid(row=0, column=1, padx=15, pady=15, sticky="ew")
        source_frame.grid_columnconfigure(0, weight=1)

        self.source_entry = ctk.CTkEntry(
            source_frame,
            placeholder_text="Select source directory..."
        )
        self.source_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        ctk.CTkButton(
            source_frame,
            text="Browse",
            width=80,
            command=self._browse_source
        ).grid(row=0, column=1)

        # Destination directory
        ctk.CTkLabel(
            form_frame,
            text="Destination:",
            font=ctk.CTkFont(size=13)
        ).grid(row=1, column=0, padx=15, pady=15, sticky="w")

        dest_frame = ctk.CTkFrame(form_frame)
        dest_frame.grid(row=1, column=1, padx=15, pady=15, sticky="ew")
        dest_frame.grid_columnconfigure(0, weight=1)

        self.dest_entry = ctk.CTkEntry(
            dest_frame,
            placeholder_text="Select destination directory..."
        )
        self.dest_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        ctk.CTkButton(
            dest_frame,
            text="Browse",
            width=80,
            command=self._browse_destination
        ).grid(row=0, column=1)

        # Schedule name
        ctk.CTkLabel(
            form_frame,
            text="Schedule Name:",
            font=ctk.CTkFont(size=13)
        ).grid(row=2, column=0, padx=15, pady=15, sticky="w")

        self.name_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="e.g., Daily Documents Backup"
        )
        self.name_entry.grid(row=2, column=1, padx=15, pady=15, sticky="ew")

        # Frequency
        ctk.CTkLabel(
            form_frame,
            text="Frequency:",
            font=ctk.CTkFont(size=13)
        ).grid(row=3, column=0, padx=15, pady=15, sticky="w")

        self.frequency_var = ctk.StringVar(value="daily")
        frequency_frame = ctk.CTkFrame(form_frame)
        frequency_frame.grid(row=3, column=1, padx=15, pady=15, sticky="w")

        frequencies = [
            ("Hourly", "hourly"),
            ("Daily", "daily"),
            ("Weekly", "weekly"),
            ("Monthly", "monthly")
        ]

        for idx, (text, value) in enumerate(frequencies):
            radio = ctk.CTkRadioButton(
                frequency_frame,
                text=text,
                variable=self.frequency_var,
                value=value,
                font=ctk.CTkFont(size=13)
            )
            radio.grid(row=0, column=idx, padx=10, pady=5)

        # Time selection (for daily/weekly/monthly)
        ctk.CTkLabel(
            form_frame,
            text="Time:",
            font=ctk.CTkFont(size=13)
        ).grid(row=4, column=0, padx=15, pady=15, sticky="w")

        time_frame = ctk.CTkFrame(form_frame)
        time_frame.grid(row=4, column=1, padx=15, pady=15, sticky="w")

        self.hour_var = ctk.StringVar(value="00")
        hour_menu = ctk.CTkOptionMenu(
            time_frame,
            variable=self.hour_var,
            values=[f"{i:02d}" for i in range(24)],
            width=80
        )
        hour_menu.grid(row=0, column=0, padx=5)

        ctk.CTkLabel(time_frame, text=":", font=ctk.CTkFont(size=13)).grid(row=0, column=1)

        self.minute_var = ctk.StringVar(value="00")
        minute_menu = ctk.CTkOptionMenu(
            time_frame,
            variable=self.minute_var,
            values=[f"{i:02d}" for i in range(0, 60, 15)],
            width=80
        )
        minute_menu.grid(row=0, column=2, padx=5)

        # Day of week (for weekly)
        ctk.CTkLabel(
            form_frame,
            text="Day of Week:",
            font=ctk.CTkFont(size=13)
        ).grid(row=5, column=0, padx=15, pady=15, sticky="w")

        self.day_var = ctk.StringVar(value="monday")
        day_menu = ctk.CTkOptionMenu(
            form_frame,
            variable=self.day_var,
            values=["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"],
            width=150
        )
        day_menu.grid(row=5, column=1, padx=15, pady=15, sticky="w")

        # Options
        ctk.CTkLabel(
            form_frame,
            text="Options:",
            font=ctk.CTkFont(size=13)
        ).grid(row=6, column=0, padx=15, pady=15, sticky="nw")

        options_frame = ctk.CTkFrame(form_frame)
        options_frame.grid(row=6, column=1, padx=15, pady=15, sticky="w")

        self.incremental_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            options_frame,
            text="Incremental Backup",
            variable=self.incremental_var,
            font=ctk.CTkFont(size=12)
        ).grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.encrypt_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            options_frame,
            text="Encryption",
            variable=self.encrypt_var,
            font=ctk.CTkFont(size=12)
        ).grid(row=0, column=1, padx=5, pady=5, sticky="w")

        self.compress_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            options_frame,
            text="Compression",
            variable=self.compress_var,
            font=ctk.CTkFont(size=12)
        ).grid(row=1, column=0, padx=5, pady=5, sticky="w")

        self.verify_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            options_frame,
            text="Verification",
            variable=self.verify_var,
            font=ctk.CTkFont(size=12)
        ).grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # Create schedule button
        create_btn = ctk.CTkButton(
            form_frame,
            text="Create Schedule",
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._create_schedule
        )
        create_btn.grid(row=7, column=0, columnspan=2, padx=15, pady=20, sticky="ew")

        # Active schedules section
        schedules_label = ctk.CTkLabel(
            self.parent,
            text="Active Schedules",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        schedules_label.grid(row=2, column=0, padx=20, pady=(0, 5), sticky="w")

        # Schedules list
        self.schedules_frame = ctk.CTkScrollableFrame(self.parent, height=200)
        self.schedules_frame.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.schedules_frame.grid_columnconfigure(0, weight=1)

    def _browse_source(self):
        """Browse for source directory"""
        directory = filedialog.askdirectory(title="Select Source Directory")
        if directory:
            self.source_dir = directory
            self.source_entry.delete(0, "end")
            self.source_entry.insert(0, directory)

    def _browse_destination(self):
        """Browse for destination directory"""
        directory = filedialog.askdirectory(title="Select Destination Directory")
        if directory:
            self.dest_dir = directory
            self.dest_entry.delete(0, "end")
            self.dest_entry.insert(0, directory)

    def _create_schedule(self):
        """Create a new backup schedule"""
        if not SCHEDULER_AVAILABLE:
            self.main_window.show_error(
                "Scheduler Not Available",
                "APScheduler is not installed. Install it with:\npip install apscheduler"
            )
            return

        if not self.source_dir or not self.dest_dir:
            self.main_window.show_error(
                "Error",
                "Please select source and destination directories"
            )
            return

        name = self.name_entry.get().strip()
        if not name:
            self.main_window.show_error(
                "Error",
                "Please enter a schedule name"
            )
            return

        frequency = self.frequency_var.get()
        time = f"{self.hour_var.get()}:{self.minute_var.get()}"

        try:
            # Create schedule based on frequency
            if frequency == "hourly":
                self.scheduler.schedule_hourly_backup(
                    name=name,
                    source=self.source_dir,
                    destination=self.dest_dir,
                    minute=int(self.minute_var.get())
                )
            elif frequency == "daily":
                self.scheduler.schedule_daily_backup(
                    name=name,
                    source=self.source_dir,
                    destination=self.dest_dir,
                    time=time
                )
            elif frequency == "weekly":
                self.scheduler.schedule_weekly_backup(
                    name=name,
                    source=self.source_dir,
                    destination=self.dest_dir,
                    day=self.day_var.get(),
                    time=time
                )
            elif frequency == "monthly":
                self.scheduler.schedule_monthly_backup(
                    name=name,
                    source=self.source_dir,
                    destination=self.dest_dir,
                    day=1,
                    time=time
                )

            self.main_window.update_status(f"Schedule '{name}' created successfully")
            self._load_schedules()

            # Clear form
            self.name_entry.delete(0, "end")

        except Exception as e:
            self.main_window.show_error("Error", f"Failed to create schedule: {str(e)}")

    def _load_schedules(self):
        """Load and display active schedules"""
        if not SCHEDULER_AVAILABLE:
            return

        # Clear existing
        for widget in self.schedules_frame.winfo_children():
            widget.destroy()

        jobs = self.scheduler.list_jobs()

        if not jobs:
            no_schedules = ctk.CTkLabel(
                self.schedules_frame,
                text="No active schedules",
                font=ctk.CTkFont(size=13),
                text_color="gray"
            )
            no_schedules.grid(row=0, column=0, pady=50)
            return

        # Display schedules
        for idx, job in enumerate(jobs):
            self._create_schedule_card(job, idx)

    def _create_schedule_card(self, job, idx):
        """Create schedule card"""
        card = ctk.CTkFrame(self.schedules_frame)
        card.grid(row=idx, column=0, padx=5, pady=5, sticky="ew")
        card.grid_columnconfigure(1, weight=1)

        # Status indicator
        status_frame = ctk.CTkFrame(card, width=5, fg_color="green")
        status_frame.grid(row=0, column=0, rowspan=3, sticky="ns")

        # Job info
        name_label = ctk.CTkLabel(
            card,
            text=job.get('name', job['id']),
            font=ctk.CTkFont(size=13, weight="bold")
        )
        name_label.grid(row=0, column=1, padx=15, pady=(15, 5), sticky="w")

        next_run = job.get('next_run_time', 'N/A')
        if next_run != 'N/A':
            next_run = str(next_run).split('.')[0]  # Remove microseconds

        schedule_label = ctk.CTkLabel(
            card,
            text=f"Next run: {next_run}",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        schedule_label.grid(row=1, column=1, padx=15, pady=2, sticky="w")

        trigger_label = ctk.CTkLabel(
            card,
            text=f"Trigger: {job.get('trigger', 'N/A')}",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        trigger_label.grid(row=2, column=1, padx=15, pady=(2, 15), sticky="w")

        # Control buttons
        button_frame = ctk.CTkFrame(card)
        button_frame.grid(row=0, column=2, rowspan=3, padx=15, pady=15)

        pause_btn = ctk.CTkButton(
            button_frame,
            text="Pause",
            width=80,
            height=30,
            command=lambda j=job: self._pause_schedule(j['id'])
        )
        pause_btn.pack(side="left", padx=2)

        delete_btn = ctk.CTkButton(
            button_frame,
            text="Delete",
            width=80,
            height=30,
            fg_color="red",
            hover_color="darkred",
            command=lambda j=job: self._delete_schedule(j['id'])
        )
        delete_btn.pack(side="left", padx=2)

    def _pause_schedule(self, job_id: str):
        """Pause a schedule"""
        if not SCHEDULER_AVAILABLE:
            return

        try:
            self.scheduler.pause_job(job_id)
            self.main_window.update_status(f"Schedule paused: {job_id}")
            self._load_schedules()
        except Exception as e:
            self.main_window.show_error("Error", f"Failed to pause schedule: {str(e)}")

    def _delete_schedule(self, job_id: str):
        """Delete a schedule"""
        if not SCHEDULER_AVAILABLE:
            return

        try:
            self.scheduler.remove_job(job_id)
            self.main_window.update_status(f"Schedule deleted: {job_id}")
            self._load_schedules()
        except Exception as e:
            self.main_window.show_error("Error", f"Failed to delete schedule: {str(e)}")
