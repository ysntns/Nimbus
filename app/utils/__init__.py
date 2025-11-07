"""
Utility functions and helpers.

Common utilities, helpers, and shared functionality.
"""

from app.utils.helpers import (
    format_size,
    parse_size,
    format_duration,
    format_datetime,
    format_relative_time,
    safe_filename,
    ensure_directory,
    get_file_count,
    get_directory_size,
    generate_backup_name,
    validate_email,
    truncate_string
)

from app.utils.database import BackupDatabase, BackupRecord

from app.utils.compression import CompressionManager

from app.utils.notifications import NotificationManager, NotificationConfig, NotificationType

__all__ = [
    # Helpers
    'format_size',
    'parse_size',
    'format_duration',
    'format_datetime',
    'format_relative_time',
    'safe_filename',
    'ensure_directory',
    'get_file_count',
    'get_directory_size',
    'generate_backup_name',
    'validate_email',
    'truncate_string',
    # Database
    'BackupDatabase',
    'BackupRecord',
    # Compression
    'CompressionManager',
    # Notifications
    'NotificationManager',
    'NotificationConfig',
    'NotificationType',
]
