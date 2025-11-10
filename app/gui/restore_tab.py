"""
Restore Tab - Restore backups interface (Coming Soon)
"""

import customtkinter as ctk


class RestoreTab:
    """Restore tab interface"""

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
        icon_label = ctk.CTkLabel(container, text="🔄", font=ctk.CTkFont(size=80))
        icon_label.pack(pady=(50, 20))

        # Title
        title_label = ctk.CTkLabel(container, text="Restore Functionality", font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(pady=(0, 10))

        # Description
        desc_label = ctk.CTkLabel(
            container,
            text="The restore feature is coming soon!\n\n"
            "You'll be able to:\n"
            "• Browse available backups\n"
            "• Select specific files or folders to restore\n"
            "• View backup metadata and timestamps\n"
            "• Restore to original or custom location",
            font=ctk.CTkFont(size=14),
            text_color="gray",
        )
        desc_label.pack(pady=20)

        # Status
        status_label = ctk.CTkLabel(
            container,
            text="For now, you can manually restore files from the backup destination directory.",
            font=ctk.CTkFont(size=12),
            text_color="orange",
        )
        status_label.pack(pady=30)
