"""
History Tab - View backup history
"""

import customtkinter as ctk
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.backup import BackupEngine


class HistoryTab:
    """History tab interface"""

    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.backup_engine = BackupEngine()

        self._create_widgets()
        self._load_history()

    def _create_widgets(self):
        """Create all widgets"""
        self.parent.grid_columnconfigure(0, weight=1)
        self.parent.grid_rowconfigure(1, weight=1)

        # Header
        header_frame = ctk.CTkFrame(self.parent)
        header_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(
            header_frame,
            text="Backup History",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=15, pady=15, sticky="w")

        refresh_btn = ctk.CTkButton(
            header_frame,
            text="Refresh",
            width=100,
            command=self._load_history
        )
        refresh_btn.grid(row=0, column=1, padx=15, pady=15)

        # History list
        self.history_frame = ctk.CTkScrollableFrame(self.parent)
        self.history_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.history_frame.grid_columnconfigure(0, weight=1)

    def _load_history(self):
        """Load backup history"""
        # Clear existing
        for widget in self.history_frame.winfo_children():
            widget.destroy()

        backups = self.backup_engine.list_backups()

        if not backups:
            no_history = ctk.CTkLabel(
                self.history_frame,
                text="No backup history available",
                font=ctk.CTkFont(size=13),
                text_color="gray"
            )
            no_history.grid(row=0, column=0, pady=50)
            return

        # Display in reverse chronological order
        for idx, backup in enumerate(reversed(backups)):
            self._create_history_card(backup, idx)

    def _create_history_card(self, backup, idx):
        """Create history card"""
        card = ctk.CTkFrame(self.history_frame)
        card.grid(row=idx, column=0, padx=10, pady=5, sticky="ew")
        card.grid_columnconfigure(1, weight=1)

        # Status indicator
        status_color = "green" if backup.get('verified', False) else "gray"
        status_frame = ctk.CTkFrame(card, width=5, fg_color=status_color)
        status_frame.grid(row=0, column=0, rowspan=4, sticky="ns")

        # Info
        name_label = ctk.CTkLabel(
            card,
            text=backup['name'],
            font=ctk.CTkFont(size=13, weight="bold")
        )
        name_label.grid(row=0, column=1, padx=15, pady=(15, 5), sticky="w")

        type_label = ctk.CTkLabel(
            card,
            text=f"Type: {backup['type'].title()}",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        type_label.grid(row=1, column=1, padx=15, pady=2, sticky="w")

        date_label = ctk.CTkLabel(
            card,
            text=f"Date: {backup['timestamp']}",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        date_label.grid(row=2, column=1, padx=15, pady=2, sticky="w")

        # Source and destination
        source_text = backup.get('source', 'N/A')
        if len(source_text) > 50:
            source_text = "..." + source_text[-47:]

        source_label = ctk.CTkLabel(
            card,
            text=f"Source: {source_text}",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        source_label.grid(row=3, column=1, padx=15, pady=(2, 15), sticky="w")

        # Stats
        stats_frame = ctk.CTkFrame(card)
        stats_frame.grid(row=0, column=2, rowspan=4, padx=15, pady=15)

        files_count = len(backup.get('files', []))

        ctk.CTkLabel(
            stats_frame,
            text=str(files_count),
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=2)

        ctk.CTkLabel(
            stats_frame,
            text="Files",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        ).pack()

        # Options badges
        options_frame = ctk.CTkFrame(card)
        options_frame.grid(row=0, column=3, rowspan=4, padx=15, pady=15)

        if backup.get('encrypted'):
            ctk.CTkLabel(
                options_frame,
                text="🔒 Encrypted",
                font=ctk.CTkFont(size=10)
            ).pack(anchor="e", pady=2)

        if backup.get('compressed'):
            ctk.CTkLabel(
                options_frame,
                text="📦 Compressed",
                font=ctk.CTkFont(size=10)
            ).pack(anchor="e", pady=2)

        if backup.get('verified'):
            ctk.CTkLabel(
                options_frame,
                text="✓ Verified",
                font=ctk.CTkFont(size=10),
                text_color="green"
            ).pack(anchor="e", pady=2)
