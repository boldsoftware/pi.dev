from datetime import datetime, timedelta

import pytest
from google.api_core.exceptions import PreconditionFailed

from podcast_generator.server.lock import LockHeldError, StaleLockError, acquire_lock


@pytest.fixture
def mock_storage_client(mocker):
    mock_client = mocker.patch("lock.storage.Client")
    mock_bucket = mocker.Mock()
    mock_blob = mocker.Mock()
    mock_client.return_value.bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = mock_blob
    return mock_blob


def test_acquire_lock_success(mock_storage_client):
    with acquire_lock("test-bucket", "test-path"):
        mock_storage_client.upload_from_string.assert_called_once_with(
            "locked", if_generation_match=0
        )
    mock_storage_client.delete.assert_called_once()


def test_acquire_lock_stale_error(mock_storage_client):
    mock_storage_client.upload_from_string.side_effect = PreconditionFailed(
        "Precondition Failed"
    )
    mock_storage_client.time_created = datetime.now() - timedelta(minutes=31)
    mock_storage_client.generation = 1

    with pytest.raises(StaleLockError):  # noqa: SIM117
        with acquire_lock("test-bucket", "test-path"):
            pass

    mock_storage_client.delete.assert_called_once_with(if_generation_match=1)


def test_acquire_lock_held_error(mock_storage_client):
    mock_storage_client.upload_from_string.side_effect = PreconditionFailed(
        "Precondition Failed"
    )
    mock_storage_client.time_created = datetime.now()
    mock_storage_client.generation = 1

    with pytest.raises(LockHeldError):  # noqa: SIM117
        with acquire_lock("test-bucket", "test-path"):
            pass

    mock_storage_client.delete.assert_not_called()
