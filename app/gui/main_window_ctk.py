"""
Nimbus Main GUI Window - CustomTkinter Version
Modern interface with CustomTkinter
"""

import customtkinter as ctk
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.gui.backup_tab import BackupTab  # noqa: E402
from app.gui.restore_tab import RestoreTab  # noqa: E402
from app.gui.schedule_tab import ScheduleTab  # noqa: E402
from app.gui.history_tab import HistoryTab  # noqa: E402
from app.gui.settings_tab import SettingsTab  # noqa: E402
from app.gui.cloud_tab import CloudTab  # noqa: E402


class NimbusGUI(ctk.CTk):
    """Main application window"""

    def __init__(self):
        super().__init__()

        # Configure window
        self.title("Nimbus - Enterprise Backup Solution")
        self.geometry("1000x700")

        # Set theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Configure grid
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Create header
        self._create_header()

        # Create tab view
        self._create_tabs()

        # Status bar
        self._create_status_bar()

    def _create_header(self):
        """Create header with title"""
        header_frame = ctk.CTkFrame(self, height=60, corner_radius=0)
        header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        header_frame.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(
            header_frame, text="☁️ Nimbus - Enterprise Backup Solution", font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.grid(row=0, column=0, pady=15, padx=20)

    def _create_tabs(self):
        """Create tab view with all tabs"""
        self.tabview = ctk.CTkTabview(self, corner_radius=10)
        self.tabview.grid(row=1, column=0, padx=20, pady=(10, 10), sticky="nsew")

        # Add tabs
        self.tabview.add("Backup")
        self.tabview.add("Cloud Sync")
        self.tabview.add("Restore")
        self.tabview.add("Schedule")
        self.tabview.add("History")
        self.tabview.add("Settings")

        # Initialize tab contents
        self.backup_tab = BackupTab(self.tabview.tab("Backup"), self)
        self.cloud_tab = CloudTab(self.tabview.tab("Cloud Sync"), self)
        self.restore_tab = RestoreTab(self.tabview.tab("Restore"), self)
        self.schedule_tab = ScheduleTab(self.tabview.tab("Schedule"), self)
        self.history_tab = HistoryTab(self.tabview.tab("History"), self)
        self.settings_tab = SettingsTab(self.tabview.tab("Settings"), self)

    def _create_status_bar(self):
        """Create status bar at bottom"""
        self.status_frame = ctk.CTkFrame(self, height=30, corner_radius=0)
        self.status_frame.grid(row=2, column=0, sticky="ew", padx=0, pady=0)

        self.status_label = ctk.CTkLabel(self.status_frame, text="Ready", font=ctk.CTkFont(size=12))
        self.status_label.pack(side="left", padx=10, pady=5)

    def update_status(self, message: str):
        """Update status bar message"""
        self.status_label.configure(text=message)
        self.update()

    def show_error(self, title: str, message: str):
        """Show error dialog"""
        dialog = ctk.CTkToplevel(self)
        dialog.title(title)
        dialog.geometry("400x200")

        # Center the dialog
        dialog.transient(self)
        dialog.grab_set()

        # Message
        msg_label = ctk.CTkLabel(dialog, text=message, font=ctk.CTkFont(size=13), wraplength=350)
        msg_label.pack(pady=30, padx=20)

        # OK button
        ok_btn = ctk.CTkButton(dialog, text="OK", width=100, command=dialog.destroy)
        ok_btn.pack(pady=10)

    def show_info(self, title: str, message: str):
        """Show info dialog"""
        dialog = ctk.CTkToplevel(self)
        dialog.title(title)
        dialog.geometry("400x200")

        # Center the dialog
        dialog.transient(self)
        dialog.grab_set()

        # Message
        msg_label = ctk.CTkLabel(dialog, text=message, font=ctk.CTkFont(size=13), wraplength=350)
        msg_label.pack(pady=30, padx=20)

        # OK button
        ok_btn = ctk.CTkButton(dialog, text="OK", width=100, command=dialog.destroy)
        ok_btn.pack(pady=10)


def main():
    """Main entry point"""
    app = NimbusGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
