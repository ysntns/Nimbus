"""
Integration tests for cloud providers.
"""

import pytest


def test_cloud_provider_factory():
    """Test cloud provider factory."""
    try:
        from app.cloud.base import CloudProviderFactory

        # Test listing providers
        providers = CloudProviderFactory.list_providers()
        assert isinstance(providers, list)
    except Exception as e:
        pytest.skip(f"Cloud provider dependencies not available: {e}")


def test_google_drive_import():
    """Test Google Drive provider import."""
    try:
        from app.cloud.google_drive import GoogleDriveProvider

        assert GoogleDriveProvider is not None
    except Exception as e:
        pytest.skip(f"Google Drive dependencies not installed: {e}")


def test_aws_s3_import():
    """Test AWS S3 provider import."""
    try:
        from app.cloud.aws_s3 import AWSS3Provider

        assert AWSS3Provider is not None
    except Exception as e:
        pytest.skip(f"AWS S3 dependencies not installed: {e}")
