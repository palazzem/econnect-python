import pytest

from elmo.api.exceptions import PermissionDenied, APIException


def test_client_auth_success(mock_client):
    """Should authenticate with valid credentials."""
    mock_client.auth("test", "test")
    assert mock_client._session_id == "00000000-0000-0000-0000-000000000000"


def test_client_auth_failure(mock_client):
    """Should raise an exception if credentials are not valid."""
    with pytest.raises(PermissionDenied):
        mock_client.auth("test-fail", "test-fail")


def test_client_auth_unknown_error(mock_client):
    """Should raise an exception if there is an unknown error."""
    with pytest.raises(APIException):
        mock_client.auth("unknown", "unknown")


def test_client_lock(mock_client, mocker):
    """Should acquire a lock if credentials are properly provided."""
    mocker.patch.object(mock_client, "unlock")
    mock_client._session_id = "test"
    with mock_client.lock("test"):
        assert not mock_client._lock.acquire(False)


def test_client_lock_missing_code(mock_client, mocker):
    """Should raise an Exception for unknown status code."""
    mocker.patch.object(mock_client, "unlock")
    mock_client._session_id = "test"
    with pytest.raises(APIException):
        with mock_client.lock(None):
            pass


def test_client_lock_forbidden(mock_client, mocker):
    """Should raise an Exception if credentials are not correct."""
    mocker.patch.object(mock_client, "unlock")
    mock_client._session_id = "test-fail"
    with pytest.raises(PermissionDenied):
        with mock_client.lock("test-fail"):
            pass


def test_client_lock_calls_unlock(mock_client, mocker):
    """Should call unlock() when exiting from the context."""
    mocker.patch.object(mock_client, "unlock")
    mock_client._session_id = "test"
    with mock_client.lock("test"):
        pass
    assert mock_client.unlock.called is True
