"""
Core modules for Nimbus backup engine.

This package contains the core backup engine, configuration manager,
and essential backup functionality.
"""

from app.core.backup import BackupEngine, IncrementalBackup
from app.core.config import ConfigManager, config

__all__ = [
    "BackupEngine",
    "IncrementalBackup",
    "ConfigManager",
    "config",
]
