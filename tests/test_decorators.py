import pytest

from elmo.api.exceptions import InvalidSession
from elmo.api.decorators import require_session


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
    with pytest.raises(InvalidSession):
        client.action()
