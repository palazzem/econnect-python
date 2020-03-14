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


@pytest.fixture
def areas_data():
    return """[{"Active":true,"ActivePartial":false,"Max":false,"Activable":true,"ActivablePartial":false,"InUse":true,"Id":1,"Index":0,"Element":1,"CommandId":0,"InProgress":false},{"Active":false,"ActivePartial":false,"Max":false,"Activable":true,"ActivablePartial":false,"InUse":true,"Id":2,"Index":1,"Element":1,"CommandId":0,"InProgress":false}]"""


@pytest.fixture
def inputs_data():
    return """[{"Alarm":false,"MemoryAlarm":false,"Excluded":false,"InUse":true,"IsVideo":false,"Id":1,"Index":0,"Element":1,"CommandId":0,"InProgress":false},{"Alarm":false,"MemoryAlarm":false,"Excluded":false,"InUse":true,"IsVideo":false,"Id":2,"Index":1,"Element":1,"CommandId":0,"InProgress":false}]"""
