"""
Unit tests for BackupEngine

Tests the core backup functionality.
"""

import shutil
import tempfile
from pathlib import Path

import pytest

from app.core.backup import BackupEngine, IncrementalBackup


class TestBackupEngine:
    """Test cases for BackupEngine."""

    @pytest.fixture
    def temp_dirs(self):
        """Create temporary source and destination directories."""
        source = Path(tempfile.mkdtemp())
        destination = Path(tempfile.mkdtemp())

        yield source, destination

        # Cleanup
        shutil.rmtree(source, ignore_errors=True)
        shutil.rmtree(destination, ignore_errors=True)

    @pytest.fixture
    def sample_files(self, temp_dirs):
        """Create sample files in source directory."""
        source, destination = temp_dirs

        # Create test files
        (source / "file1.txt").write_text("Hello World")
        (source / "file2.txt").write_text("Test Content")

        # Create subdirectory with file
        subdir = source / "subdir"
        subdir.mkdir()
        (subdir / "file3.txt").write_text("Subdirectory file")

        return source, destination

    def test_initialization(self, temp_dirs):
        """Test BackupEngine initialization."""
        source, destination = temp_dirs
        engine = BackupEngine(source, destination)

        assert engine.source == source
        assert engine.destination == destination
        assert engine.stats["total_files"] == 0

    def test_scan_directory(self, sample_files):
        """Test directory scanning."""
        source, destination = sample_files
        engine = BackupEngine(source, destination)

        files = engine.scan_directory()

        assert len(files) == 3
        assert engine.stats["total_files"] == 3

    def test_backup_single_file(self, sample_files):
        """Test backing up a single file."""
        source, destination = sample_files
        engine = BackupEngine(source, destination)

        test_file = source / "file1.txt"
        result = engine.backup_file(test_file, verify=False)

        assert result["success"] is True
        assert result["size"] > 0

        # Check destination file exists
        dest_file = destination / "file1.txt"
        assert dest_file.exists()
        assert dest_file.read_text() == "Hello World"

    def test_backup_with_verification(self, sample_files):
        """Test backup with checksum verification."""
        source, destination = sample_files
        engine = BackupEngine(source, destination)

        test_file = source / "file1.txt"
        result = engine.backup_file(test_file, verify=True)

        assert result["success"] is True
        assert result["checksum"] != ""

    def test_full_backup(self, sample_files):
        """Test full backup operation."""
        source, destination = sample_files
        engine = BackupEngine(source, destination)

        stats = engine.backup()

        assert stats["backed_up_files"] == 3
        assert stats["failed_files"] == 0
        assert stats["total_files"] == 3

    def test_exclude_patterns(self, temp_dirs):
        """Test file exclusion patterns."""
        source, destination = temp_dirs

        # Create files
        (source / "file.txt").write_text("Include")
        (source / "file.tmp").write_text("Exclude")
        (source / "file.log").write_text("Exclude")

        engine = BackupEngine(source, destination)
        engine.exclude_patterns = ["*.tmp", "*.log"]

        files = engine.scan_directory()

        assert len(files) == 1
        assert files[0].name == "file.txt"

    def test_restore(self, sample_files):
        """Test restore operation."""
        source, destination = sample_files
        engine = BackupEngine(source, destination)

        # First, do backup
        engine.backup()

        # Create restore directory
        restore_dir = Path(tempfile.mkdtemp())

        try:
            # Restore
            stats = engine.restore(restore_dir)

            assert stats["restored_files"] == 3
            assert (restore_dir / "file1.txt").exists()
            assert (restore_dir / "file2.txt").exists()
            assert (restore_dir / "subdir" / "file3.txt").exists()

        finally:
            shutil.rmtree(restore_dir, ignore_errors=True)


class TestIncrementalBackup:
    """Test cases for IncrementalBackup."""

    @pytest.fixture
    def temp_dirs(self):
        """Create temporary directories."""
        source = Path(tempfile.mkdtemp())
        destination = Path(tempfile.mkdtemp())

        yield source, destination

        shutil.rmtree(source, ignore_errors=True)
        shutil.rmtree(destination, ignore_errors=True)

    def test_first_backup(self, temp_dirs):
        """Test first incremental backup."""
        source, destination = temp_dirs

        # Create files
        (source / "file1.txt").write_text("Content 1")
        (source / "file2.txt").write_text("Content 2")

        engine = IncrementalBackup(source, destination)
        stats = engine.backup()

        assert stats["backed_up_files"] == 2

    def test_no_changes_backup(self, temp_dirs):
        """Test backup when no files changed."""
        source, destination = temp_dirs

        # Create and backup files
        (source / "file1.txt").write_text("Content 1")

        engine = IncrementalBackup(source, destination)
        engine.backup()

        # Second backup with no changes
        engine2 = IncrementalBackup(source, destination)
        stats = engine2.backup()

        assert stats["backed_up_files"] == 0

    def test_changed_file_backup(self, temp_dirs):
        """Test backup when file is modified."""
        source, destination = temp_dirs

        file_path = source / "file1.txt"
        file_path.write_text("Original content")

        # First backup
        engine = IncrementalBackup(source, destination)
        engine.backup()

        # Modify file
        import time

        time.sleep(0.1)  # Ensure different timestamp
        file_path.write_text("Modified content")

        # Second backup
        engine2 = IncrementalBackup(source, destination)
        stats = engine2.backup()

        assert stats["backed_up_files"] == 1


if __name__ == "__main__":
    pytest.main([__file__])
