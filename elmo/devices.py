from .const import (
    STATE_ALARM_UNKNOWN,
    STATE_ALARM_ARMED_AWAY,
    STATE_ALARM_DISARMED,
)
from . import query as q


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
        # TODO: handle exceptions so that it logs expected errors; add tests for this
        self._connection.auth(username, password)
        self.update()

    def has_updates(self):
        """Use the connection to detect a possible change. This is a blocking call
        that must not be called in the main thread. Check `ElmoClient.poll()` method
        for more details.
        """
        # TODO: handle exceptions so that it logs expected errors; add tests for this
        return self._connection.poll({x: y for x, y in self._lastIds.items()})

    def update(self):
        """Update the internal status of armed and disarmed sectors, or inputs
        that are in alerted state or that are waiting. This method checks:
            * If any sector is in alerted state
            * If the alarm for each sector is armed or disarmed
            * If the alarm for each input is in alerted state or not

        Returns:
            `None`, results are stored as `device` attributes:
            * sectors_armed
            * sectors_disarmed
            * inputs_alerted
            * inputs_wait
        """
        # TODO: handle exceptions so that it logs expected errors; add tests for this
        # Retrieve sectors and inputs
        sectors_armed, sectors_disarmed, lastSector = self._connection.query(q.SECTORS)
        inputs_alerted, inputs_wait, lastInput = self._connection.query(q.INPUTS)

        self.sectors_armed = sectors_armed
        self.sectors_disarmed = sectors_disarmed
        self.inputs_alerted = inputs_alerted
        self.inputs_wait = inputs_wait
        self._lastIds[q.SECTORS] = lastSector
        self._lastIds[q.INPUTS] = lastInput

        # Update the internal state machine
        if self.sectors_armed:
            self.state = STATE_ALARM_ARMED_AWAY
        else:
            self.state = STATE_ALARM_DISARMED

    def arm(self, code, sectors=None):
        # TODO: handle exceptions so that it logs expected errors; add tests for this
        with self._connection.lock(code):
            self._connection.arm(sectors=sectors)
            self.state = STATE_ALARM_ARMED_AWAY

    def disarm(self, code, sectors=None):
        # TODO: handle exceptions so that it logs expected errors; add tests for this
        with self._connection.lock(code):
            self._connection.disarm(sectors=sectors)
            self.state = STATE_ALARM_DISARMED
