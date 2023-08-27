import logging

from requests.exceptions import HTTPError

from . import query as q
from .api.exceptions import CodeError, CredentialError, LockError, ParseError
from .const import STATE_ALARM_ARMED_AWAY, STATE_ALARM_DISARMED, STATE_ALARM_UNKNOWN
from .utils import _filter_data

_LOGGER = logging.getLogger(__name__)


class AlarmDevice:
    """AlarmDevice class represents an e-connect alarm system. This method wraps around
    a connector object (e.g. `ElmoClient`) so that the client can be stateless and just
    return data, while this class persists the status of the alarm.

    Usage:
        # Initialization
        conn = ElmoClient()
        device = AlarmDevice(conn)

        # Connect automatically grab the latest status
        device.connect("username", "password")
        print(device.state)
    """

    def __init__(self, connection):
        # Configuration and internals
        self._connection = connection
        self._lastIds = {
            q.SECTORS: 0,
            q.INPUTS: 0,
        }

        # Alarm state
        self.state = STATE_ALARM_UNKNOWN
        self.sectors_armed = {}
        self.sectors_disarmed = {}
        self.inputs_alerted = {}
        self.inputs_wait = {}

    def connect(self, username, password):
        """Establish a connection with the E-connect backend, to retrieve an access
        token. This method stores the `session_id` within the `ElmoClient` object
        and is used automatically when other methods are called.

        When a connection is successfully established, the device automatically
        updates the status calling `self.update()`.
        """
        try:
            self._connection.auth(username, password)
        except HTTPError as err:
            _LOGGER.error(f"Device | Error while authenticating with e-Connect: {err}")
            raise err
        except CredentialError as err:
            _LOGGER.error(f"Device | Username or password are not correct: {err}")
            raise err

    def has_updates(self):
        """Use the connection to detect a possible change. This is a blocking call
        that must not be called in the main thread. Check `ElmoClient.poll()` method
        for more details.

        Values passed to `ElmoClient.poll()` are the last known IDs for sectors and
        inputs. A new dictionary is sent to avoid the underlying client to mutate
        the device internal state.
        """
        try:
            return self._connection.poll({x: y for x, y in self._lastIds.items()})
        except HTTPError as err:
            _LOGGER.error(f"Device | Error while checking if there are updates: {err}")
            raise err
        except ParseError as err:
            _LOGGER.error(f"Device | Error parsing the poll response: {err}")
            raise err

    def update(self):
        """Updates the internal state of the device based on the latest data.

        This method performs the following actions:
        1. Queries for the latest sectors and inputs using the internal connection.
        2. Filters the retrieved sectors and inputs to categorize them based on their status.
        3. Updates the last known IDs for sectors and inputs.
        4. Updates internal state for sectors' and inputs' statuses.

        Raises:
            HTTPError: If there's an error while making the HTTP request.
            ParseError: If there's an error while parsing the response.

        Attributes updated:
            sectors_armed (dict): A dictionary of sectors that are armed.
            sectors_disarmed (dict): A dictionary of sectors that are disarmed.
            inputs_alerted (dict): A dictionary of inputs that are in an alerted state.
            inputs_wait (dict): A dictionary of inputs that are in a wait state.
            _lastIds (dict): Updated last known IDs for sectors and inputs.
            state (str): Updated internal state of the device.
        """
        # Retrieve sectors and inputs
        try:
            sectors = self._connection.query(q.SECTORS)
            inputs = self._connection.query(q.INPUTS)
        except (HTTPError, ParseError) as err:
            _LOGGER.error(f"Device | Error while checking if there are updates: {err}")
            raise

        # Filter sectors and inputs
        self.sectors_armed = _filter_data(sectors, "sectors", True)
        self.sectors_disarmed = _filter_data(sectors, "sectors", False)
        self.inputs_alerted = _filter_data(inputs, "inputs", True)
        self.inputs_wait = _filter_data(inputs, "inputs", False)

        self._lastIds[q.SECTORS] = sectors.get("last_id", 0)
        self._lastIds[q.INPUTS] = inputs.get("last_id", 0)

        # Update the internal state machine
        self.state = STATE_ALARM_ARMED_AWAY if self.sectors_armed else STATE_ALARM_DISARMED

    def arm(self, code, sectors=None):
        try:
            with self._connection.lock(code):
                self._connection.arm(sectors=sectors)
                self.state = STATE_ALARM_ARMED_AWAY
        except HTTPError as err:
            _LOGGER.error(f"Device | Error while arming the system: {err}")
            raise err
        except LockError as err:
            _LOGGER.error(f"Device | Error while acquiring the system lock: {err}")
            raise err
        except CodeError as err:
            _LOGGER.error(f"Device | Credentials (alarm code) is incorrect: {err}")
            raise err

    def disarm(self, code, sectors=None):
        try:
            with self._connection.lock(code):
                self._connection.disarm(sectors=sectors)
                self.state = STATE_ALARM_DISARMED
        except HTTPError as err:
            _LOGGER.error(f"Device | Error while disarming the system: {err}")
            raise err
        except LockError as err:
            _LOGGER.error(f"Device | Error while acquiring the system lock: {err}")
            raise err
        except CodeError as err:
            _LOGGER.error(f"Device | Credentials (alarm code) is incorrect: {err}")
            raise err
