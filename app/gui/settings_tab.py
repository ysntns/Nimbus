"""
Settings Tab - Application settings
"""

# import os <-- Kaldırıldı
import customtkinter as ctk
# import yaml <-- Kaldırıldı
from app.core.config import config  # <-- Merkezi config import edildi


class SettingsTab:
    """Settings tab interface"""

    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        
        # Kaldırılan manuel config yönetimi
        # self.config_file = os.path.expanduser("~/.nimbus/config.yaml")
        # self.config_obj = self._load_config()
        
        # Merkezi config manager kullan
        self.config_manager = config
        self.config_obj = self.config_manager.config  # GUI'nin .config özelliğine erişimini koru

        self._create_widgets()

    # _load_config kaldırıldı
    # _save_config kaldırıldı

    def _create_widgets(self):
        """Create all widgets"""
        self.parent.grid_columnconfigure(0, weight=1)

        # General Settings
        general_label = ctk.CTkLabel(self.parent, text="General Settings", font=ctk.CTkFont(size=14, weight="bold"))
        general_label.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")

        general_frame = ctk.CTkFrame(self.parent)
        general_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")
        general_frame.grid_columnconfigure(1, weight=1)

        # Theme
        ctk.CTkLabel(general_frame, text="Theme:", font=ctk.CTkFont(size=13)).grid(
            row=0, column=0, padx=15, pady=15, sticky="w"
        )

        # Ayarları merkezi config'den .get() ile oku
        self.theme_var = ctk.StringVar(value=self.config_manager.get("ui.theme", "dark"))
        theme_menu = ctk.CTkOptionMenu(
            general_frame, values=["dark", "light", "system"], variable=self.theme_var, command=self._change_theme
        )
        theme_menu.grid(row=0, column=1, padx=15, pady=15, sticky="w")

        # Default backup location
        ctk.CTkLabel(general_frame, text="Default Backup Location:", font=ctk.CTkFont(size=13)).grid(
            row=1, column=0, padx=15, pady=15, sticky="w"
        )

        location_frame = ctk.CTkFrame(general_frame)
        location_frame.grid(row=1, column=1, padx=15, pady=15, sticky="ew")
        location_frame.grid_columnconfigure(0, weight=1)

        self.backup_location_entry = ctk.CTkEntry(location_frame, placeholder_text="Select default backup location...")
        self.backup_location_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        # Ayarları merkezi config'den .get() ile oku
        default_loc = self.config_manager.get("backup.default_destination")
        if default_loc:
            self.backup_location_entry.insert(0, default_loc)

        ctk.CTkButton(location_frame, text="Browse", width=80).grid(row=0, column=1) # Not: Browse komutu eklenmemiş, bu ayrı bir iyileştirme

        # Backup Options
        backup_label = ctk.CTkLabel(self.parent, text="Default Backup Options", font=ctk.CTkFont(size=14, weight="bold"))
        backup_label.grid(row=2, column=0, padx=20, pady=(0, 5), sticky="w")

        backup_frame = ctk.CTkFrame(self.parent)
        backup_frame.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="ew")

        # Ayarları merkezi config'den .get() ile oku (doğru anahtarlarla)
        self.default_incremental = ctk.BooleanVar(value=self.config_manager.get("backup.incremental", True))
        ctk.CTkCheckBox(
            backup_frame,
            text="Enable Incremental Backup by Default",
            variable=self.default_incremental,
            font=ctk.CTkFont(size=13),
        ).grid(row=0, column=0, padx=15, pady=10, sticky="w")

        self.default_encrypt = ctk.BooleanVar(value=self.config_manager.get("backup.encryption", False))
        ctk.CTkCheckBox(
            backup_frame, text="Enable Encryption by Default", variable=self.default_encrypt, font=ctk.CTkFont(size=13)
        ).grid(row=1, column=0, padx=15, pady=10, sticky="w")

        self.default_compress = ctk.BooleanVar(value=self.config_manager.get("backup.compression", True))
        ctk.CTkCheckBox(
            backup_frame, text="Enable Compression by Default", variable=self.default_compress, font=ctk.CTkFont(size=13)
        ).grid(row=2, column=0, padx=15, pady=10, sticky="w")

        self.default_verify = ctk.BooleanVar(value=self.config_manager.get("backup.verify_backup", True))
        ctk.CTkCheckBox(
            backup_frame, text="Enable Verification by Default", variable=self.default_verify, font=ctk.CTkFont(size=13)
        ).grid(row=3, column=0, padx=15, pady=10, sticky="w")

        # Notifications
        notif_label = ctk.CTkLabel(self.parent, text="Notifications", font=ctk.CTkFont(size=14, weight="bold"))
        notif_label.grid(row=4, column=0, padx=20, pady=(0, 5), sticky="w")

        notif_frame = ctk.CTkFrame(self.parent)
        notif_frame.grid(row=5, column=0, padx=20, pady=(0, 20), sticky="ew")

        self.notify_success = ctk.BooleanVar(value=self.config_manager.get("notifications.on_success", True))
        ctk.CTkCheckBox(
            notif_frame, text="Notify on Successful Backup", variable=self.notify_success, font=ctk.CTkFont(size=13)
        ).grid(row=0, column=0, padx=15, pady=10, sticky="w")

        self.notify_error = ctk.BooleanVar(value=self.config_manager.get("notifications.on_failure", True))
        ctk.CTkCheckBox(
            notif_frame, text="Notify on Backup Error", variable=self.notify_error, font=ctk.CTkFont(size=13)
        ).grid(row=1, column=0, padx=15, pady=10, sticky="w")

        # Advanced
        advanced_label = ctk.CTkLabel(self.parent, text="Advanced", font=ctk.CTkFont(size=14, weight="bold"))
        advanced_label.grid(row=6, column=0, padx=20, pady=(0, 5), sticky="w")

        advanced_frame = ctk.CTkFrame(self.parent)
        advanced_frame.grid(row=7, column=0, padx=20, pady=(0, 20), sticky="ew")
        advanced_frame.grid_columnconfigure(1, weight=1)

        # Max threads
        ctk.CTkLabel(advanced_frame, text="Max Concurrent Operations:", font=ctk.CTkFont(size=13)).grid(
            row=0, column=0, padx=15, pady=15, sticky="w"
        )

        self.max_threads_var = ctk.StringVar(value=str(self.config_manager.get("performance.threads", 4)))
        threads_menu = ctk.CTkOptionMenu(advanced_frame, values=["1", "2", "4", "8", "16"], variable=self.max_threads_var)
        threads_menu.grid(row=0, column=1, padx=15, pady=15, sticky="w")

        # Buttons
        button_frame = ctk.CTkFrame(self.parent)
        button_frame.grid(row=8, column=0, padx=20, pady=20, sticky="ew")
        button_frame.grid_columnconfigure(0, weight=1)

        save_btn = ctk.CTkButton(
            button_frame,
            text="Save Settings",
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._save_settings,
        )
        save_btn.grid(row=0, column=0, sticky="ew")

    def _change_theme(self, theme):
        """Change application theme"""
        ctk.set_appearance_mode(theme)
        self.config_manager.set("ui.theme", theme) # Sadece ayarla, kaydetme butonuna basılınca kaydedilecek

    def _save_settings(self):
        """Save all settings"""
        try:
            # Ayarları merkezi config'e .set() ile kaydet
            self.config_manager.set("ui.theme", self.theme_var.get())
            self.config_manager.set("backup.default_destination", self.backup_location_entry.get() or None)
            self.config_manager.set("backup.incremental", self.default_incremental.get())
            self.config_manager.set("backup.encryption", self.default_encrypt.get())
            self.config_manager.set("backup.compression", self.default_compress.get())
            self.config_manager.set("backup.verify_backup", self.default_verify.get())
            self.config_manager.set("notifications.on_success", self.notify_success.get())
            self.config_manager.set("notifications.on_failure", self.notify_error.get())
            self.config_manager.set("performance.threads", int(self.max_threads_var.get()))

            # Merkezi config dosyasını kaydet
            self.config_manager.save()
            
            self.main_window.update_status("Settings saved")
            self.main_window.show_info("Success", "Settings saved successfully!")
        except Exception as e:
            self.main_window.update_status(f"Error saving settings: {e}")
            self.main_window.show_error("Error", f"Failed to save settings: {str(e)}")
