import pytest
import responses

from elmo.devices import AlarmDevice
from elmo.api.client import ElmoClient


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


@pytest.fixture
def sectors_json():
    return """
    [
      {
        "Active": true,
        "ActivePartial": false,
        "Max": false,
        "Activable": true,
        "ActivablePartial": false,
        "InUse": true,
        "Id": 1,
        "Index": 0,
        "Element": 1,
        "CommandId": 0,
        "InProgress": false
      },
      {
        "Active": true,
        "ActivePartial": false,
        "Max": false,
        "Activable": true,
        "ActivablePartial": false,
        "InUse": true,
        "Id": 2,
        "Index": 1,
        "Element": 2,
        "CommandId": 0,
        "InProgress": false
      },
      {
        "Active": false,
        "ActivePartial": false,
        "Max": false,
        "Activable": true,
        "ActivablePartial": false,
        "InUse": true,
        "Id": 3,
        "Index": 2,
        "Element": 3,
        "CommandId": 0,
        "InProgress": false
      },
      {
        "Active": false,
        "ActivePartial": false,
        "Max": false,
        "Activable": true,
        "ActivablePartial": false,
        "InUse": false,
        "Id": 4,
        "Index": 3,
        "Element": 5,
        "CommandId": 0,
        "InProgress": false
      }
    ]
    """


@pytest.fixture
def inputs_json():
    return """
    [
      {
        "Alarm": true,
        "MemoryAlarm": false,
        "Excluded": false,
        "InUse": true,
        "IsVideo": false,
        "Id": 1,
        "Index": 0,
        "Element": 1,
        "CommandId": 0,
        "InProgress": false
      },
      {
        "Alarm": true,
        "MemoryAlarm": false,
        "Excluded": false,
        "InUse": true,
        "IsVideo": false,
        "Id": 2,
        "Index": 1,
        "Element": 2,
        "CommandId": 0,
        "InProgress": false
      },
      {
        "Alarm": false,
        "MemoryAlarm": false,
        "Excluded": true,
        "InUse": true,
        "IsVideo": false,
        "Id": 3,
        "Index": 2,
        "Element": 3,
        "CommandId": 0,
        "InProgress": false
      },
      {
        "Alarm": false,
        "MemoryAlarm": false,
        "Excluded": false,
        "InUse": false,
        "IsVideo": false,
        "Id": 4,
        "Index": 3,
        "Element": 4,
        "CommandId": 0,
        "InProgress": false
      }
    ]
    """
