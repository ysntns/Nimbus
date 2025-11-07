"""
Backup scheduling and automation.

APScheduler-based task scheduling for automated backups.
"""

try:
    from app.scheduler.scheduler import BackupSchedule, BackupScheduler  # noqa: F401

    __all__ = ["BackupScheduler", "BackupSchedule"]
except ImportError:
    # APScheduler not installed
    __all__ = []
