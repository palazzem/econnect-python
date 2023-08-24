import pytest

from elmo import query as q
from elmo.devices import AlarmDevice


def test_device_constructor(client):
    """Should initialize defaults attributes to run properly."""
    device = AlarmDevice(client)

    assert device._connection == client
    assert device._lastIds == {q.SECTORS: 0, q.INPUTS: 0}
    assert device.state == "unknown"
    assert device.sectors_armed == {}
    assert device.sectors_disarmed == {}
    assert device.inputs_alerted == {}
    assert device.inputs_wait == {}


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

    # Query is called for Areas and Inputs
    assert device._connection.query.call_count == 2
    assert device.sectors_armed == sectors_armed
    assert device.sectors_disarmed == sectors_disarmed
    assert device.inputs_alerted == inputs_alerted
    assert device.inputs_wait == inputs_wait


def test_device_update_state_machine_armed(device, mocker):
    """Should check if the state machine is properly updated after calling update()."""
    # Mock all queries
    mocker.patch.object(device._connection, "query")
    sectors_armed = [
        {"element": 1, "id": 1, "index": 0, "name": "Living Room"},
    ]
    sectors_disarmed = []
    device._connection.query.side_effect = [
        [sectors_armed, sectors_disarmed, 1],
        [[], [], 0],
    ]

    device.update()
    assert device.state == "armed_away"


def test_device_update_state_machine_disarmed(device, mocker):
    """Should check if the state machine is properly updated after calling update()."""
    # Mock all queries
    mocker.patch.object(device._connection, "query")
    sectors_armed = []
    sectors_disarmed = [
        {"element": 1, "id": 1, "index": 0, "name": "Living Room"},
    ]
    device._connection.query.side_effect = [
        [sectors_armed, sectors_disarmed, 1],
        [[], [], 0],
    ]

    device.update()
    assert device.state == "disarmed"


@pytest.mark.xfail
def test_device_update_query_not_valid(device, mocker):
    """Should not crash if an exception is raised."""
    # Mock all queries
    mocker.patch.object(device._connection, "query")
    device._connection.query.side_effect = Exception("Unexpected")

    device.update()


def test_device_authentication(device, mocker):
    """Should authenticate and update the internal status when using `connect()`."""
    mocker.patch.object(device._connection, "auth")
    mocker.patch.object(device, "update")

    # ElmoClient.auth() and AlarmDevice.update() are already tested
    # Check only if they are called properly and if the method handles
    # properly exceptions
    device.connect("username", "password")
    assert device._connection.auth.call_count == 1
    assert "username" == device._connection.auth.call_args[0][0]
    assert "password" == device._connection.auth.call_args[0][1]
    assert device.update.call_count == 1


def test_device_poll_updates_success(device, mocker):
    """Should call the client polling system."""
    mocker.patch.object(device._connection, "poll")
    device._lastIds = {q.SECTORS: 42, q.INPUTS: 4242}

    # ElmoClient.poll() is already tested
    # Check only if they are called properly and if the method handles
    # properly exceptions
    device.has_updates()
    assert device._connection.poll.call_count == 1
    assert {9: 42, 10: 4242} in device._connection.poll.call_args[0]


def test_device_poll_updates_ids_immutable(device, mocker):
    """Should pass a new dictionary to the underlying client, so it stays immutable."""

    def bad_poll(ids):
        ids[q.SECTORS] = 0
        ids[q.INPUTS] = 0

    device._lastIds = {q.SECTORS: 42, q.INPUTS: 4242}
    mocker.patch.object(device._connection, "poll")
    device._connection.poll.side_effect = bad_poll

    # ElmoClient.poll() is already tested
    # Check only if they are called properly and if the method handles
    # properly exceptions
    device.has_updates()
    assert device._connection.poll.call_count == 1
    assert {9: 42, 10: 4242} == device._lastIds


def test_device_arm_success(device, mocker):
    """Should arm the e-connect system using the underlying client."""
    mocker.patch.object(device._connection, "lock")
    mocker.patch.object(device._connection, "arm")

    # ElmoClient.lock() and ElmoClient.arm() are already tested
    # Check only if they are called properly and if the method handles
    # properly exceptions
    device._connection._session_id = "test"
    device.arm("1234", sectors=[4])

    assert device._connection.lock.call_count == 1
    assert device._connection.arm.call_count == 1
    assert "1234" in device._connection.lock.call_args[0]
    assert {"sectors": [4]} == device._connection.arm.call_args[1]


def test_device_disarm_success(device, mocker):
    """Should disarm the e-connect system using the underlying client."""
    mocker.patch.object(device._connection, "lock")
    mocker.patch.object(device._connection, "disarm")

    # ElmoClient.lock() and ElmoClient.disarm() are already tested
    # Check only if they are called properly and if the method handles
    # properly exceptions
    device._connection._session_id = "test"
    device.disarm("1234", sectors=[4])

    assert device._connection.lock.call_count == 1
    assert device._connection.disarm.call_count == 1
    assert "1234" in device._connection.lock.call_args[0]
    assert {"sectors": [4]} == device._connection.disarm.call_args[1]
