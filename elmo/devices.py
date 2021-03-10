from threading import Lock

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
        self._lock = Lock()
        self._latestEntryId = {
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
        pass

    def arm(self, sectors=None):
        pass

    def disarm(self, sectors=None):
        pass
