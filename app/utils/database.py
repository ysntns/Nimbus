"""
Database Module - SQLite database for backup history tracking

Stores backup metadata, history, and statistics.
"""

import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from loguru import logger


@dataclass
class BackupRecord:
    """Represents a backup operation record."""

    id: Optional[int] = None
    source: str = ""
    destination: str = ""
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: str = "pending"  # pending, running, completed, failed
    backup_type: str = "full"  # full, incremental
    total_files: int = 0
    backed_up_files: int = 0
    failed_files: int = 0
    skipped_files: int = 0
    total_size: int = 0
    transferred_size: int = 0
    duration_seconds: float = 0.0
    error_message: Optional[str] = None
    encrypted: bool = False
    compressed: bool = False
    cloud_provider: Optional[str] = None


class BackupDatabase:
    """Manages backup history database."""

    def __init__(self, db_path: Optional[Path] = None):
        """Initialize database connection.

        Args:
            db_path: Path to database file (default: ~/.config/nimbus/backups.db)
        """
        if db_path is None:
            db_path = Path.home() / ".config" / "nimbus" / "backups.db"

        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.conn: Optional[sqlite3.Connection] = None
        self._init_database()

        logger.info(f"Backup database initialized: {self.db_path}")

    def _init_database(self):
        """Initialize database schema."""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row

        cursor = self.conn.cursor()

        # Create backups table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS backups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                destination TEXT NOT NULL,
                started_at TEXT,
                completed_at TEXT,
                status TEXT NOT NULL,
                backup_type TEXT,
                total_files INTEGER,
                backed_up_files INTEGER,
                failed_files INTEGER,
                skipped_files INTEGER,
                total_size INTEGER,
                transferred_size INTEGER,
                duration_seconds REAL,
                error_message TEXT,
                encrypted BOOLEAN,
                compressed BOOLEAN,
                cloud_provider TEXT
            )
        """
        )

        # Create index on status and started_at
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_backups_status
            ON backups(status)
        """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_backups_started_at
            ON backups(started_at DESC)
        """
        )

        self.conn.commit()

        logger.debug("Database schema initialized")

    def add_backup_record(self, record: BackupRecord) -> int:
        """Add a backup record to database.

        Args:
            record: BackupRecord to add

        Returns:
            ID of inserted record
        """
        cursor = self.conn.cursor()

        cursor.execute(
            """
            INSERT INTO backups (
                source, destination, started_at, completed_at, status,
                backup_type, total_files, backed_up_files, failed_files,
                skipped_files, total_size, transferred_size, duration_seconds,
                error_message, encrypted, compressed, cloud_provider
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                record.source,
                record.destination,
                record.started_at.isoformat() if record.started_at else None,
                record.completed_at.isoformat() if record.completed_at else None,
                record.status,
                record.backup_type,
                record.total_files,
                record.backed_up_files,
                record.failed_files,
                record.skipped_files,
                record.total_size,
                record.transferred_size,
                record.duration_seconds,
                record.error_message,
                record.encrypted,
                record.compressed,
                record.cloud_provider,
            ),
        )

        self.conn.commit()

        record_id = cursor.lastrowid
        logger.debug(f"Added backup record: ID={record_id}")

        return record_id

    def update_backup_record(self, record: BackupRecord):
        """Update an existing backup record.

        Args:
            record: BackupRecord with updated data
        """
        if record.id is None:
            raise ValueError("Record ID is required for update")

        cursor = self.conn.cursor()

        cursor.execute(
            """
            UPDATE backups SET
                source = ?, destination = ?, started_at = ?, completed_at = ?,
                status = ?, backup_type = ?, total_files = ?, backed_up_files = ?,
                failed_files = ?, skipped_files = ?, total_size = ?, transferred_size = ?,
                duration_seconds = ?, error_message = ?, encrypted = ?, compressed = ?,
                cloud_provider = ?
            WHERE id = ?
        """,
            (
                record.source,
                record.destination,
                record.started_at.isoformat() if record.started_at else None,
                record.completed_at.isoformat() if record.completed_at else None,
                record.status,
                record.backup_type,
                record.total_files,
                record.backed_up_files,
                record.failed_files,
                record.skipped_files,
                record.total_size,
                record.transferred_size,
                record.duration_seconds,
                record.error_message,
                record.encrypted,
                record.compressed,
                record.cloud_provider,
                record.id,
            ),
        )

        self.conn.commit()

        logger.debug(f"Updated backup record: ID={record.id}")

    def get_backup_record(self, record_id: int) -> Optional[BackupRecord]:
        """Get a backup record by ID.

        Args:
            record_id: Record ID

        Returns:
            BackupRecord or None if not found
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM backups WHERE id = ?", (record_id,))

        row = cursor.fetchone()

        if row:
            return self._row_to_record(row)
        else:
            return None

    def list_backup_records(self, limit: int = 100, offset: int = 0, status: Optional[str] = None) -> List[BackupRecord]:
        """List backup records.

        Args:
            limit: Maximum number of records to return
            offset: Number of records to skip
            status: Filter by status (optional)

        Returns:
            List of BackupRecord objects
        """
        cursor = self.conn.cursor()

        if status:
            cursor.execute(
                """
                SELECT * FROM backups
                WHERE status = ?
                ORDER BY started_at DESC
                LIMIT ? OFFSET ?
            """,
                (status, limit, offset),
            )
        else:
            cursor.execute(
                """
                SELECT * FROM backups
                ORDER BY started_at DESC
                LIMIT ? OFFSET ?
            """,
                (limit, offset),
            )

        rows = cursor.fetchall()

        return [self._row_to_record(row) for row in rows]

    def get_statistics(self) -> Dict[str, Any]:
        """Get backup statistics.

        Returns:
            Dictionary with statistics
        """
        cursor = self.conn.cursor()

        stats = {}

        # Total backups
        cursor.execute("SELECT COUNT(*) as count FROM backups")
        stats["total_backups"] = cursor.fetchone()["count"]

        # Backups by status
        cursor.execute("SELECT status, COUNT(*) as count FROM backups GROUP BY status")
        stats["by_status"] = {row["status"]: row["count"] for row in cursor.fetchall()}

        # Total data transferred
        cursor.execute('SELECT SUM(transferred_size) as total FROM backups WHERE status = "completed"')
        result = cursor.fetchone()
        stats["total_transferred"] = result["total"] or 0

        # Average duration
        cursor.execute('SELECT AVG(duration_seconds) as avg FROM backups WHERE status = "completed"')
        result = cursor.fetchone()
        stats["avg_duration_seconds"] = result["avg"] or 0

        # Recent backups
        cursor.execute(
            """
            SELECT * FROM backups
            ORDER BY started_at DESC
            LIMIT 10
        """
        )
        stats["recent_backups"] = [self._row_to_record(row) for row in cursor.fetchall()]

        return stats

    def delete_old_records(self, days: int = 90) -> int:
        """Delete backup records older than specified days.

        Args:
            days: Number of days to keep

        Returns:
            Number of deleted records
        """
        cursor = self.conn.cursor()

        cutoff_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        cutoff_date = cutoff_date.replace(day=cutoff_date.day - days)

        cursor.execute(
            """
            DELETE FROM backups
            WHERE started_at < ?
        """,
            (cutoff_date.isoformat(),),
        )

        deleted_count = cursor.rowcount
        self.conn.commit()

        logger.info(f"Deleted {deleted_count} old backup records")

        return deleted_count

    def _row_to_record(self, row: sqlite3.Row) -> BackupRecord:
        """Convert database row to BackupRecord.

        Args:
            row: Database row

        Returns:
            BackupRecord object
        """
        return BackupRecord(
            id=row["id"],
            source=row["source"],
            destination=row["destination"],
            started_at=(datetime.fromisoformat(row["started_at"]) if row["started_at"] else None),
            completed_at=(datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None),
            status=row["status"],
            backup_type=row["backup_type"],
            total_files=row["total_files"],
            backed_up_files=row["backed_up_files"],
            failed_files=row["failed_files"],
            skipped_files=row["skipped_files"],
            total_size=row["total_size"],
            transferred_size=row["transferred_size"],
            duration_seconds=row["duration_seconds"],
            error_message=row["error_message"],
            encrypted=bool(row["encrypted"]),
            compressed=bool(row["compressed"]),
            cloud_provider=row["cloud_provider"],
        )

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.debug("Database connection closed")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
