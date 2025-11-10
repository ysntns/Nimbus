"""
Restore Tab - Restore backups interface
"""

import customtkinter as ctk
from tkinter import filedialog
import threading
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.backup import BackupEngine


class RestoreTab:
    """Restore tab interface"""

    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.backup_engine = BackupEngine()
        self.selected_backup = None
        self.restore_path = None

        self._create_widgets()
        self._load_backups()

    def _create_widgets(self):
        """Create all widgets"""
        # Configure grid
        self.parent.grid_columnconfigure(0, weight=1)
        self.parent.grid_rowconfigure(1, weight=1)

        # Header
        header_label = ctk.CTkLabel(
            self.parent,
            text="Select Backup to Restore",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        header_label.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")

        # Backup list frame
        list_frame = ctk.CTkFrame(self.parent)
        list_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(0, weight=1)

        # Scrollable frame for backups
        self.backups_frame = ctk.CTkScrollableFrame(list_frame, height=250)
        self.backups_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.backups_frame.grid_columnconfigure(0, weight=1)

        # Restore destination section
        dest_label = ctk.CTkLabel(
            self.parent,
            text="Restore Destination",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        dest_label.grid(row=2, column=0, padx=20, pady=(0, 5), sticky="w")

        dest_frame = ctk.CTkFrame(self.parent)
        dest_frame.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="ew")
        dest_frame.grid_columnconfigure(0, weight=1)

        self.restore_entry = ctk.CTkEntry(
            dest_frame,
            placeholder_text="Select restore destination...",
            height=40
        )
        self.restore_entry.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        restore_browse_btn = ctk.CTkButton(
            dest_frame,
            text="Browse",
            width=100,
            height=40,
            command=self._browse_restore_destination
        )
        restore_browse_btn.grid(row=0, column=1, padx=10, pady=10)

        # Progress section
        progress_label = ctk.CTkLabel(
            self.parent,
            text="Progress",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        progress_label.grid(row=4, column=0, padx=20, pady=(0, 5), sticky="w")

        progress_frame = ctk.CTkFrame(self.parent, height=120)
        progress_frame.grid(row=5, column=0, padx=20, pady=(0, 20), sticky="ew")
        progress_frame.grid_propagate(False)
        progress_frame.grid_columnconfigure(0, weight=1)

        self.restore_status_label = ctk.CTkLabel(
            progress_frame,
            text="Select a backup to restore",
            font=ctk.CTkFont(size=13)
        )
        self.restore_status_label.grid(row=0, column=0, padx=15, pady=(15, 10), sticky="w")

        self.restore_progress_bar = ctk.CTkProgressBar(progress_frame)
        self.restore_progress_bar.grid(row=1, column=0, padx=15, pady=10, sticky="ew")
        self.restore_progress_bar.set(0)

        self.restore_progress_text = ctk.CTkTextbox(
            progress_frame,
            height=40,
            font=ctk.CTkFont(size=11, family="Courier")
        )
        self.restore_progress_text.grid(row=2, column=0, padx=15, pady=(10, 15), sticky="ew")

        # Restore button
        button_frame = ctk.CTkFrame(self.parent)
        button_frame.grid(row=6, column=0, padx=20, pady=20, sticky="ew")
        button_frame.grid_columnconfigure(0, weight=1)

        self.restore_btn = ctk.CTkButton(
            button_frame,
            text="Restore Backup",
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            state="disabled",
            command=self._start_restore
        )
        self.restore_btn.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        refresh_btn = ctk.CTkButton(
            button_frame,
            text="Refresh List",
            height=40,
            font=ctk.CTkFont(size=14),
            command=self._load_backups
        )
        refresh_btn.grid(row=0, column=1, padx=(10, 0), sticky="ew")

    def _load_backups(self):
        """Load available backups"""
        # Clear existing
        for widget in self.backups_frame.winfo_children():
            widget.destroy()

        backups = self.backup_engine.list_backups()

        if not backups:
            no_backups = ctk.CTkLabel(
                self.backups_frame,
                text="No backups available",
                font=ctk.CTkFont(size=13),
                text_color="gray"
            )
            no_backups.grid(row=0, column=0, pady=50)
            return

        # Display backups in reverse chronological order
        for idx, backup in enumerate(reversed(backups)):
            self._create_backup_card(backup, idx)

    def _create_backup_card(self, backup, idx):
        """Create backup selection card"""
        card = ctk.CTkFrame(self.backups_frame)
        card.grid(row=idx, column=0, padx=5, pady=5, sticky="ew")
        card.grid_columnconfigure(1, weight=1)

        # Radio button for selection
        def select_backup():
            self.selected_backup = backup
            self.restore_btn.configure(state="normal")
            self.restore_status_label.configure(
                text=f"Ready to restore: {backup['name']}"
            )

            # Update all cards to show selection
            for child in self.backups_frame.winfo_children():
                for subchild in child.winfo_children():
                    if isinstance(subchild, ctk.CTkRadioButton):
                        if subchild.cget("text") == "":
                            if backup == self.selected_backup:
                                card.configure(border_width=2, border_color="green")

        # Selection indicator
        select_radio = ctk.CTkRadioButton(
            card,
            text="",
            command=select_backup
        )
        select_radio.grid(row=0, column=0, rowspan=4, padx=10, pady=15)

        # Backup info
        name_label = ctk.CTkLabel(
            card,
            text=backup['name'],
            font=ctk.CTkFont(size=13, weight="bold")
        )
        name_label.grid(row=0, column=1, padx=15, pady=(15, 5), sticky="w")

        type_label = ctk.CTkLabel(
            card,
            text=f"Type: {backup['type'].title()} | Date: {backup['timestamp']}",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        type_label.grid(row=1, column=1, padx=15, pady=2, sticky="w")

        source_text = backup.get('source', 'N/A')
        if len(source_text) > 60:
            source_text = "..." + source_text[-57:]

        source_label = ctk.CTkLabel(
            card,
            text=f"Source: {source_text}",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        source_label.grid(row=2, column=1, padx=15, pady=2, sticky="w")

        # File count
        files_count = len(backup.get('files', []))
        files_label = ctk.CTkLabel(
            card,
            text=f"Files: {files_count}",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        files_label.grid(row=3, column=1, padx=15, pady=(2, 15), sticky="w")

        # Options badges
        options_frame = ctk.CTkFrame(card)
        options_frame.grid(row=0, column=2, rowspan=4, padx=15, pady=15)

        if backup.get('encrypted'):
            ctk.CTkLabel(
                options_frame,
                text="🔒",
                font=ctk.CTkFont(size=16)
            ).pack(side="left", padx=2)

        if backup.get('compressed'):
            ctk.CTkLabel(
                options_frame,
                text="📦",
                font=ctk.CTkFont(size=16)
            ).pack(side="left", padx=2)

        if backup.get('verified'):
            ctk.CTkLabel(
                options_frame,
                text="✓",
                font=ctk.CTkFont(size=16),
                text_color="green"
            ).pack(side="left", padx=2)

    def _browse_restore_destination(self):
        """Browse for restore destination"""
        directory = filedialog.askdirectory(title="Select Restore Destination")
        if directory:
            self.restore_path = directory
            self.restore_entry.delete(0, "end")
            self.restore_entry.insert(0, directory)

    def _update_restore_progress(self, progress: float, message: str):
        """Update restore progress"""
        self.restore_progress_bar.set(progress / 100)
        self.restore_status_label.configure(text=message)
        self.restore_progress_text.insert("end", f"{message}\n")
        self.restore_progress_text.see("end")
        self.main_window.update()

    def _start_restore(self):
        """Start restore process"""
        if not self.selected_backup:
            self.main_window.show_error(
                "Error",
                "Please select a backup to restore"
            )
            return

        if not self.restore_path:
            self.main_window.show_error(
                "Error",
                "Please select a restore destination"
            )
            return

        # Disable button
        self.restore_btn.configure(state="disabled")

        # Clear progress
        self.restore_progress_bar.set(0)
        self.restore_progress_text.delete("1.0", "end")

        # Start restore in thread
        thread = threading.Thread(target=self._run_restore)
        thread.daemon = True
        thread.start()

    def _run_restore(self):
        """Run restore in background thread"""
        try:
            self._update_restore_progress(0, "Starting restore...")

            self.backup_engine.restore_backup(
                backup_info=self.selected_backup,
                restore_path=self.restore_path,
                progress_callback=self._update_restore_progress
            )

            self._update_restore_progress(100, "✓ Restore completed successfully!")
            self.main_window.update_status("Restore completed")

        except Exception as e:
            self._update_restore_progress(0, f"✗ Error: {str(e)}")
            self.main_window.update_status(f"Restore failed: {str(e)}")

        finally:
            self.restore_btn.configure(state="normal")
