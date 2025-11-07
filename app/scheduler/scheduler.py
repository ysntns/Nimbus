"""
Scheduler Module - Automated backup scheduling using APScheduler

Provides scheduled backup functionality with cron-like scheduling.
"""

from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime, time
from dataclasses import dataclass, asdict
import json
from loguru import logger

try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger
    from apscheduler.triggers.interval import IntervalTrigger
    from apscheduler.job import Job
    APSCHEDULER_AVAILABLE = True
except ImportError:
    APSCHEDULER_AVAILABLE = False
    logger.warning("APScheduler not available - install with: pip install apscheduler")


@dataclass
class BackupSchedule:
    """Represents a backup schedule configuration."""

    id: str
    name: str
    source: str
    destination: str
    frequency: str  # 'hourly', 'daily', 'weekly', 'monthly'
    time: Optional[str] = None  # HH:MM for daily/weekly/monthly
    days: Optional[List[str]] = None  # For weekly: ['monday', 'friday']
    enabled: bool = True
    incremental: bool = True
    encrypt: bool = False
    compress: bool = True
    created_at: Optional[datetime] = None
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        if self.created_at:
            data['created_at'] = self.created_at.isoformat()
        if self.last_run:
            data['last_run'] = self.last_run.isoformat()
        if self.next_run:
            data['next_run'] = self.next_run.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BackupSchedule':
        """Create from dictionary."""
        if 'created_at' in data and data['created_at']:
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if 'last_run' in data and data['last_run']:
            data['last_run'] = datetime.fromisoformat(data['last_run'])
        if 'next_run' in data and data['next_run']:
            data['next_run'] = datetime.fromisoformat(data['next_run'])
        return cls(**data)


class BackupScheduler:
    """Manages scheduled backups."""

    def __init__(self, schedules_file: Optional[Path] = None):
        """Initialize backup scheduler.

        Args:
            schedules_file: Path to schedules configuration file
        """
        if not APSCHEDULER_AVAILABLE:
            raise ImportError("APScheduler not available")

        self.schedules_file = schedules_file or Path.home() / '.config' / 'nimbus' / 'schedules.json'
        self.scheduler = BackgroundScheduler()
        self.schedules: Dict[str, BackupSchedule] = {}
        self.backup_callback: Optional[Callable] = None

        # Load schedules
        self._load_schedules()

        logger.info("Backup scheduler initialized")

    def _load_schedules(self):
        """Load schedules from file."""
        if self.schedules_file.exists():
            try:
                with open(self.schedules_file, 'r') as f:
                    data = json.load(f)

                for schedule_data in data:
                    schedule = BackupSchedule.from_dict(schedule_data)
                    self.schedules[schedule.id] = schedule

                logger.info(f"Loaded {len(self.schedules)} schedules from {self.schedules_file}")

            except Exception as e:
                logger.error(f"Failed to load schedules: {e}")

    def _save_schedules(self):
        """Save schedules to file."""
        try:
            self.schedules_file.parent.mkdir(parents=True, exist_ok=True)

            data = [schedule.to_dict() for schedule in self.schedules.values()]

            with open(self.schedules_file, 'w') as f:
                json.dump(data, f, indent=2)

            logger.debug(f"Saved {len(self.schedules)} schedules to {self.schedules_file}")

        except Exception as e:
            logger.error(f"Failed to save schedules: {e}")

    def set_backup_callback(self, callback: Callable):
        """Set callback function for backup execution.

        Args:
            callback: Function to call for backup (should accept schedule as argument)
        """
        self.backup_callback = callback
        logger.debug("Backup callback set")

    def add_schedule(self, schedule: BackupSchedule) -> bool:
        """Add a new backup schedule.

        Args:
            schedule: BackupSchedule configuration

        Returns:
            True if schedule added successfully
        """
        try:
            # Set creation time
            if not schedule.created_at:
                schedule.created_at = datetime.now()

            # Add to schedules
            self.schedules[schedule.id] = schedule

            # Add to scheduler if enabled
            if schedule.enabled:
                self._add_job(schedule)

            # Save schedules
            self._save_schedules()

            logger.info(f"Added backup schedule: {schedule.name} ({schedule.id})")
            return True

        except Exception as e:
            logger.error(f"Failed to add schedule: {e}")
            return False

    def remove_schedule(self, schedule_id: str) -> bool:
        """Remove a backup schedule.

        Args:
            schedule_id: ID of schedule to remove

        Returns:
            True if schedule removed successfully
        """
        if schedule_id not in self.schedules:
            logger.warning(f"Schedule not found: {schedule_id}")
            return False

        try:
            # Remove from scheduler
            if self.scheduler.get_job(schedule_id):
                self.scheduler.remove_job(schedule_id)

            # Remove from schedules
            del self.schedules[schedule_id]

            # Save schedules
            self._save_schedules()

            logger.info(f"Removed backup schedule: {schedule_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to remove schedule: {e}")
            return False

    def enable_schedule(self, schedule_id: str) -> bool:
        """Enable a backup schedule.

        Args:
            schedule_id: ID of schedule to enable

        Returns:
            True if schedule enabled successfully
        """
        if schedule_id not in self.schedules:
            return False

        try:
            schedule = self.schedules[schedule_id]
            schedule.enabled = True

            # Add job to scheduler
            self._add_job(schedule)

            # Save schedules
            self._save_schedules()

            logger.info(f"Enabled backup schedule: {schedule_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to enable schedule: {e}")
            return False

    def disable_schedule(self, schedule_id: str) -> bool:
        """Disable a backup schedule.

        Args:
            schedule_id: ID of schedule to disable

        Returns:
            True if schedule disabled successfully
        """
        if schedule_id not in self.schedules:
            return False

        try:
            schedule = self.schedules[schedule_id]
            schedule.enabled = False

            # Remove job from scheduler
            if self.scheduler.get_job(schedule_id):
                self.scheduler.remove_job(schedule_id)

            # Save schedules
            self._save_schedules()

            logger.info(f"Disabled backup schedule: {schedule_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to disable schedule: {e}")
            return False

    def _add_job(self, schedule: BackupSchedule):
        """Add a job to the scheduler.

        Args:
            schedule: BackupSchedule configuration
        """
        # Create trigger based on frequency
        trigger = self._create_trigger(schedule)

        # Add job
        job = self.scheduler.add_job(
            self._execute_backup,
            trigger=trigger,
            id=schedule.id,
            name=schedule.name,
            args=[schedule]
        )

        # Update next run time
        if job.next_run_time:
            schedule.next_run = job.next_run_time

        logger.debug(f"Added job to scheduler: {schedule.id}")

    def _create_trigger(self, schedule: BackupSchedule):
        """Create trigger for schedule.

        Args:
            schedule: BackupSchedule configuration

        Returns:
            APScheduler trigger
        """
        if schedule.frequency == 'hourly':
            return IntervalTrigger(hours=1)

        elif schedule.frequency == 'daily':
            hour, minute = self._parse_time(schedule.time or '00:00')
            return CronTrigger(hour=hour, minute=minute)

        elif schedule.frequency == 'weekly':
            hour, minute = self._parse_time(schedule.time or '00:00')
            days = schedule.days or ['monday']
            day_of_week = ','.join(days)
            return CronTrigger(day_of_week=day_of_week, hour=hour, minute=minute)

        elif schedule.frequency == 'monthly':
            hour, minute = self._parse_time(schedule.time or '00:00')
            return CronTrigger(day=1, hour=hour, minute=minute)

        else:
            # Default to daily
            return CronTrigger(hour=0, minute=0)

    def _parse_time(self, time_str: str) -> tuple:
        """Parse time string (HH:MM) to hour and minute.

        Args:
            time_str: Time string

        Returns:
            Tuple of (hour, minute)
        """
        try:
            hour, minute = map(int, time_str.split(':'))
            return hour, minute
        except:
            return 0, 0

    def _execute_backup(self, schedule: BackupSchedule):
        """Execute a scheduled backup.

        Args:
            schedule: BackupSchedule configuration
        """
        logger.info(f"Executing scheduled backup: {schedule.name}")

        # Update last run time
        schedule.last_run = datetime.now()

        try:
            # Call backup callback
            if self.backup_callback:
                self.backup_callback(schedule)
                logger.info(f"Completed scheduled backup: {schedule.name}")
            else:
                logger.warning("No backup callback set - skipping backup execution")

        except Exception as e:
            logger.error(f"Scheduled backup failed: {e}")

        finally:
            # Update next run time
            job = self.scheduler.get_job(schedule.id)
            if job and job.next_run_time:
                schedule.next_run = job.next_run_time

            # Save schedules
            self._save_schedules()

    def start(self):
        """Start the scheduler."""
        if not self.scheduler.running:
            # Add all enabled schedules
            for schedule in self.schedules.values():
                if schedule.enabled:
                    self._add_job(schedule)

            self.scheduler.start()
            logger.info("Backup scheduler started")

    def stop(self):
        """Stop the scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Backup scheduler stopped")

    def list_schedules(self) -> List[BackupSchedule]:
        """List all schedules.

        Returns:
            List of BackupSchedule objects
        """
        return list(self.schedules.values())

    def get_schedule(self, schedule_id: str) -> Optional[BackupSchedule]:
        """Get a specific schedule.

        Args:
            schedule_id: Schedule ID

        Returns:
            BackupSchedule or None if not found
        """
        return self.schedules.get(schedule_id)

    def is_running(self) -> bool:
        """Check if scheduler is running.

        Returns:
            True if scheduler is running
        """
        return self.scheduler.running
