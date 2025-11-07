"""
AWS S3 Provider - Cloud storage integration for Amazon S3

Implements backup to AWS S3 using boto3.
"""

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
    import boto3

    AWS_S3_AVAILABLE = True
except ImportError:
    AWS_S3_AVAILABLE = False
    logger.warning("AWS S3 not available - install with: pip install boto3")


class AWSS3Provider(CloudProvider):
    """AWS S3 cloud storage provider."""

    def __init__(
        self, credentials: Dict[str, Any], config: Optional[Dict[str, Any]] = None
    ):
        """Initialize AWS S3 provider.

        Args:
            credentials: AWS credentials (access_key_id, secret_access_key, region)
            config: Optional configuration (bucket_name, etc.)
        """
        if not AWS_S3_AVAILABLE:
            raise ImportError("boto3 not available")

        super().__init__(credentials, config)
        self.s3_client = None
        self.bucket_name = config.get("bucket_name") if config else None

    def authenticate(self) -> bool:
        """Authenticate with AWS S3.

        Returns:
            True if authentication successful
        """
        try:
            self.s3_client = boto3.client(
                "s3",
                aws_access_key_id=self.credentials.get("access_key_id"),
                aws_secret_access_key=self.credentials.get("secret_access_key"),
                region_name=self.credentials.get("region", "us-east-1"),
            )

            # Test connection
            self.s3_client.list_buckets()
            self.authenticated = True

            logger.info("Successfully authenticated with AWS S3")
            return True

        except Exception as e:
            logger.error(f"AWS S3 authentication failed: {e}")
            return False

    def upload_file(
        self,
        local_path: Path,
        remote_path: str,
        progress_callback: Optional[Callable] = None,
    ) -> UploadResult:
        """Upload a file to S3.

        Args:
            local_path: Path to local file
            remote_path: S3 key (path)
            progress_callback: Optional callback for progress updates

        Returns:
            UploadResult with operation details
        """
        if not self.authenticated or not self.bucket_name:
            return UploadResult(
                success=False, error="Not authenticated or bucket not set"
            )

        try:
            file_size = local_path.stat().st_size

            self.s3_client.upload_file(str(local_path), self.bucket_name, remote_path)

            logger.info(
                f"Uploaded {local_path.name} to S3: s3://{self.bucket_name}/{remote_path}"
            )

            return UploadResult(
                success=True,
                file_id=remote_path,
                file_path=f"s3://{self.bucket_name}/{remote_path}",
                size=file_size,
            )

        except Exception as e:
            logger.error(f"Upload to S3 failed: {e}")
            return UploadResult(success=False, error=str(e))

    def download_file(
        self,
        remote_path: str,
        local_path: Path,
        progress_callback: Optional[Callable] = None,
    ) -> DownloadResult:
        """Download a file from S3.

        Args:
            remote_path: S3 key (path)
            local_path: Destination path on local filesystem
            progress_callback: Optional callback for progress updates

        Returns:
            DownloadResult with operation details
        """
        if not self.authenticated or not self.bucket_name:
            return DownloadResult(
                success=False, error="Not authenticated or bucket not set"
            )

        try:
            local_path.parent.mkdir(parents=True, exist_ok=True)

            self.s3_client.download_file(self.bucket_name, remote_path, str(local_path))

            file_size = local_path.stat().st_size

            logger.info(f"Downloaded from S3: s3://{self.bucket_name}/{remote_path}")

            return DownloadResult(success=True, local_path=local_path, size=file_size)

        except Exception as e:
            logger.error(f"Download from S3 failed: {e}")
            return DownloadResult(success=False, error=str(e))

    def list_files(self, remote_path: str = "/") -> List[CloudFile]:
        """List files in S3.

        Args:
            remote_path: Prefix to filter by

        Returns:
            List of CloudFile objects
        """
        if not self.authenticated or not self.bucket_name:
            return []

        try:
            prefix = remote_path.lstrip("/")

            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name, Prefix=prefix
            )

            cloud_files = []
            for obj in response.get("Contents", []):
                cloud_files.append(
                    CloudFile(
                        id=obj["Key"],
                        name=obj["Key"].split("/")[-1],
                        path=obj["Key"],
                        size=obj["Size"],
                        modified=obj["LastModified"],
                        checksum=obj.get("ETag", "").strip('"'),
                    )
                )

            logger.debug(f"Listed {len(cloud_files)} files from S3")
            return cloud_files

        except Exception as e:
            logger.error(f"Failed to list S3 files: {e}")
            return []

    def delete_file(self, remote_path: str) -> bool:
        """Delete a file from S3.

        Args:
            remote_path: S3 key to delete

        Returns:
            True if deletion successful
        """
        if not self.authenticated or not self.bucket_name:
            return False

        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=remote_path)
            logger.info(f"Deleted from S3: s3://{self.bucket_name}/{remote_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete from S3: {e}")
            return False

    def create_folder(self, remote_path: str) -> bool:
        """Create a folder in S3 (S3 doesn't have real folders, creates empty object).

        Args:
            remote_path: Folder path

        Returns:
            True if creation successful
        """
        if not self.authenticated or not self.bucket_name:
            return False

        try:
            folder_key = remote_path.rstrip("/") + "/"

            self.s3_client.put_object(Bucket=self.bucket_name, Key=folder_key)

            logger.info(f"Created folder in S3: s3://{self.bucket_name}/{folder_key}")
            return True

        except Exception as e:
            logger.error(f"Failed to create folder in S3: {e}")
            return False

    def get_file_info(self, remote_path: str) -> Optional[CloudFile]:
        """Get information about a file in S3.

        Args:
            remote_path: S3 key

        Returns:
            CloudFile object or None if not found
        """
        if not self.authenticated or not self.bucket_name:
            return None

        try:
            response = self.s3_client.head_object(
                Bucket=self.bucket_name, Key=remote_path
            )

            return CloudFile(
                id=remote_path,
                name=remote_path.split("/")[-1],
                path=remote_path,
                size=response["ContentLength"],
                modified=response["LastModified"],
                checksum=response.get("ETag", "").strip('"'),
                mime_type=response.get("ContentType"),
            )

        except Exception as e:
            logger.error(f"Failed to get file info from S3: {e}")
            return None

    def get_quota_info(self) -> Dict[str, int]:
        """Get storage quota information (S3 has no quota limit).

        Returns:
            Dictionary with storage info
        """
        if not self.authenticated or not self.bucket_name:
            return {"total": 0, "used": 0, "available": 0}

        try:
            # Calculate total size of objects in bucket
            response = self.s3_client.list_objects_v2(Bucket=self.bucket_name)
            used = sum(obj["Size"] for obj in response.get("Contents", []))

            # S3 has effectively unlimited storage
            return {
                "total": -1,  # Unlimited
                "used": used,
                "available": -1,  # Unlimited
            }

        except Exception as e:
            logger.error(f"Failed to get quota info from S3: {e}")
            return {"total": 0, "used": 0, "available": 0}


# Register provider
if AWS_S3_AVAILABLE:
    CloudProviderFactory.register_provider("aws_s3", AWSS3Provider)
    CloudProviderFactory.register_provider("s3", AWSS3Provider)
