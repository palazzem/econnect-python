import pytest
import responses

from elmo.api.client import ElmoClient
from elmo.devices import AlarmDevice


@pytest.fixture
def client():
    """Create an ElmoClient with unlimited expiration time."""
    client = ElmoClient("https://example.com", "domain")
    yield client


@pytest.fixture
def device(client, mocker):
    """Create an AlarmDevice with a mocked client."""
    client._session = mocker.Mock()
    device = AlarmDevice(connection=client)
    yield device


@pytest.fixture
def server():
    """Create a `responses` mock."""
    with responses.RequestsMock() as resp:
        yield resp
