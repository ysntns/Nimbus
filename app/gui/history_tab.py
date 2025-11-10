"""
History Tab - View backup history (Coming Soon)
"""

import customtkinter as ctk


class HistoryTab:
    """History tab interface"""

    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window

        self._create_widgets()

    def _create_widgets(self):
        """Create all widgets"""
        # Configure grid
        self.parent.grid_columnconfigure(0, weight=1)
        self.parent.grid_rowconfigure(0, weight=1)

        # Coming soon frame
        container = ctk.CTkFrame(self.parent)
        container.grid(row=0, column=0, sticky="nsew", padx=40, pady=40)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Icon
        icon_label = ctk.CTkLabel(container, text="📜", font=ctk.CTkFont(size=80))
        icon_label.pack(pady=(50, 20))

        # Title
        title_label = ctk.CTkLabel(container, text="Backup History", font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(pady=(0, 10))

        # Description
        desc_label = ctk.CTkLabel(
            container,
            text="The backup history feature is coming soon!\n\n"
            "You'll be able to:\n"
            "• View all past backups with timestamps\n"
            "• See backup sizes and file counts\n"
            "• Check backup status and verification\n"
            "• Search and filter backup history",
            font=ctk.CTkFont(size=14),
            text_color="gray",
        )
        desc_label.pack(pady=20)

        # Status
        status_label = ctk.CTkLabel(
            container,
            text="Check your backup destination directory for completed backups.",
            font=ctk.CTkFont(size=12),
            text_color="orange",
        )
        status_label.pack(pady=30)
