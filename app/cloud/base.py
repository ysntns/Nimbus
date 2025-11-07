"""
Base Cloud Provider - Abstract base class for cloud storage providers

Defines the interface that all cloud providers must implement.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from loguru import logger


@dataclass
class CloudFile:
    """Represents a file in cloud storage."""

    id: str
    name: str
    path: str
    size: int
    modified: datetime
    checksum: Optional[str] = None
    mime_type: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class UploadResult:
    """Result of an upload operation."""

    success: bool
    file_id: Optional[str] = None
    file_path: Optional[str] = None
    size: int = 0
    error: Optional[str] = None


@dataclass
class DownloadResult:
    """Result of a download operation."""

    success: bool
    local_path: Optional[Path] = None
    size: int = 0
    error: Optional[str] = None


class CloudProvider(ABC):
    """Abstract base class for cloud storage providers."""

    def __init__(self, credentials: Dict[str, Any], config: Optional[Dict[str, Any]] = None):
        """Initialize cloud provider.

        Args:
            credentials: Provider credentials
            config: Optional configuration
        """
        self.credentials = credentials
        self.config = config or {}
        self.authenticated = False
        logger.info(f"Initialized {self.__class__.__name__}")

    @abstractmethod
    def authenticate(self) -> bool:
        """Authenticate with the cloud provider.

        Returns:
            True if authentication successful
        """
        pass

    @abstractmethod
    def upload_file(
        self,
        local_path: Path,
        remote_path: str,
        progress_callback: Optional[Callable] = None,
    ) -> UploadResult:
        """Upload a file to cloud storage.

        Args:
            local_path: Path to local file
            remote_path: Destination path in cloud storage
            progress_callback: Optional callback for progress updates

        Returns:
            UploadResult with operation details
        """
        pass

    @abstractmethod
    def download_file(
        self,
        remote_path: str,
        local_path: Path,
        progress_callback: Optional[Callable] = None,
    ) -> DownloadResult:
        """Download a file from cloud storage.

        Args:
            remote_path: Path in cloud storage
            local_path: Destination path on local filesystem
            progress_callback: Optional callback for progress updates

        Returns:
            DownloadResult with operation details
        """
        pass

    @abstractmethod
    def list_files(self, remote_path: str = "/") -> List[CloudFile]:
        """List files in cloud storage.

        Args:
            remote_path: Path to list (default: root)

        Returns:
            List of CloudFile objects
        """
        pass

    @abstractmethod
    def delete_file(self, remote_path: str) -> bool:
        """Delete a file from cloud storage.

        Args:
            remote_path: Path to file to delete

        Returns:
            True if deletion successful
        """
        pass

    @abstractmethod
    def create_folder(self, remote_path: str) -> bool:
        """Create a folder in cloud storage.

        Args:
            remote_path: Path to folder to create

        Returns:
            True if creation successful
        """
        pass

    @abstractmethod
    def get_file_info(self, remote_path: str) -> Optional[CloudFile]:
        """Get information about a file.

        Args:
            remote_path: Path to file

        Returns:
            CloudFile object or None if not found
        """
        pass

    @abstractmethod
    def get_quota_info(self) -> Dict[str, int]:
        """Get storage quota information.

        Returns:
            Dictionary with 'total', 'used', and 'available' in bytes
        """
        pass

    def file_exists(self, remote_path: str) -> bool:
        """Check if a file exists in cloud storage.

        Args:
            remote_path: Path to check

        Returns:
            True if file exists
        """
        return self.get_file_info(remote_path) is not None

    def get_provider_name(self) -> str:
        """Get the provider name.

        Returns:
            Provider name
        """
        return self.__class__.__name__


class CloudProviderFactory:
    """Factory for creating cloud provider instances."""

    _providers: Dict[str, type] = {}

    @classmethod
    def register_provider(cls, name: str, provider_class: type):
        """Register a cloud provider.

        Args:
            name: Provider name
            provider_class: Provider class
        """
        cls._providers[name.lower()] = provider_class
        logger.info(f"Registered cloud provider: {name}")

    @classmethod
    def create_provider(
        cls,
        provider_name: str,
        credentials: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None,
    ) -> CloudProvider:
        """Create a cloud provider instance.

        Args:
            provider_name: Name of provider
            credentials: Provider credentials
            config: Optional configuration

        Returns:
            CloudProvider instance

        Raises:
            ValueError: If provider not found
        """
        provider_class = cls._providers.get(provider_name.lower())

        if not provider_class:
            raise ValueError(f"Unknown cloud provider: {provider_name}")

        return provider_class(credentials, config)

    @classmethod
    def list_providers(cls) -> List[str]:
        """List all registered providers.

        Returns:
            List of provider names
        """
        return list(cls._providers.keys())
