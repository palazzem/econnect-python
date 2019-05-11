import pytest

from requests import Response

from elmo.api.client import ElmoClient


@pytest.fixture
def mock_client(monkeypatch):
    """Create an ElmoClient that mocks external calls based on the values
    defined by the internal router. The mock tests the client internal logic
    (i.e. retrieving an access token), but it doesn't take in account the
    response from the server.

    If the response changes, ``mockresponse`` must be updated.
    """
    client = ElmoClient()

    def mockresponse(endpoint, data=None):
        response = Response()
        if endpoint == client._router.auth:
            if data.get("UserName") == data.get("Password") == "test":
                # Correct credentials
                response.status_code = 200
                response._content = b"""<script type="text/javascript">
                  var apiURL = 'https://example.com';
                  var sessionId = '00000000-0000-0000-0000-000000000000';
                  var canElevate = '1';
                """
            else:
                # Wrong credentials. Status Code is still 200 (API behavior)
                response.status_code = 200
                response._content = b""
        if endpoint == client._router.lock:
            if data.get("password") == data.get("sessionId") == "test":
                # Correct credentials
                response.status_code = 200
                response._context = b"""[
                    {
                        "Poller": {"Poller": 1, "Panel": 1},
                        "CommandId": 5,
                        "Successful": True,
                    }
                ]"""
            elif data.get("password") is None:
                # Missing session ID
                response.status_code = 401
                response._context = b"""[
                    {
                        "Poller": {"Poller": 1, "Panel": 1},
                        "CommandId": 5,
                        "Successful": False,
                    }
                ]"""
            else:
                # Wrong credentials
                response.status_code = 403
                response._context = b"""[
                    {
                        "Poller": {"Poller": 1, "Panel": 1},
                        "CommandId": 5,
                        "Successful": False,
                    }
                ]"""

        return response

    monkeypatch.setattr(client._session, "post", mockresponse)
    yield client
