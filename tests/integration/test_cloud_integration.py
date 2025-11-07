"""
Integration tests for cloud providers.
"""

import pytest


def test_cloud_provider_factory():
    """Test cloud provider factory."""
    from app.cloud.base import CloudProviderFactory

    # Test listing providers
    providers = CloudProviderFactory.list_providers()
    assert isinstance(providers, list)


def test_google_drive_import():
    """Test Google Drive provider import."""
    try:
        from app.cloud.google_drive import GoogleDriveProvider

        assert GoogleDriveProvider is not None
    except ImportError:
        pytest.skip("Google Drive dependencies not installed")


def test_aws_s3_import():
    """Test AWS S3 provider import."""
    try:
        from app.cloud.aws_s3 import AWSS3Provider

        assert AWSS3Provider is not None
    except ImportError:
        pytest.skip("AWS S3 dependencies not installed")
