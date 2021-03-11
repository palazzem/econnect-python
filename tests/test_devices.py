import pytest

from elmo import query as q
from elmo.devices import AlarmDevice


def test_device_constructor(client):
    """Should initialize defaults attributes to run properly."""
    device = AlarmDevice(client)

    assert device._connection == client
    assert device._lastIds == {q.SECTORS: 0, q.INPUTS: 0}
    assert device.state == "unknown"
    assert device.sectors_armed == []
    assert device.sectors_disarmed == []
    assert device.inputs_alerted == []
    assert device.inputs_wait == []


def test_device_update_success(device, mocker):
    """Should check store the e-connect System status in the device object."""
    # Mock all queries
    mocker.patch.object(device._connection, "query")
    sectors_armed = [
        {"element": 1, "id": 1, "index": 0, "name": "Living Room"},
        {"element": 2, "id": 2, "index": 1, "name": "Bedroom"},
    ]
    sectors_disarmed = [
        {"element": 3, "id": 3, "index": 2, "name": "Kitchen"},
    ]
    inputs_alerted = [
        {"element": 1, "id": 1, "index": 0, "name": "Alarm"},
        {"element": 2, "id": 2, "index": 1, "name": "Window kitchen"},
    ]
    inputs_wait = [
        [{"element": 3, "id": 3, "index": 2, "name": "Door entryway"}],
    ]
    device._connection.query.side_effect = [
        [sectors_armed, sectors_disarmed, 4],
        [inputs_alerted, inputs_wait, 42],
    ]

    device.update()
    assert device._lastIds == {
        q.SECTORS: 4,
        q.INPUTS: 42,
    }

    assert device.sectors_armed == sectors_armed
    assert device.sectors_disarmed == sectors_disarmed
    assert device.inputs_alerted == inputs_alerted
    assert device.inputs_wait == inputs_wait


@pytest.mark.xfail
def test_device_update_query_not_valid(device, mocker):
    """Should not crash if an exception is raised."""
    # Mock all queries
    mocker.patch.object(device._connection, "query")
    device._connection.query.side_effect = Exception("Unexpected")

    device.update()
