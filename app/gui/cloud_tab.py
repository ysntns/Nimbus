"""
Cloud Sync Tab - Google Drive and other cloud providers
"""

import customtkinter as ctk
from tkinter import filedialog
import threading
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app.cloud.google_drive import GoogleDriveProvider

    GDRIVE_AVAILABLE = True
except Exception:
    GDRIVE_AVAILABLE = False


class CloudTab:
    """Cloud sync interface"""

    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.gdrive_client = None
        self.selected_directory = None

        self._create_widgets()

    def _create_widgets(self):
        """Create all widgets"""
        # Configure grid
        self.parent.grid_columnconfigure(0, weight=1)

        # Cloud Provider Selection
        provider_label = ctk.CTkLabel(self.parent, text="Cloud Provider", font=ctk.CTkFont(size=14, weight="bold"))
        provider_label.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")

        provider_frame = ctk.CTkFrame(self.parent)
        provider_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")

        self.provider_var = ctk.StringVar(value="Google Drive")

        providers = ["Google Drive", "Dropbox", "OneDrive", "AWS S3", "Azure Blob"]
        for idx, provider in enumerate(providers):
            radio = ctk.CTkRadioButton(
                provider_frame,
                text=provider,
                variable=self.provider_var,
                value=provider,
                font=ctk.CTkFont(size=13),
                command=self._on_provider_change,
            )
            radio.grid(row=idx // 3, column=idx % 3, padx=15, pady=10, sticky="w")

        # Authentication Section
        auth_label = ctk.CTkLabel(self.parent, text="Authentication", font=ctk.CTkFont(size=14, weight="bold"))
        auth_label.grid(row=2, column=0, padx=20, pady=(0, 5), sticky="w")

        auth_frame = ctk.CTkFrame(self.parent)
        auth_frame.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="ew")
        auth_frame.grid_columnconfigure(1, weight=1)

        self.auth_status_label = ctk.CTkLabel(
            auth_frame, text="Not authenticated", font=ctk.CTkFont(size=13), text_color="gray"
        )
        self.auth_status_label.grid(row=0, column=0, padx=15, pady=15, sticky="w")

        self.auth_btn = ctk.CTkButton(auth_frame, text="Connect to Google Drive", height=35, command=self._authenticate)
        self.auth_btn.grid(row=0, column=1, padx=15, pady=15, sticky="e")

        # Storage Info
        storage_label = ctk.CTkLabel(self.parent, text="Storage Information", font=ctk.CTkFont(size=14, weight="bold"))
        storage_label.grid(row=4, column=0, padx=20, pady=(0, 5), sticky="w")

        self.storage_frame = ctk.CTkFrame(self.parent)
        self.storage_frame.grid(row=5, column=0, padx=20, pady=(0, 20), sticky="ew")

        self.storage_info_label = ctk.CTkLabel(
            self.storage_frame, text="Connect to view storage information", font=ctk.CTkFont(size=12), text_color="gray"
        )
        self.storage_info_label.grid(row=0, column=0, padx=15, pady=20)

        # Upload Section
        upload_label = ctk.CTkLabel(self.parent, text="Upload to Cloud", font=ctk.CTkFont(size=14, weight="bold"))
        upload_label.grid(row=6, column=0, padx=20, pady=(0, 5), sticky="w")

        upload_frame = ctk.CTkFrame(self.parent)
        upload_frame.grid(row=7, column=0, padx=20, pady=(0, 20), sticky="ew")
        upload_frame.grid_columnconfigure(0, weight=1)

        self.upload_entry = ctk.CTkEntry(upload_frame, placeholder_text="Select directory to upload...", height=40)
        self.upload_entry.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        upload_browse_btn = ctk.CTkButton(upload_frame, text="Browse", width=100, height=40, command=self._browse_upload)
        upload_browse_btn.grid(row=0, column=1, padx=10, pady=10)

        # Progress Section
        progress_label = ctk.CTkLabel(self.parent, text="Progress", font=ctk.CTkFont(size=14, weight="bold"))
        progress_label.grid(row=8, column=0, padx=20, pady=(0, 5), sticky="w")

        progress_frame = ctk.CTkFrame(self.parent, height=120)
        progress_frame.grid(row=9, column=0, padx=20, pady=(0, 20), sticky="ew")
        progress_frame.grid_propagate(False)
        progress_frame.grid_columnconfigure(0, weight=1)

        self.cloud_status_label = ctk.CTkLabel(progress_frame, text="Ready", font=ctk.CTkFont(size=13))
        self.cloud_status_label.grid(row=0, column=0, padx=15, pady=(15, 10), sticky="w")

        self.cloud_progress_bar = ctk.CTkProgressBar(progress_frame)
        self.cloud_progress_bar.grid(row=1, column=0, padx=15, pady=10, sticky="ew")
        self.cloud_progress_bar.set(0)

        self.cloud_progress_text = ctk.CTkTextbox(progress_frame, height=40, font=ctk.CTkFont(size=11, family="Courier"))
        self.cloud_progress_text.grid(row=2, column=0, padx=15, pady=(10, 15), sticky="ew")

        # Upload Button
        button_frame = ctk.CTkFrame(self.parent)
        button_frame.grid(row=10, column=0, padx=20, pady=20, sticky="ew")

        self.upload_btn = ctk.CTkButton(
            button_frame,
            text="Upload to Cloud",
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            state="disabled",
            command=self._start_upload,
        )
        self.upload_btn.pack(fill="x", padx=0, pady=0)

    def _on_provider_change(self):
        """Handle provider change"""
        provider = self.provider_var.get()
        self.auth_btn.configure(text=f"Connect to {provider}")
        self.auth_status_label.configure(text="Not authenticated", text_color="gray")
        self.gdrive_client = None
        self.upload_btn.configure(state="disabled")

    def _authenticate(self):
        """Authenticate with selected cloud provider"""
        provider = self.provider_var.get()

        if provider == "Google Drive":
            self._authenticate_google_drive()
        else:
            self.main_window.show_info("Coming Soon", f"{provider} integration will be available in the next update!")

    def _authenticate_google_drive(self):
        """Authenticate with Google Drive"""
        if not GDRIVE_AVAILABLE:
            self.main_window.show_error(
                "Google Drive Not Available",
                "Google Drive dependencies are not installed.\n"
                "Install with: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib",
            )
            return

        self.auth_status_label.configure(text="Authenticating...", text_color="orange")
        self.main_window.update()

        thread = threading.Thread(target=self._run_authentication)
        thread.daemon = True
        thread.start()

    def _run_authentication(self):
        """Run authentication in background"""
        try:
            self.gdrive_client = GoogleDriveProvider()

            # Get storage quota
            quota = self.gdrive_client.get_storage_quota()

            self.auth_status_label.configure(text="✓ Connected to Google Drive", text_color="green")

            # Update storage info
            total_gb = quota["limit"] / (1024**3) if quota["limit"] > 0 else 0
            used_gb = quota["usage"] / (1024**3)
            percent = (quota["usage"] / quota["limit"]) * 100 if quota["limit"] > 0 else 0

            storage_text = f"Storage: {used_gb:.2f} GB / {total_gb:.2f} GB ({percent:.1f}% used)"

            self.storage_info_label.configure(text=storage_text, text_color="white")

            self.upload_btn.configure(state="normal")
            self.main_window.update_status("Connected to Google Drive")

        except FileNotFoundError:
            self.auth_status_label.configure(text="✗ Credentials file not found", text_color="red")
            self.main_window.show_error(
                "Authentication Error",
                "Please download OAuth 2.0 credentials from Google Cloud Console\n" "and save as ~/.nimbus/credentials.json",
            )
        except Exception as e:
            self.auth_status_label.configure(text=f"✗ Authentication failed: {str(e)}", text_color="red")

    def _browse_upload(self):
        """Browse for directory to upload"""
        directory = filedialog.askdirectory(title="Select Directory to Upload")
        if directory:
            self.selected_directory = directory
            self.upload_entry.delete(0, "end")
            self.upload_entry.insert(0, directory)

    def _update_cloud_progress(self, progress: float, message: str):
        """Update cloud progress"""
        self.cloud_progress_bar.set(progress / 100)
        self.cloud_status_label.configure(text=message)
        self.cloud_progress_text.insert("end", f"{message}\n")
        self.cloud_progress_text.see("end")
        self.main_window.update()

    def _start_upload(self):
        """Start upload to cloud"""
        if not self.selected_directory:
            self.main_window.show_error("Error", "Please select a directory to upload")
            return

        if not self.gdrive_client:
            self.main_window.show_error("Error", "Please authenticate first")
            return

        # Disable button
        self.upload_btn.configure(state="disabled")

        # Clear progress
        self.cloud_progress_bar.set(0)
        self.cloud_progress_text.delete("1.0", "end")

        # Start upload in thread
        thread = threading.Thread(target=self._run_upload)
        thread.daemon = True
        thread.start()

    def _run_upload(self):
        """Run upload in background thread"""
        try:
            self._update_cloud_progress(0, "Starting upload to Google Drive...")

            result = self.gdrive_client.upload_directory(
                self.selected_directory, progress_callback=self._update_cloud_progress
            )

            self._update_cloud_progress(100, f"✓ Upload completed! {result.get('files_uploaded', 0)} files uploaded")
            self.main_window.update_status("Upload completed")

        except Exception as e:
            self._update_cloud_progress(0, f"✗ Error: {str(e)}")
            self.main_window.update_status(f"Upload failed: {str(e)}")

        finally:
            self.upload_btn.configure(state="normal")
