"""
Backup Engine - Core backup functionality

Handles backup operations, file tracking, versioning, and restoration.
"""

import hashlib
import os
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from loguru import logger

from app.core.config import config


class BackupEngine:
    """Core backup engine for Nimbus."""

    def __init__(self, source: Path, destination: Path):
        """Initialize backup engine.

        Args:
            source: Source directory to backup
            destination: Destination path for backup
        """
        self.source = Path(source)
        self.destination = Path(destination)
        self.stats = {
            "total_files": 0,
            "backed_up_files": 0,
            "skipped_files": 0,
            "failed_files": 0,
            "total_size": 0,
            "transferred_size": 0,
            "start_time": None,
            "end_time": None,
        }
        self.exclude_patterns = config.get("backup.exclude_patterns", [])
        self.max_threads = config.get("performance.threads", 4)

    def should_exclude(self, path: Path) -> bool:
        """Check if file should be excluded from backup.

        Args:
            path: File path to check

        Returns:
            True if file should be excluded
        """
        for pattern in self.exclude_patterns:
            if path.match(pattern):
                return True
        return False

    def calculate_checksum(self, file_path: Path, algorithm: str = "sha256") -> str:
        """Calculate file checksum.

        Args:
            file_path: Path to file
            algorithm: Hash algorithm (sha256, md5, etc.)

        Returns:
            File checksum as hex string
        """
        hash_obj = hashlib.new(algorithm)
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    hash_obj.update(chunk)
            return hash_obj.hexdigest()
        except Exception as e:
            logger.error(f"Error calculating checksum for {file_path}: {e}")
            return ""

    def scan_directory(self, progress_callback: Optional[Callable] = None) -> List[Path]:
        """Scan source directory and collect files to backup.

        Args:
            progress_callback: Optional callback for progress updates

        Returns:
            List of file paths to backup
        """
        files_to_backup = []

        logger.info(f"Scanning directory: {self.source}")

        try:
            for root, dirs, files in os.walk(self.source):
                root_path = Path(root)

                # Filter out excluded directories
                dirs[:] = [d for d in dirs if not self.should_exclude(root_path / d)]

                for file in files:
                    file_path = root_path / file

                    if not self.should_exclude(file_path):
                        files_to_backup.append(file_path)
                        self.stats["total_files"] += 1

                        if file_path.exists():
                            self.stats["total_size"] += file_path.stat().st_size

                        if progress_callback:
                            progress_callback(
                                {
                                    "phase": "scanning",
                                    "current_file": str(file_path),
                                    "total_files": self.stats["total_files"],
                                }
                            )

            logger.info(f"Scan complete: {len(files_to_backup)} files found")
            return files_to_backup

        except Exception as e:
            logger.error(f"Error scanning directory: {e}")
            raise

    def backup_file(self, file_path: Path, verify: bool = True) -> Dict[str, Any]:
        """Backup a single file.

        Args:
            file_path: Path to file to backup
            verify: Whether to verify backup integrity

        Returns:
            Dictionary with backup result
        """
        result = {
            "path": str(file_path),
            "success": False,
            "size": 0,
            "checksum": "",
            "error": None,
        }

        try:
            # Calculate relative path
            rel_path = file_path.relative_to(self.source)
            dest_path = self.destination / rel_path

            # Create destination directory
            dest_path.parent.mkdir(parents=True, exist_ok=True)

            # Calculate source checksum if verification enabled
            source_checksum = ""
            if verify:
                source_checksum = self.calculate_checksum(file_path)

            # Copy file
            shutil.copy2(file_path, dest_path)

            # Verify backup if enabled
            if verify:
                dest_checksum = self.calculate_checksum(dest_path)
                if source_checksum != dest_checksum:
                    raise ValueError("Checksum mismatch - backup verification failed")

            # Update result
            result["success"] = True
            result["size"] = file_path.stat().st_size
            result["checksum"] = source_checksum

            logger.debug(f"Backed up: {file_path} -> {dest_path}")

        except Exception as e:
            result["error"] = str(e)
            logger.error(f"Error backing up {file_path}: {e}")

        return result

    def backup(self, progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """Perform backup operation.

        Args:
            progress_callback: Optional callback for progress updates

        Returns:
            Dictionary with backup statistics
        """
        self.stats["start_time"] = datetime.now()

        logger.info(f"Starting backup: {self.source} -> {self.destination}")

        # Check if source exists
        if not self.source.exists():
            raise FileNotFoundError(f"Source directory not found: {self.source}")

        # Check available disk space
        dest_stat = shutil.disk_usage(self.destination.parent)
        if dest_stat.free < self.stats["total_size"]:
            raise IOError("Insufficient disk space at destination")

        # Scan directory
        files_to_backup = self.scan_directory(progress_callback)

        # Backup files using thread pool
        verify_backup = config.get("backup.verify_backup", True)

        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            futures = {executor.submit(self.backup_file, file_path, verify_backup): file_path for file_path in files_to_backup}

            for future in as_completed(futures):
                file_path = futures[future]

                try:
                    result = future.result()

                    if result["success"]:
                        self.stats["backed_up_files"] += 1
                        self.stats["transferred_size"] += result["size"]
                    else:
                        self.stats["failed_files"] += 1

                    if progress_callback:
                        progress_callback(
                            {
                                "phase": "backing_up",
                                "current_file": result["path"],
                                "backed_up_files": self.stats["backed_up_files"],
                                "total_files": self.stats["total_files"],
                                "transferred_size": self.stats["transferred_size"],
                                "total_size": self.stats["total_size"],
                                "percentage": (self.stats["backed_up_files"] / self.stats["total_files"] * 100),
                            }
                        )

                except Exception as e:
                    self.stats["failed_files"] += 1
                    logger.error(f"Error processing {file_path}: {e}")

        self.stats["end_time"] = datetime.now()
        duration = (self.stats["end_time"] - self.stats["start_time"]).total_seconds()

        logger.info(f"Backup completed in {duration:.2f} seconds")
        logger.info(f"Files backed up: {self.stats['backed_up_files']}/{self.stats['total_files']}")
        logger.info(f"Failed files: {self.stats['failed_files']}")

        return self.stats

    def restore(self, restore_path: Path, progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """Restore backup to specified location.

        Args:
            restore_path: Path to restore backup to
            progress_callback: Optional callback for progress updates

        Returns:
            Dictionary with restore statistics
        """
        logger.info(f"Starting restore: {self.destination} -> {restore_path}")

        restore_stats = {
            "total_files": 0,
            "restored_files": 0,
            "failed_files": 0,
            "start_time": datetime.now(),
        }

        try:
            # Scan backup directory
            for root, dirs, files in os.walk(self.destination):
                root_path = Path(root)

                for file in files:
                    file_path = root_path / file
                    restore_stats["total_files"] += 1

                    try:
                        # Calculate relative path
                        rel_path = file_path.relative_to(self.destination)
                        dest_path = restore_path / rel_path

                        # Create destination directory
                        dest_path.parent.mkdir(parents=True, exist_ok=True)

                        # Copy file
                        shutil.copy2(file_path, dest_path)
                        restore_stats["restored_files"] += 1

                        if progress_callback:
                            progress_callback(
                                {
                                    "phase": "restoring",
                                    "current_file": str(file_path),
                                    "restored_files": restore_stats["restored_files"],
                                    "total_files": restore_stats["total_files"],
                                }
                            )

                    except Exception as e:
                        restore_stats["failed_files"] += 1
                        logger.error(f"Error restoring {file_path}: {e}")

            restore_stats["end_time"] = datetime.now()
            duration = (restore_stats["end_time"] - restore_stats["start_time"]).total_seconds()

            logger.info(f"Restore completed in {duration:.2f} seconds")
            logger.info(f"Files restored: {restore_stats['restored_files']}/{restore_stats['total_files']}")

            return restore_stats

        except Exception as e:
            logger.error(f"Error during restore: {e}")
            raise


class IncrementalBackup(BackupEngine):
    """Incremental backup engine - only backs up changed files."""

    def __init__(self, source: Path, destination: Path, manifest_file: Optional[Path] = None):
        """Initialize incremental backup engine.

        Args:
            source: Source directory to backup
            destination: Destination path for backup
            manifest_file: Path to manifest file for tracking changes
        """
        super().__init__(source, destination)
        self.manifest_file = manifest_file or (destination / ".nimbus_manifest")
        self.manifest = self._load_manifest()

    def _load_manifest(self) -> Dict[str, Dict[str, Any]]:
        """Load backup manifest from file.

        Returns:
            Manifest dictionary
        """
        if self.manifest_file.exists():
            try:
                import json

                with open(self.manifest_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading manifest: {e}")
        return {}

    def _save_manifest(self):
        """Save backup manifest to file."""
        try:
            import json

            self.manifest_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.manifest_file, "w") as f:
                json.dump(self.manifest, f, indent=2)
            logger.debug(f"Manifest saved to {self.manifest_file}")
        except Exception as e:
            logger.error(f"Error saving manifest: {e}")

    def file_needs_backup(self, file_path: Path) -> bool:
        """Check if file needs to be backed up.

        Args:
            file_path: Path to file

        Returns:
            True if file needs backup
        """
        rel_path = str(file_path.relative_to(self.source))

        # File not in manifest - needs backup
        if rel_path not in self.manifest:
            return True

        # Check modification time
        current_mtime = file_path.stat().st_mtime
        manifest_mtime = self.manifest[rel_path].get("mtime", 0)

        if current_mtime > manifest_mtime:
            return True

        # Check file size
        current_size = file_path.stat().st_size
        manifest_size = self.manifest[rel_path].get("size", 0)

        if current_size != manifest_size:
            return True

        return False

    def backup(self, progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """Perform incremental backup.

        Args:
            progress_callback: Optional callback for progress updates

        Returns:
            Dictionary with backup statistics
        """
        self.stats["start_time"] = datetime.now()

        logger.info(f"Starting incremental backup: {self.source} -> {self.destination}")

        # Scan directory
        all_files = self.scan_directory(progress_callback)

        # Filter files that need backup
        files_to_backup = [f for f in all_files if self.file_needs_backup(f)]

        logger.info(f"Incremental backup: {len(files_to_backup)}/{len(all_files)} files need backup")

        # Backup files
        verify_backup = config.get("backup.verify_backup", True)

        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            futures = {executor.submit(self.backup_file, file_path, verify_backup): file_path for file_path in files_to_backup}

            for future in as_completed(futures):
                file_path = futures[future]

                try:
                    result = future.result()

                    if result["success"]:
                        self.stats["backed_up_files"] += 1
                        self.stats["transferred_size"] += result["size"]

                        # Update manifest
                        rel_path = str(file_path.relative_to(self.source))
                        self.manifest[rel_path] = {
                            "mtime": file_path.stat().st_mtime,
                            "size": result["size"],
                            "checksum": result["checksum"],
                            "backup_time": datetime.now().isoformat(),
                        }
                    else:
                        self.stats["failed_files"] += 1

                    if progress_callback:
                        progress_callback(
                            {
                                "phase": "backing_up",
                                "current_file": result["path"],
                                "backed_up_files": self.stats["backed_up_files"],
                                "total_files": len(files_to_backup),
                                "transferred_size": self.stats["transferred_size"],
                            }
                        )

                except Exception as e:
                    self.stats["failed_files"] += 1
                    logger.error(f"Error processing {file_path}: {e}")

        # Save manifest
        self._save_manifest()

        self.stats["end_time"] = datetime.now()
        duration = (self.stats["end_time"] - self.stats["start_time"]).total_seconds()

        logger.info(f"Incremental backup completed in {duration:.2f} seconds")

        return self.stats
