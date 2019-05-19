import pytest
import responses

from elmo.api.client import ElmoClient


@pytest.fixture
def client():
    """Create an ElmoClient with a default base URL."""
    client = ElmoClient("https://example.com", "vendor")
    yield client


@pytest.fixture
def server():
    """Create a `responses` mock."""
    with responses.RequestsMock() as resp:
        yield resp
