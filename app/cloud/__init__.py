"""
Cloud storage providers integration.

Support for Google Drive, Dropbox, OneDrive, AWS S3, and other
cloud storage services.
"""

from app.cloud.base import CloudFile, CloudProvider, CloudProviderFactory, DownloadResult, UploadResult

__all__ = [
    "CloudProvider",
    "CloudFile",
    "UploadResult",
    "DownloadResult",
    "CloudProviderFactory",
]

# Import providers (will auto-register if dependencies available)
try:
    from app.cloud import google_drive  # noqa: F401
except Exception:
    pass

try:
    from app.cloud import aws_s3  # noqa: F401
except Exception:
    pass
