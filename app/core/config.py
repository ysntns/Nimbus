"""
Configuration Manager for Nimbus

Handles all configuration file operations, default settings, and user preferences.
"""

from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from loguru import logger


class ConfigManager:
    """Manages application configuration."""

    DEFAULT_CONFIG_DIR = Path.home() / ".config" / "nimbus"
    DEFAULT_CONFIG_FILE = DEFAULT_CONFIG_DIR / "config.yaml"
    DEFAULT_PROVIDERS_FILE = DEFAULT_CONFIG_DIR / "providers.yaml"

    DEFAULT_CONFIG = {
        "backup": {
            "default_destination": None,
            "compression": True,
            "compression_level": 6,
            "encryption": False,
            "incremental": True,
            "exclude_patterns": [
                "*.tmp",
                "*.temp",
                "*.log",
                "__pycache__",
                "node_modules",
                ".git",
                ".venv",
                "venv",
            ],
            "max_file_size": "5GB",
            "verify_backup": True,
        },
        "schedule": {
            "enabled": False,
            "time": "23:00",
            "frequency": "daily",
            "days": [
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday",
                "sunday",
            ],
        },
        "notifications": {
            "email": False,
            "email_address": None,
            "telegram": False,
            "telegram_token": None,
            "telegram_chat_id": None,
            "desktop": True,
            "on_success": True,
            "on_failure": True,
            "on_warning": True,
        },
        "performance": {
            "threads": 4,
            "chunk_size": "10MB",
            "bandwidth_limit": None,
            "retry_attempts": 3,
            "retry_delay": 5,
            "timeout": 300,
        },
        "security": {
            "encryption_algorithm": "AES256",
            "hash_algorithm": "SHA256",
            "key_derivation": "PBKDF2",
            "key_iterations": 100000,
        },
        "logging": {
            "level": "INFO",
            "file": str(DEFAULT_CONFIG_DIR / "logs" / "nimbus.log"),
            "max_size": "100MB",
            "backup_count": 10,
            "format": "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        },
        "ui": {
            "theme": "dark",
            "language": "en",
            "show_hidden_files": False,
            "confirm_before_backup": True,
            "minimize_to_tray": True,
        },
        "updates": {
            "check_on_startup": True,
            "auto_update": False,
            "update_channel": "stable",
        },
    }

    def __init__(self, config_file: Optional[Path] = None):
        """Initialize configuration manager.

        Args:
            config_file: Path to config file. Uses default if None.
        """
        self.config_file = config_file or self.DEFAULT_CONFIG_FILE
        self.providers_file = self.DEFAULT_PROVIDERS_FILE
        self.config: Dict[str, Any] = {}
        self.providers: Dict[str, Any] = {}

        # Ensure config directory exists
        self._ensure_config_dir()

        # Load or create configuration
        self.load()

    def _ensure_config_dir(self):
        """Create configuration directory if it doesn't exist."""
        self.DEFAULT_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        (self.DEFAULT_CONFIG_DIR / "logs").mkdir(exist_ok=True)
        (self.DEFAULT_CONFIG_DIR / "keys").mkdir(exist_ok=True)
        (self.DEFAULT_CONFIG_DIR / "backups").mkdir(exist_ok=True)
        logger.info(f"Config directory: {self.DEFAULT_CONFIG_DIR}")

    def load(self):
        """Load configuration from file or create default."""
        try:
            if self.config_file.exists():
                with open(self.config_file, "r") as f:
                    self.config = yaml.safe_load(f) or {}
                logger.info(f"Configuration loaded from {self.config_file}")
            else:
                self.config = self.DEFAULT_CONFIG.copy()
                self.save()
                logger.info("Default configuration created")

            # Load providers config
            if self.providers_file.exists():
                with open(self.providers_file, "r") as f:
                    self.providers = yaml.safe_load(f) or {}
            else:
                self.providers = {}

        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            self.config = self.DEFAULT_CONFIG.copy()

    def save(self):
        """Save configuration to file."""
        try:
            with open(self.config_file, "w") as f:
                yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)
            logger.info(f"Configuration saved to {self.config_file}")

            if self.providers:
                with open(self.providers_file, "w") as f:
                    yaml.dump(self.providers, f, default_flow_style=False)
                logger.info(f"Providers configuration saved to {self.providers_file}")

        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            raise

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key path.

        Args:
            key: Dot-separated key path (e.g., 'backup.compression')
            default: Default value if key doesn't exist

        Returns:
            Configuration value
        """
        keys = key.split(".")
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any):
        """Set configuration value by key path.

        Args:
            key: Dot-separated key path (e.g., 'backup.compression')
            value: Value to set
        """
        keys = key.split(".")
        config = self.config

        for k in keys[:-1]:
            if k not in config or not isinstance(config[k], dict):
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value
        logger.debug(f"Configuration updated: {key} = {value}")

    def add_provider(self, name: str, provider_config: Dict[str, Any]):
        """Add cloud provider configuration.

        Args:
            name: Provider name
            provider_config: Provider configuration dictionary
        """
        self.providers[name] = provider_config
        logger.info(f"Provider added: {name}")

    def get_provider(self, name: str) -> Optional[Dict[str, Any]]:
        """Get cloud provider configuration.

        Args:
            name: Provider name

        Returns:
            Provider configuration or None
        """
        return self.providers.get(name)

    def list_providers(self) -> list:
        """List all configured providers.

        Returns:
            List of provider names
        """
        return list(self.providers.keys())

    def remove_provider(self, name: str):
        """Remove cloud provider configuration.

        Args:
            name: Provider name
        """
        if name in self.providers:
            del self.providers[name]
            logger.info(f"Provider removed: {name}")

    def reset_to_default(self):
        """Reset configuration to default values."""
        self.config = self.DEFAULT_CONFIG.copy()
        self.save()
        logger.warning("Configuration reset to default values")

    def export_config(self, export_path: Path):
        """Export configuration to specified path.

        Args:
            export_path: Path to export configuration
        """
        try:
            with open(export_path, "w") as f:
                yaml.dump(self.config, f, default_flow_style=False)
            logger.info(f"Configuration exported to {export_path}")
        except Exception as e:
            logger.error(f"Error exporting configuration: {e}")
            raise

    def import_config(self, import_path: Path):
        """Import configuration from specified path.

        Args:
            import_path: Path to import configuration from
        """
        try:
            with open(import_path, "r") as f:
                imported_config = yaml.safe_load(f)

            if isinstance(imported_config, dict):
                self.config = imported_config
                self.save()
                logger.info(f"Configuration imported from {import_path}")
            else:
                raise ValueError("Invalid configuration format")

        except Exception as e:
            logger.error(f"Error importing configuration: {e}")
            raise


# Global configuration instance
config = ConfigManager()
