"""
Google Drive Provider - Cloud storage integration for Google Drive

Implements backup to Google Drive using Google Drive API v3.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from loguru import logger

from app.cloud.base import (
    CloudFile,
    CloudProvider,
    CloudProviderFactory,
    DownloadResult,
    UploadResult,
)

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

    GOOGLE_DRIVE_AVAILABLE = True
except ImportError:
    GOOGLE_DRIVE_AVAILABLE = False
    logger.warning(
        "Google Drive API not available - install with: pip install google-api-python-client google-auth-oauthlib"
    )


class GoogleDriveProvider(CloudProvider):
    """Google Drive cloud storage provider."""

    # OAuth 2.0 scopes
    SCOPES = ["https://www.googleapis.com/auth/drive.file"]

    def __init__(
        self, credentials: Dict[str, Any], config: Optional[Dict[str, Any]] = None
    ):
        """Initialize Google Drive provider.

        Args:
            credentials: Google Drive credentials (client_id, client_secret, etc.)
            config: Optional configuration
        """
        if not GOOGLE_DRIVE_AVAILABLE:
            raise ImportError("Google Drive API not available")

        super().__init__(credentials, config)
        self.service = None
        self.folder_id = config.get("folder_id") if config else None

    def authenticate(self) -> bool:
        """Authenticate with Google Drive.

        Returns:
            True if authentication successful
        """
        try:
            creds = None

            # Load credentials from token file if exists
            token_file = self.credentials.get("token_file")
            if token_file and Path(token_file).exists():
                creds = Credentials.from_authorized_user_file(token_file, self.SCOPES)

            # If no valid credentials, do OAuth flow
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials["credentials_file"], self.SCOPES
                    )
                    creds = flow.run_local_server(port=0)

                # Save credentials for next time
                if token_file:
                    with open(token_file, "w") as token:
                        token.write(creds.to_json())

            # Build service
            self.service = build("drive", "v3", credentials=creds)
            self.authenticated = True

            logger.info("Successfully authenticated with Google Drive")
            return True

        except Exception as e:
            logger.error(f"Google Drive authentication failed: {e}")
            return False

    def upload_file(
        self,
        local_path: Path,
        remote_path: str,
        progress_callback: Optional[Callable] = None,
    ) -> UploadResult:
        """Upload a file to Google Drive.

        Args:
            local_path: Path to local file
            remote_path: Destination path in Google Drive
            progress_callback: Optional callback for progress updates

        Returns:
            UploadResult with operation details
        """
        if not self.authenticated:
            return UploadResult(success=False, error="Not authenticated")

        try:
            # File metadata
            file_metadata = {
                "name": local_path.name,
                "parents": [self.folder_id] if self.folder_id else [],
            }

            # Create media upload
            media = MediaFileUpload(
                str(local_path), resumable=True, chunksize=1024 * 1024  # 1MB chunks
            )

            # Upload file
            file = (
                self.service.files()
                .create(body=file_metadata, media_body=media, fields="id,name,size")
                .execute()
            )

            file_size = local_path.stat().st_size

            logger.info(
                f"Uploaded {local_path.name} to Google Drive (ID: {file.get('id')})"
            )

            return UploadResult(
                success=True,
                file_id=file.get("id"),
                file_path=remote_path,
                size=file_size,
            )

        except Exception as e:
            logger.error(f"Upload to Google Drive failed: {e}")
            return UploadResult(success=False, error=str(e))

    def download_file(
        self,
        remote_path: str,
        local_path: Path,
        progress_callback: Optional[Callable] = None,
    ) -> DownloadResult:
        """Download a file from Google Drive.

        Args:
            remote_path: File ID in Google Drive
            local_path: Destination path on local filesystem
            progress_callback: Optional callback for progress updates

        Returns:
            DownloadResult with operation details
        """
        if not self.authenticated:
            return DownloadResult(success=False, error="Not authenticated")

        try:
            # Get file metadata
            file_metadata = self.service.files().get(fileId=remote_path).execute()

            # Download file
            request = self.service.files().get_media(fileId=remote_path)
            local_path.parent.mkdir(parents=True, exist_ok=True)

            with open(local_path, "wb") as fh:
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                    if progress_callback and status:
                        progress_callback({"progress": status.progress() * 100})

            file_size = local_path.stat().st_size

            logger.info(f"Downloaded {file_metadata['name']} from Google Drive")

            return DownloadResult(success=True, local_path=local_path, size=file_size)

        except Exception as e:
            logger.error(f"Download from Google Drive failed: {e}")
            return DownloadResult(success=False, error=str(e))

    def list_files(self, remote_path: str = "/") -> List[CloudFile]:
        """List files in Google Drive.

        Args:
            remote_path: Folder ID (default: root)

        Returns:
            List of CloudFile objects
        """
        if not self.authenticated:
            return []

        try:
            query = (
                f"'{self.folder_id}' in parents" if self.folder_id else "trashed=false"
            )

            results = (
                self.service.files()
                .list(
                    q=query,
                    pageSize=1000,
                    fields="files(id, name, size, modifiedTime, mimeType, md5Checksum)",
                )
                .execute()
            )

            files = results.get("files", [])

            cloud_files = []
            for file in files:
                cloud_files.append(
                    CloudFile(
                        id=file["id"],
                        name=file["name"],
                        path=file["id"],
                        size=int(file.get("size", 0)),
                        modified=datetime.fromisoformat(
                            file["modifiedTime"].replace("Z", "+00:00")
                        ),
                        checksum=file.get("md5Checksum"),
                        mime_type=file.get("mimeType"),
                    )
                )

            logger.debug(f"Listed {len(cloud_files)} files from Google Drive")
            return cloud_files

        except Exception as e:
            logger.error(f"Failed to list Google Drive files: {e}")
            return []

    def delete_file(self, remote_path: str) -> bool:
        """Delete a file from Google Drive.

        Args:
            remote_path: File ID to delete

        Returns:
            True if deletion successful
        """
        if not self.authenticated:
            return False

        try:
            self.service.files().delete(fileId=remote_path).execute()
            logger.info(f"Deleted file from Google Drive (ID: {remote_path})")
            return True

        except Exception as e:
            logger.error(f"Failed to delete file from Google Drive: {e}")
            return False

    def create_folder(self, remote_path: str) -> bool:
        """Create a folder in Google Drive.

        Args:
            remote_path: Folder name

        Returns:
            True if creation successful
        """
        if not self.authenticated:
            return False

        try:
            file_metadata = {
                "name": remote_path,
                "mimeType": "application/vnd.google-apps.folder",
                "parents": [self.folder_id] if self.folder_id else [],
            }

            folder = (
                self.service.files().create(body=file_metadata, fields="id").execute()
            )

            logger.info(f"Created folder in Google Drive (ID: {folder.get('id')})")
            return True

        except Exception as e:
            logger.error(f"Failed to create folder in Google Drive: {e}")
            return False

    def get_file_info(self, remote_path: str) -> Optional[CloudFile]:
        """Get information about a file.

        Args:
            remote_path: File ID

        Returns:
            CloudFile object or None if not found
        """
        if not self.authenticated:
            return None

        try:
            file = (
                self.service.files()
                .get(
                    fileId=remote_path,
                    fields="id, name, size, modifiedTime, mimeType, md5Checksum",
                )
                .execute()
            )

            return CloudFile(
                id=file["id"],
                name=file["name"],
                path=file["id"],
                size=int(file.get("size", 0)),
                modified=datetime.fromisoformat(
                    file["modifiedTime"].replace("Z", "+00:00")
                ),
                checksum=file.get("md5Checksum"),
                mime_type=file.get("mimeType"),
            )

        except Exception as e:
            logger.error(f"Failed to get file info from Google Drive: {e}")
            return None

    def get_quota_info(self) -> Dict[str, int]:
        """Get storage quota information.

        Returns:
            Dictionary with 'total', 'used', and 'available' in bytes
        """
        if not self.authenticated:
            return {"total": 0, "used": 0, "available": 0}

        try:
            about = self.service.about().get(fields="storageQuota").execute()
            quota = about["storageQuota"]

            total = int(quota.get("limit", 0))
            used = int(quota.get("usage", 0))
            available = total - used

            return {"total": total, "used": used, "available": available}

        except Exception as e:
            logger.error(f"Failed to get quota info from Google Drive: {e}")
            return {"total": 0, "used": 0, "available": 0}


# Register provider
if GOOGLE_DRIVE_AVAILABLE:
    CloudProviderFactory.register_provider("google_drive", GoogleDriveProvider)
    CloudProviderFactory.register_provider("gdrive", GoogleDriveProvider)
