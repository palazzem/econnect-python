from .const import STATE_ALARM_UNKNOWN
from . import query as q


class AlarmDevice:
    """Describe.
    Usage:
        TBD
    """

    def __init__(self, connection=None):
        # Configuration and internals
        self._connection = connection
        self._strings = None
        self._lastIds = {
            q.SECTORS: 0,
            q.INPUTS: 0,
        }

        # Alarm state
        self.state = STATE_ALARM_UNKNOWN
        self.sectors_armed = []
        self.sectors_disarmed = []
        self.inputs_alerted = []
        self.inputs_wait = []

    def connect(self, username, password):
        pass

    def has_updates(self):
        pass

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
        # Retrieve sectors and inputs
        sectors_armed, sectors_disarmed, lastSector = self._connection.query(q.SECTORS)
        inputs_alerted, inputs_wait, lastInput = self._connection.query(q.INPUTS)

        self.sectors_armed = sectors_armed
        self.sectors_disarmed = sectors_disarmed
        self.inputs_alerted = inputs_alerted
        self.inputs_wait = inputs_wait
        self._lastIds[q.SECTORS] = lastSector
        self._lastIds[q.INPUTS] = lastInput

    def arm(self, sectors=None):
        pass

    def disarm(self, sectors=None):
        pass
