"""
Utility functions and helpers.

Common utilities, helpers, and shared functionality.
"""

from app.utils.compression import CompressionManager
from app.utils.database import BackupDatabase, BackupRecord
from app.utils.helpers import (
    ensure_directory,
    format_datetime,
    format_duration,
    format_relative_time,
    format_size,
    generate_backup_name,
    get_directory_size,
    get_file_count,
    parse_size,
    safe_filename,
    truncate_string,
    validate_email,
)
from app.utils.notifications import NotificationConfig, NotificationManager, NotificationType

__all__ = [
    # Helpers
    "format_size",
    "parse_size",
    "format_duration",
    "format_datetime",
    "format_relative_time",
    "safe_filename",
    "ensure_directory",
    "get_file_count",
    "get_directory_size",
    "generate_backup_name",
    "validate_email",
    "truncate_string",
    # Database
    "BackupDatabase",
    "BackupRecord",
    # Compression
    "CompressionManager",
    # Notifications
    "NotificationManager",
    "NotificationConfig",
    "NotificationType",
]
