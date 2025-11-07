"""
Backup scheduling and automation.

APScheduler-based task scheduling for automated backups.
"""

try:
    from app.scheduler.scheduler import BackupScheduler, BackupSchedule
    __all__ = ['BackupScheduler', 'BackupSchedule']
except ImportError:
    # APScheduler not installed
    __all__ = []
