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
                response._content = b"""<script type="text/javascript">
                  var apiURL = 'https://example.com';
                  var sessionId = '00000000-0000-0000-0000-000000000000';
                  var canElevate = '1';
                """
            else:
                # Wrong credentials
                response._content = b""
        return response

    monkeypatch.setattr(client._session, "post", mockresponse)
    yield client
