import pytest

from elmo.api.exceptions import PermissionDenied


def test_client_auth_success(mock_client):
    """Should authenticate with valid credentials."""
    mock_client.auth("test", "test")
    assert mock_client._session_id == "00000000-0000-0000-0000-000000000000"


def test_client_auth_failure(mock_client):
    """Should raise an exception if credentials are not valid."""
    with pytest.raises(PermissionDenied):
        mock_client.auth("wrong", "credentials")
