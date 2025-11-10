"""
Backup Tab - Main backup interface
"""

import os
import sys
import threading
from tkinter import filedialog

import customtkinter as ctk

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.backup import BackupEngine  # noqa: E402


class BackupTab:
    """Backup tab interface"""

    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.backup_engine = None  # Will be created when backup starts

        self.source_dir = None
        self.dest_dir = None

        self._create_widgets()

    def _create_widgets(self):
        """Create all widgets"""
        # Configure grid
        self.parent.grid_columnconfigure(0, weight=1)

        # Source section
        source_label = ctk.CTkLabel(self.parent, text="Source", font=ctk.CTkFont(size=14, weight="bold"))
        source_label.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")

        source_frame = ctk.CTkFrame(self.parent)
        source_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")
        source_frame.grid_columnconfigure(0, weight=1)

        self.source_entry = ctk.CTkEntry(source_frame, placeholder_text="Select source directory...", height=40)
        self.source_entry.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        source_browse_btn = ctk.CTkButton(source_frame, text="Browse", width=100, height=40, command=self._browse_source)
        source_browse_btn.grid(row=0, column=1, padx=10, pady=10)

        # Destination section
        dest_label = ctk.CTkLabel(self.parent, text="Destination", font=ctk.CTkFont(size=14, weight="bold"))
        dest_label.grid(row=2, column=0, padx=20, pady=(0, 5), sticky="w")

        dest_frame = ctk.CTkFrame(self.parent)
        dest_frame.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="ew")
        dest_frame.grid_columnconfigure(0, weight=1)

        self.dest_entry = ctk.CTkEntry(dest_frame, placeholder_text="Select destination directory...", height=40)
        self.dest_entry.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        dest_browse_btn = ctk.CTkButton(dest_frame, text="Browse", width=100, height=40, command=self._browse_destination)
        dest_browse_btn.grid(row=0, column=1, padx=10, pady=10)

        # Options section
        options_label = ctk.CTkLabel(self.parent, text="Options", font=ctk.CTkFont(size=14, weight="bold"))
        options_label.grid(row=4, column=0, padx=20, pady=(0, 5), sticky="w")

        options_frame = ctk.CTkFrame(self.parent)
        options_frame.grid(row=5, column=0, padx=20, pady=(0, 20), sticky="ew")

        # Checkboxes
        self.incremental_var = ctk.BooleanVar(value=True)
        self.incremental_check = ctk.CTkCheckBox(
            options_frame, text="Incremental Backup", variable=self.incremental_var, font=ctk.CTkFont(size=13)
        )
        self.incremental_check.grid(row=0, column=0, padx=15, pady=10, sticky="w")

        self.encrypt_var = ctk.BooleanVar(value=True)
        self.encrypt_check = ctk.CTkCheckBox(
            options_frame, text="Encrypt Backup", variable=self.encrypt_var, font=ctk.CTkFont(size=13)
        )
        self.encrypt_check.grid(row=1, column=0, padx=15, pady=10, sticky="w")

        self.compress_var = ctk.BooleanVar(value=True)
        self.compress_check = ctk.CTkCheckBox(
            options_frame, text="Compress Backup", variable=self.compress_var, font=ctk.CTkFont(size=13)
        )
        self.compress_check.grid(row=2, column=0, padx=15, pady=10, sticky="w")

        self.verify_var = ctk.BooleanVar(value=True)
        self.verify_check = ctk.CTkCheckBox(
            options_frame, text="Verify Integrity", variable=self.verify_var, font=ctk.CTkFont(size=13)
        )
        self.verify_check.grid(row=3, column=0, padx=15, pady=10, sticky="w")

        # Progress section
        progress_label = ctk.CTkLabel(self.parent, text="Progress", font=ctk.CTkFont(size=14, weight="bold"))
        progress_label.grid(row=6, column=0, padx=20, pady=(0, 5), sticky="w")

        progress_frame = ctk.CTkFrame(self.parent, height=150)
        progress_frame.grid(row=7, column=0, padx=20, pady=(0, 20), sticky="ew")
        progress_frame.grid_propagate(False)
        progress_frame.grid_columnconfigure(0, weight=1)

        self.status_label = ctk.CTkLabel(progress_frame, text="Ready to start backup", font=ctk.CTkFont(size=13))
        self.status_label.grid(row=0, column=0, padx=15, pady=(15, 10), sticky="w")

        self.progress_bar = ctk.CTkProgressBar(progress_frame)
        self.progress_bar.grid(row=1, column=0, padx=15, pady=10, sticky="ew")
        self.progress_bar.set(0)

        self.progress_text = ctk.CTkTextbox(progress_frame, height=60, font=ctk.CTkFont(size=11, family="Courier"))
        self.progress_text.grid(row=2, column=0, padx=15, pady=(10, 15), sticky="ew")

        # Buttons
        button_frame = ctk.CTkFrame(self.parent)
        button_frame.grid(row=8, column=0, padx=20, pady=20, sticky="ew")
        button_frame.grid_columnconfigure(0, weight=1)

        self.start_btn = ctk.CTkButton(
            button_frame, text="Start Backup", height=40, font=ctk.CTkFont(size=14, weight="bold"), command=self._start_backup
        )
        self.start_btn.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        self.stop_btn = ctk.CTkButton(
            button_frame,
            text="Stop",
            height=40,
            font=ctk.CTkFont(size=14),
            state="disabled",
            fg_color="gray",
            command=self._stop_backup,
        )
        self.stop_btn.grid(row=0, column=1, padx=(10, 0), sticky="ew")

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

    def _update_progress(self, progress: float, message: str):
        """Update progress bar and message"""
        self.progress_bar.set(progress / 100)
        self.status_label.configure(text=message)
        self.progress_text.insert("end", f"{message}\n")
        self.progress_text.see("end")
        self.main_window.update()

    def _start_backup(self):
        """Start backup process"""
        if not self.source_dir or not self.dest_dir:
            self.main_window.show_error("Error", "Please select source and destination directories")
            return

        # Disable start button
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal", fg_color=["#3B8ED0", "#1F6AA5"])

        # Clear progress
        self.progress_bar.set(0)
        self.progress_text.delete("1.0", "end")

        # Start backup in thread
        thread = threading.Thread(target=self._run_backup)
        thread.daemon = True
        thread.start()

    def _run_backup(self):
        """Run backup in background thread"""
        try:
            from pathlib import Path

            # Create BackupEngine instance
            self.backup_engine = BackupEngine(source=Path(self.source_dir), destination=Path(self.dest_dir))

            self._update_progress(0, "Scanning directory...")

            # Scan directory
            files = self.backup_engine.scan_directory(progress_callback=self._backup_progress_callback)

            self._update_progress(10, f"Found {len(files)} files to backup...")

            # Perform backup
            result = self.backup_engine.backup(progress_callback=self._backup_progress_callback)

            self._update_progress(100, f"✓ Backup completed! {result['backed_up_files']} files backed up")
            self.main_window.update_status("Backup completed")

        except Exception as e:
            import traceback

            self._update_progress(0, f"✗ Error: {str(e)}")
            self.main_window.update_status(f"Backup failed: {str(e)}")
            traceback.print_exc()

        finally:
            # Re-enable buttons
            self.start_btn.configure(state="normal")
            self.stop_btn.configure(state="disabled", fg_color="gray")

    def _backup_progress_callback(self, progress_data: dict):
        """Handle progress callback from BackupEngine"""
        phase = progress_data.get("phase", "")
        current_file = progress_data.get("current_file", "")
        total_files = progress_data.get("total_files", 0)
        processed = progress_data.get("processed_files", 0)

        if phase == "scanning":
            self._update_progress(5, f"Scanning: {current_file}")
        elif phase == "backup":
            if total_files > 0:
                progress = 10 + (processed / total_files) * 90
                self._update_progress(progress, f"Backing up: {current_file}")

    def _stop_backup(self):
        """Stop backup process"""
        # TODO: Implement backup cancellation
        self.main_window.update_status("Stopping backup...")
