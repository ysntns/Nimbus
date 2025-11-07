"""
Helper Utilities - Common utility functions

Provides various helper functions for file operations, formatting, etc.
"""

import os
import re
from pathlib import Path
from typing import Union, Optional
from datetime import datetime, timedelta


def format_size(size_bytes: int) -> str:
    """Format bytes to human-readable size.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted size string (e.g., "1.5 GB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def parse_size(size_str: str) -> int:
    """Parse size string to bytes.

    Args:
        size_str: Size string (e.g., "1.5GB", "100MB")

    Returns:
        Size in bytes
    """
    size_str = size_str.strip().upper()

    # Extract number and unit
    match = re.match(r'^([\d.]+)\s*([KMGT]?B?)$', size_str)

    if not match:
        raise ValueError(f"Invalid size format: {size_str}")

    value = float(match.group(1))
    unit = match.group(2) or 'B'

    multipliers = {
        'B': 1,
        'KB': 1024,
        'MB': 1024 ** 2,
        'GB': 1024 ** 3,
        'TB': 1024 ** 4,
    }

    return int(value * multipliers.get(unit, 1))


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human-readable string.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted duration (e.g., "1h 30m 45s")
    """
    if seconds < 60:
        return f"{seconds:.1f}s"

    minutes = int(seconds // 60)
    seconds = int(seconds % 60)

    if minutes < 60:
        return f"{minutes}m {seconds}s"

    hours = minutes // 60
    minutes = minutes % 60

    return f"{hours}h {minutes}m {seconds}s"


def format_datetime(dt: datetime, format: str = '%Y-%m-%d %H:%M:%S') -> str:
    """Format datetime to string.

    Args:
        dt: Datetime object
        format: Format string

    Returns:
        Formatted datetime string
    """
    return dt.strftime(format)


def format_relative_time(dt: datetime) -> str:
    """Format datetime as relative time (e.g., "2 hours ago").

    Args:
        dt: Datetime object

    Returns:
        Relative time string
    """
    now = datetime.now()
    diff = now - dt

    if diff.total_seconds() < 60:
        return "just now"
    elif diff.total_seconds() < 3600:
        minutes = int(diff.total_seconds() // 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif diff.total_seconds() < 86400:
        hours = int(diff.total_seconds() // 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff.days < 30:
        return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
    elif diff.days < 365:
        months = diff.days // 30
        return f"{months} month{'s' if months != 1 else ''} ago"
    else:
        years = diff.days // 365
        return f"{years} year{'s' if years != 1 else ''} ago"


def safe_filename(filename: str) -> str:
    """Convert string to safe filename.

    Args:
        filename: Original filename

    Returns:
        Safe filename
    """
    # Remove invalid characters
    safe = re.sub(r'[<>:"/\\|?*]', '_', filename)

    # Remove control characters
    safe = ''.join(char for char in safe if ord(char) >= 32)

    # Limit length
    if len(safe) > 255:
        name, ext = os.path.splitext(safe)
        safe = name[:255 - len(ext)] + ext

    return safe


def ensure_directory(path: Union[str, Path]) -> Path:
    """Ensure directory exists, create if not.

    Args:
        path: Directory path

    Returns:
        Path object
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def is_path_safe(path: Union[str, Path], base_path: Union[str, Path]) -> bool:
    """Check if path is within base path (prevent path traversal).

    Args:
        path: Path to check
        base_path: Base directory path

    Returns:
        True if path is safe
    """
    try:
        path = Path(path).resolve()
        base_path = Path(base_path).resolve()
        # Python 3.8 compatible version (is_relative_to is 3.9+)
        try:
            path.relative_to(base_path)
            return True
        except ValueError:
            return False
    except (ValueError, RuntimeError):
        return False


def get_file_count(directory: Union[str, Path], recursive: bool = True) -> int:
    """Count files in directory.

    Args:
        directory: Directory path
        recursive: Count recursively

    Returns:
        Number of files
    """
    directory = Path(directory)
    count = 0

    if recursive:
        for item in directory.rglob('*'):
            if item.is_file():
                count += 1
    else:
        for item in directory.iterdir():
            if item.is_file():
                count += 1

    return count


def get_directory_size(directory: Union[str, Path]) -> int:
    """Calculate total size of directory.

    Args:
        directory: Directory path

    Returns:
        Total size in bytes
    """
    directory = Path(directory)
    total_size = 0

    for item in directory.rglob('*'):
        if item.is_file():
            total_size += item.stat().st_size

    return total_size


def generate_backup_name(source: str, timestamp: Optional[datetime] = None) -> str:
    """Generate backup name from source path.

    Args:
        source: Source path
        timestamp: Timestamp (default: now)

    Returns:
        Backup name
    """
    if timestamp is None:
        timestamp = datetime.now()

    source_name = Path(source).name
    timestamp_str = timestamp.strftime('%Y%m%d_%H%M%S')

    return f"{source_name}_{timestamp_str}"


def validate_email(email: str) -> bool:
    """Validate email address.

    Args:
        email: Email address

    Returns:
        True if valid
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def truncate_string(text: str, max_length: int = 100, suffix: str = '...') -> str:
    """Truncate string to maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix


def calculate_checksum_quick(file_path: Path, algorithm: str = 'md5') -> str:
    """Calculate quick checksum of file (first and last chunks).

    Args:
        file_path: Path to file
        algorithm: Hash algorithm

    Returns:
        Checksum hex string
    """
    import hashlib

    hash_obj = hashlib.new(algorithm)
    file_size = file_path.stat().st_size

    chunk_size = 8192

    with open(file_path, 'rb') as f:
        # Read first chunk
        hash_obj.update(f.read(chunk_size))

        # Read last chunk if file is large enough
        if file_size > chunk_size * 2:
            f.seek(-chunk_size, os.SEEK_END)
            hash_obj.update(f.read(chunk_size))

    return hash_obj.hexdigest()
