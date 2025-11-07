"""
Integration tests for full backup workflow.
"""

import pytest
from pathlib import Path
import tempfile
import shutil


def test_full_backup_with_all_features():
    """Test complete backup workflow with database, compression, and notifications."""
    from app.core.backup import BackupEngine
    from app.utils.database import BackupDatabase, BackupRecord
    from app.utils.compression import CompressionManager
    from datetime import datetime

    # Create temporary directories
    with tempfile.TemporaryDirectory() as temp_dir:
        source_dir = Path(temp_dir) / "source"
        backup_dir = Path(temp_dir) / "backup"
        source_dir.mkdir()
        backup_dir.mkdir()

        # Create test files
        test_files = [
            "file1.txt",
            "file2.txt",
            "subdir/file3.txt"
        ]

        for file_path in test_files:
            full_path = source_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(f"Content of {file_path}")

        # Perform backup
        engine = BackupEngine(source_dir, backup_dir)
        stats = engine.backup()

        # Verify stats
        assert stats['total_files'] == 3
        assert stats['backed_up_files'] == 3
        assert stats['failed_files'] == 0

        # Test database recording
        with BackupDatabase(Path(temp_dir) / "test.db") as db:
            record = BackupRecord(
                source=str(source_dir),
                destination=str(backup_dir),
                started_at=datetime.now(),
                completed_at=datetime.now(),
                status="completed",
                backup_type="full",
                total_files=stats['total_files'],
                backed_up_files=stats['backed_up_files'],
                failed_files=stats['failed_files'],
                total_size=stats['total_size'],
                transferred_size=stats['transferred_size']
            )

            record_id = db.add_backup_record(record)
            assert record_id > 0

            # Retrieve record
            retrieved = db.get_backup_record(record_id)
            assert retrieved is not None
            assert retrieved.total_files == 3

        # Test compression
        test_file = source_dir / "file1.txt"
        compressor = CompressionManager('gzip')

        compressed = compressor.compress_file(test_file)
        assert compressed.exists()
        assert compressed.suffix == '.gz'

        # Cleanup compressed file
        compressed.unlink()


def test_scheduler_basic():
    """Test scheduler basic functionality."""
    try:
        from app.scheduler.scheduler import BackupScheduler, BackupSchedule
        from datetime import datetime
        import tempfile

        with tempfile.TemporaryDirectory() as temp_dir:
            schedules_file = Path(temp_dir) / "schedules.json"

            scheduler = BackupScheduler(schedules_file)

            # Create test schedule
            schedule = BackupSchedule(
                id="test_schedule_1",
                name="Test Backup",
                source="/tmp/source",
                destination="/tmp/backup",
                frequency="daily",
                time="02:00",
                enabled=False  # Don't actually run it
            )

            # Add schedule
            result = scheduler.add_schedule(schedule)
            assert result is True

            # List schedules
            schedules = scheduler.list_schedules()
            assert len(schedules) == 1
            assert schedules[0].id == "test_schedule_1"

            # Remove schedule
            result = scheduler.remove_schedule("test_schedule_1")
            assert result is True

            schedules = scheduler.list_schedules()
            assert len(schedules) == 0

    except ImportError:
        pytest.skip("APScheduler not installed")
