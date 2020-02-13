from threading import Lock

import pytest

from elmo.api.decorators import require_lock, require_session
from elmo.api.exceptions import LockNotAcquired, PermissionDenied


def test_require_session_present():
    """Should succeed if a session ID is available."""

    class TestClient(object):
        def __init__(self):
            # Session is available
            self._session_id = "test"

        @require_session
        def action(self):
            return 42

    client = TestClient()
    assert client.action() == 42


def test_require_session_missing():
    """Should fail if a session ID is not available."""

    class TestClient(object):
        def __init__(self):
            # Session is not available
            self._session_id = None

        @require_session
        def action(self):
            return 42

    client = TestClient()
    with pytest.raises(PermissionDenied):
        client.action()


def test_require_lock():
    """Should succeed if the lock has been acquired."""

    class TestClient(object):
        def __init__(self):
            # Lock attribute
            self._lock = Lock()

        @require_lock
        def action(self):
            return 42

    client = TestClient()
    client._lock.acquire()
    assert client.action() == 42


def test_require_lock_fails():
    """Should fail if the lock has not been acquired."""

    class TestClient(object):
        def __init__(self):
            # Lock attribute
            self._lock = Lock()

        @require_lock
        def action(self):
            return 42

    client = TestClient()
    with pytest.raises(LockNotAcquired):
        client.action()
