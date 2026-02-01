import pytest
from unittest.mock import MagicMock, patch, call
from pathlib import Path
import sys

# Import the module
import app.cloud.google_drive

# Monkeypatch the module if dependencies were missing during import
if not hasattr(app.cloud.google_drive, "build"):
    app.cloud.google_drive.build = MagicMock()
if not hasattr(app.cloud.google_drive, "MediaFileUpload"):
    app.cloud.google_drive.MediaFileUpload = MagicMock()
if not hasattr(app.cloud.google_drive, "MediaIoBaseDownload"):
    app.cloud.google_drive.MediaIoBaseDownload = MagicMock()
if not hasattr(app.cloud.google_drive, "Credentials"):
    app.cloud.google_drive.Credentials = MagicMock()
if not hasattr(app.cloud.google_drive, "InstalledAppFlow"):
    app.cloud.google_drive.InstalledAppFlow = MagicMock()
if not hasattr(app.cloud.google_drive, "Request"):
    app.cloud.google_drive.Request = MagicMock()

from app.cloud.google_drive import GoogleDriveProvider

@pytest.fixture
def mock_drive_service():
    with patch("app.cloud.google_drive.build") as mock_build:
        service = MagicMock()
        mock_build.return_value = service
        yield service

@pytest.fixture
def provider(mock_drive_service):
    with patch("app.cloud.google_drive.GOOGLE_DRIVE_AVAILABLE", True):
        # Mock credentials and config
        creds = {"client_id": "test", "client_secret": "test"}
        config = {"folder_id": "root_id"}

        provider = GoogleDriveProvider(creds, config)
        provider.service = mock_drive_service
        provider.authenticated = True
        return provider

def test_find_folder_in_cache(provider):
    provider.folder_cache[("root_id", "cached_folder")] = "cached_id"

    folder_id = provider._find_folder("cached_folder", "root_id")

    assert folder_id == "cached_id"
    # Service should not be called if in cache
    provider.service.files.assert_not_called()

def test_find_folder_api_hit_found(provider):
    # Setup mock response
    mock_files = provider.service.files.return_value
    mock_list = mock_files.list.return_value
    mock_execute = mock_list.execute.return_value
    mock_execute.get.return_value = [{"id": "found_id", "name": "folder_name"}]

    folder_id = provider._find_folder("folder_name", "root_id")

    assert folder_id == "found_id"
    provider.service.files().list.assert_called_with(
        q="name = 'folder_name' and mimeType = 'application/vnd.google-apps.folder' and trashed = false and 'root_id' in parents",
        spaces="drive",
        fields="files(id, name)",
        pageSize=1
    )
    # Check if cached
    assert provider.folder_cache[("root_id", "folder_name")] == "found_id"

def test_find_folder_api_hit_not_found(provider):
    mock_files = provider.service.files.return_value
    mock_list = mock_files.list.return_value
    mock_execute = mock_list.execute.return_value
    mock_execute.get.return_value = []

    folder_id = provider._find_folder("missing_folder", "root_id")

    assert folder_id is None

def test_create_folder_in_parent(provider):
    mock_files = provider.service.files.return_value
    mock_create = mock_files.create.return_value
    mock_execute = mock_create.execute.return_value
    mock_execute.get.return_value = "new_folder_id"

    folder_id = provider._create_folder_in_parent("new_folder", "root_id")

    assert folder_id == "new_folder_id"
    provider.service.files().create.assert_called_with(
        body={
            "name": "new_folder",
            "mimeType": "application/vnd.google-apps.folder",
            "parents": ["root_id"]
        },
        fields="id"
    )
    assert provider.folder_cache[("root_id", "new_folder")] == "new_folder_id"

def test_get_or_create_folder_nested(provider):
    # Scenario: Create structure "sub/nested"
    # "sub" exists (id: sub_id)
    # "nested" does not exist -> create (id: nested_id)

    with patch.object(provider, '_find_folder') as mock_find, \
         patch.object(provider, '_create_folder_in_parent') as mock_create:

        # Call 1: find "sub" in "root_id" -> returns "sub_id"
        # Call 2: find "nested" in "sub_id" -> returns None
        mock_find.side_effect = ["sub_id", None]

        # Call 1: create "nested" in "sub_id" -> returns "nested_id"
        mock_create.return_value = "nested_id"

        final_id = provider._get_or_create_folder("sub/nested")

        assert final_id == "nested_id"

        expected_calls_find = [
            call("sub", "root_id"),
            call("nested", "sub_id")
        ]
        mock_find.assert_has_calls(expected_calls_find)

        mock_create.assert_called_once_with("nested", "sub_id")

def test_upload_file_nested(provider):
    local_path = Path("/tmp/local/subdir/file.txt")
    remote_path = "subdir/file.txt"

    with patch.object(provider, '_get_or_create_folder') as mock_get_or_create:
        mock_get_or_create.return_value = "subdir_id"

        # Mock create file
        provider.service.files().create.return_value.execute.return_value = {"id": "file_id"}

        # Mock file stat for size and open
        with patch("pathlib.Path.stat") as mock_stat, \
             patch("builtins.open", MagicMock()):
            mock_stat.return_value.st_size = 100

            provider.upload_file(local_path, remote_path)

            mock_get_or_create.assert_called_once_with("subdir")

            # Check create call uses subdir_id
            call_args = provider.service.files().create.call_args
            assert call_args[1]['body']['parents'] == ['subdir_id']
            assert call_args[1]['body']['name'] == 'file.txt'

def test_upload_file_root(provider):
    local_path = Path("/tmp/local/file.txt")
    remote_path = "file.txt"

    with patch.object(provider, '_get_or_create_folder') as mock_get_or_create:
        # Mock create file
        provider.service.files().create.return_value.execute.return_value = {"id": "file_id"}

        with patch("pathlib.Path.stat") as mock_stat, \
             patch("builtins.open", MagicMock()):
            mock_stat.return_value.st_size = 100

            provider.upload_file(local_path, remote_path)

            # _get_or_create_folder should NOT be called for root files
            mock_get_or_create.assert_not_called()

            # Check create call uses root_id (self.folder_id)
            call_args = provider.service.files().create.call_args
            assert call_args[1]['body']['parents'] == ['root_id']

def test_find_folder_escapes_quotes(provider):
    # Setup mock response
    mock_files = provider.service.files.return_value
    mock_list = mock_files.list.return_value
    mock_execute = mock_list.execute.return_value
    mock_execute.get.return_value = [{"id": "found_id", "name": "User's Data"}]

    folder_name = "User's Data"
    provider._find_folder(folder_name, "root_id")

    # Check that quotes were escaped in the query
    call_args = provider.service.files().list.call_args
    query = call_args[1]['q']
    assert "name = 'User\\'s Data'" in query
