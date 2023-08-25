import pytest
from requests.exceptions import HTTPError

from elmo import query as q
from elmo.api.exceptions import CodeError, CredentialError, LockError, ParseError
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


def test_device_connect(device, mocker):
    """Should call authentication endpoints."""
    mocker.patch.object(device._connection, "auth")
    mocker.patch.object(device, "update")
    # Test
    device.connect("username", "password")
    assert device._connection.auth.call_count == 1
    assert "username" == device._connection.auth.call_args[0][0]
    assert "password" == device._connection.auth.call_args[0][1]
    assert device.update.call_count == 1


def test_device_connect_error(device, mocker):
    """Should handle (log) authentication errors (not 2xx)."""
    mocker.patch.object(device._connection, "auth")
    mocker.patch.object(device, "update")
    device._connection.auth.side_effect = HTTPError("Unable to communicate with e-Connect")
    # Test
    with pytest.raises(HTTPError):
        device.connect("username", "password")
    assert device._connection.auth.call_count == 1
    assert device.update.call_count == 0


def test_device_connect_credential_error(device, mocker):
    """Should handle (log) credential errors (401/403)."""
    mocker.patch.object(device._connection, "auth")
    mocker.patch.object(device, "update")
    device._connection.auth.side_effect = CredentialError("Incorrect username and/or password")
    # Test
    with pytest.raises(CredentialError):
        device.connect("username", "password")
    assert device._connection.auth.call_count == 1
    assert device.update.call_count == 0


def test_device_has_updates(device, mocker):
    """Should call the client polling system passing the internal state."""
    mocker.patch.object(device._connection, "poll")
    device._lastIds = {q.SECTORS: 42, q.INPUTS: 4242}
    # Test
    device.has_updates()
    assert device._connection.poll.call_count == 1
    assert {9: 42, 10: 4242} in device._connection.poll.call_args[0]


def test_device_has_updates_ids_immutable(device, mocker):
    """Device internal ids must be immutable."""

    def bad_poll(ids):
        ids[q.SECTORS] = 0
        ids[q.INPUTS] = 0

    device._lastIds = {q.SECTORS: 42, q.INPUTS: 4242}
    mocker.patch.object(device._connection, "poll")
    device._connection.poll.side_effect = bad_poll
    # Test
    device.has_updates()
    assert device._connection.poll.call_count == 1
    assert {9: 42, 10: 4242} == device._lastIds


def test_device_has_updates_errors(device, mocker):
    """Should handle (log) polling errors."""
    mocker.patch.object(device._connection, "poll")
    device._connection.poll.side_effect = HTTPError("Unable to communicate with e-Connect")
    # Test
    with pytest.raises(HTTPError):
        device.has_updates()
    assert device._connection.poll.call_count == 1
    assert {9: 0, 10: 0} == device._lastIds


def test_device_has_updates_parse_errors(device, mocker):
    """Should handle (log) polling errors."""
    mocker.patch.object(device._connection, "poll")
    device._connection.poll.side_effect = ParseError("Error parsing the poll response")
    # Test
    with pytest.raises(ParseError):
        device.has_updates()
    assert device._connection.poll.call_count == 1
    assert {9: 0, 10: 0} == device._lastIds


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


def test_device_arm_success(device, mocker):
    """Should arm the e-connect system using the underlying client."""
    mocker.patch.object(device._connection, "lock")
    mocker.patch.object(device._connection, "arm")
    # Test
    device._connection._session_id = "test"
    device.arm("1234", sectors=[4])
    assert device._connection.lock.call_count == 1
    assert device._connection.arm.call_count == 1
    assert "1234" in device._connection.lock.call_args[0]
    assert {"sectors": [4]} == device._connection.arm.call_args[1]


def test_device_arm_error(device, mocker):
    """Should handle (log) connection errors."""
    mocker.patch.object(device._connection, "lock")
    mocker.patch.object(device._connection, "arm")
    device._connection.lock.side_effect = HTTPError("Unable to communicate with e-Connect")
    device._connection._session_id = "test"
    # Test
    with pytest.raises(HTTPError):
        device.arm("1234", sectors=[4])
    assert device._connection.lock.call_count == 1
    assert device._connection.arm.call_count == 0


def test_device_arm_lock_error(device, mocker):
    """Should handle (log) locking errors."""
    mocker.patch.object(device._connection, "lock")
    mocker.patch.object(device._connection, "arm")
    device._connection.lock.side_effect = LockError("Unable to acquire the lock")
    device._connection._session_id = "test"
    # Test
    with pytest.raises(LockError):
        device.arm("1234", sectors=[4])
    assert device._connection.lock.call_count == 1
    assert device._connection.arm.call_count == 0


def test_device_arm_code_error(device, mocker):
    """Should handle (log) code errors."""
    mocker.patch.object(device._connection, "lock")
    mocker.patch.object(device._connection, "arm")
    device._connection.lock.side_effect = CodeError("Code is incorrect")
    device._connection._session_id = "test"
    # Test
    with pytest.raises(CodeError):
        device.arm("1234", sectors=[4])
    assert device._connection.lock.call_count == 1
    assert device._connection.arm.call_count == 0


def test_device_disarm_success(device, mocker):
    """Should disarm the e-connect system using the underlying client."""
    mocker.patch.object(device._connection, "lock")
    mocker.patch.object(device._connection, "disarm")
    # Test
    device._connection._session_id = "test"
    device.disarm("1234", sectors=[4])

    assert device._connection.lock.call_count == 1
    assert device._connection.disarm.call_count == 1
    assert "1234" in device._connection.lock.call_args[0]
    assert {"sectors": [4]} == device._connection.disarm.call_args[1]


def test_device_disarm_error(device, mocker):
    """Should handle (log) connection errors."""
    mocker.patch.object(device._connection, "lock")
    mocker.patch.object(device._connection, "disarm")
    device._connection.lock.side_effect = HTTPError("Unable to communicate with e-Connect")
    device._connection._session_id = "test"
    # Test
    with pytest.raises(HTTPError):
        device.disarm("1234", sectors=[4])
    assert device._connection.lock.call_count == 1
    assert device._connection.disarm.call_count == 0


def test_device_disarm_lock_error(device, mocker):
    """Should handle (log) locking errors."""
    mocker.patch.object(device._connection, "lock")
    mocker.patch.object(device._connection, "disarm")
    device._connection.lock.side_effect = LockError("Unable to acquire the lock")
    device._connection._session_id = "test"
    # Test
    with pytest.raises(LockError):
        device.disarm("1234", sectors=[4])
    assert device._connection.lock.call_count == 1
    assert device._connection.disarm.call_count == 0


def test_device_disarm_code_error(device, mocker):
    """Should handle (log) code errors."""
    mocker.patch.object(device._connection, "lock")
    mocker.patch.object(device._connection, "disarm")
    device._connection.lock.side_effect = CodeError("Code is incorrect")
    device._connection._session_id = "test"
    # Test
    with pytest.raises(CodeError):
        device.disarm("1234", sectors=[4])
    assert device._connection.lock.call_count == 1
    assert device._connection.disarm.call_count == 0
