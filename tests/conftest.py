import pytest

from requests import Response

from elmo.api.client import ElmoClient


@pytest.fixture
def mock_client(mocker):
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
            elif data.get("UserName") == data.get("Password") == "test-fail":
                # Wrong credentials. Status Code is still 200 (API behavior)
                response.status_code = 200
                response._content = b""
            else:
                # Server Error
                response.status_code = 500
                response._context = b"Server error"
        elif endpoint == client._router.lock:
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
            elif data.get("password") == data.get("sessionId") == "test-fail":
                # Wrong credentials
                response.status_code = 403
                response._context = b"""[
                    {
                        "Poller": {"Poller": 1, "Panel": 1},
                        "CommandId": 5,
                        "Successful": False,
                    }
                ]"""
            else:
                # Server Error
                response.status_code = 500
                response._context = b"Server error"
        elif endpoint == client._router.unlock:
            if data.get("sessionId") == "test":
                # Correct credentials
                response.status_code = 200
                response._context = b"""[
                    {
                        "Poller": {"Poller": 1, "Panel": 1},
                        "CommandId": 5,
                        "Successful": True,
                    }
                ]"""
            elif data.get("sessionId") == "test-fail":
                # Wrong credentials
                response.status_code = 403
                response._context = b"""[
                    {
                        "Poller": {"Poller": 1, "Panel": 1},
                        "CommandId": 5,
                        "Successful": False,
                    }
                ]"""
            else:
                # Server Error
                response.status_code = 500
                response._context = b"Server error"
        elif endpoint == client._router.send_command:
            if data.get("sessionId") == "test":
                # Correct credentials
                response.status_code = 200
                response._context = b"""[
                    {
                        "CommandId": 1,
                        "Successful": True,
                    }
                ]"""
            elif data.get("sessionId") == "test-fail":
                # Wrong credentials
                response.status_code = 403
                response._context = b"""[
                    {
                        "CommandId": 1,
                        "Successful": False,
                    }
                ]"""
            else:
                # Server Error
                response.status_code = 500
                response._context = b"Server error"

        return response

    mocker.patch.object(client._session, "post", side_effect=mockresponse)
    yield client
