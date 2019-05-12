import pytest

from elmo.api.exceptions import APIException, PermissionDenied, LockNotAcquired


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


def test_client_unlock(mock_client):
    """Should call the API and release the system lock."""
    mock_client._session_id = "test"
    mock_client._lock.acquire()
    assert mock_client.unlock() is True
    assert mock_client._session.post.called is True
    assert mock_client._lock.acquire(False)


def test_client_unlock_fails_missing_lock(mock_client):
    """unlock() should fail without calling the endpoint if Lock() has not been acquired."""
    mock_client._session_id = "test"
    with pytest.raises(LockNotAcquired):
        mock_client.unlock()
    assert mock_client._session.post.called is False
    assert mock_client._lock.acquire(False)


def test_client_unlock_fails_wrong_credentials(mock_client):
    """Should fail if wrong credentials are used."""
    mock_client._session_id = "test-fail"
    mock_client._lock.acquire()
    with pytest.raises(PermissionDenied):
        mock_client.unlock()
    assert mock_client._session.post.called is True
    assert not mock_client._lock.acquire(False)


def test_client_unlock_fails_unexpected_error(mock_client):
    """Should raise an error and keep the lock if the server has problems."""
    mock_client._session_id = "unknown"
    mock_client._lock.acquire()
    with pytest.raises(APIException):
        mock_client.unlock()
    assert mock_client._session.post.called is True
    assert not mock_client._lock.acquire(False)


def test_client_arm(mock_client):
    """Should call the API and arm the system."""
    mock_client._session_id = "test"
    mock_client._lock.acquire()
    assert mock_client.arm() is True
    assert mock_client._session.post.called is True


def test_client_arm_fails_missing_lock(mock_client):
    """arm() should fail without calling the endpoint if Lock() has not been acquired."""
    mock_client._session_id = "test"
    with pytest.raises(LockNotAcquired):
        mock_client.arm()
    assert mock_client._session.post.called is False
    assert mock_client._lock.acquire(False)


def test_client_arm_fails_missing_session(mock_client):
    """Should fail if a wrong access token is used."""
    mock_client._session_id = "test-fail"
    mock_client._lock.acquire()
    with pytest.raises(PermissionDenied):
        mock_client.arm()
    assert mock_client._session.post.called is True


def test_client_arm_fails_unknown_error(mock_client):
    """Should fail if an unknown error happens."""
    mock_client._session_id = "unknown"
    mock_client._lock.acquire()
    with pytest.raises(APIException):
        mock_client.arm()
    assert mock_client._session.post.called is True


def test_client_disarm(mock_client):
    """Should call the API and disarm the system."""
    mock_client._session_id = "test"
    mock_client._lock.acquire()
    assert mock_client.disarm() is True
    assert mock_client._session.post.called is True


def test_client_disarm_fails_missing_lock(mock_client):
    """disarm() should fail without calling the endpoint if Lock() has not been acquired."""
    mock_client._session_id = "test"
    with pytest.raises(LockNotAcquired):
        mock_client.disarm()
    assert mock_client._session.post.called is False
    assert mock_client._lock.acquire(False)


def test_client_disarm_fails_missing_session(mock_client):
    """Should fail if a wrong access token is used."""
    mock_client._session_id = "test-fail"
    mock_client._lock.acquire()
    with pytest.raises(PermissionDenied):
        mock_client.disarm()
    assert mock_client._session.post.called is True


def test_client_disarm_fails_unknown_error(mock_client):
    """Should fail if an unknown error happens."""
    mock_client._session_id = "unknown"
    mock_client._lock.acquire()
    with pytest.raises(APIException):
        mock_client.disarm()
    assert mock_client._session.post.called is True
