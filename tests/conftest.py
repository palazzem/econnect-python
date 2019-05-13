import pytest
import responses

from elmo.api.client import ElmoClient
from elmo.api.router import Router


@pytest.fixture
def client():
    """Create an ElmoClient with a default base URL."""
    client = ElmoClient()
    client._router = Router("https://example.com", "vendor")
    yield client


@pytest.fixture
def server():
    """Create a `responses` mock."""
    with responses.RequestsMock() as resp:
        yield resp
