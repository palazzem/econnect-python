from requests import Session

from . import settings
from .router import Router


class AlertingClient(object):
    """AlertingClient class provides all the functionalities to connect
    to an Elmo system. It stores login tokens via `Session` cookies
    and exposes actions. Available actions are:
        * `connect` to have credentials to operate with the system
        * `disable` to deactivate the alerting system
        * `enable` to activate the alerting system
    """
    def __init__(self):
        # Connector Session must be preserved when operating the system
        self._router = Router(settings.BASE_URL, settings.VENDOR)
        self._session = Session()
        self._session_id = None

    def connect(self, username, password, code):
        """Uses credentials to gain a login token via Cookies
        and then unlock the system with the given code.
        """
        # Access to the system
        # TODO: Split connect from retrieve Session ID
        payload = {
            'UserName': username,
            'Password': password,
            'RememberMe': False,
        }
        # Parse the Authentication page to retrieve the Session ID
        resp = self._session.post(self._router.auth, data=payload)
        start = resp.text.find("var sessionId = \'") + 17
        end = start + 36
        # TODO: validate Session ID
        self._session_id = resp.text[start:end]

        # Set the current session as active
        payload = {
            'userId': 1,
            'password': code,
            'sessionId': self._session_id,
        }
        # TODO: check if it was a success (i.e. concurrent connect are not allowed)
        self._session.post(self._router.connect, data=payload)

    def disconnect(self):
        """Disconnect the system clearing the local cache"""
        if self._session_id is None:
            return False

        payload = {
            'sessionId': self._session_id,
        }
        self._session.post(self._router.disconnect, data=payload)

        # TODO: check if the logout is a success
        self._session_id = None

    def disable(self):
        """Deactivate the system"""
        if self._session_id is None:
            return False

        payload = {
            'CommandType': 2,
            'ElementsClass': 1,
            'ElementsIndexes': 1,
            'sessionId': self._session_id,
        }
        self._session.post(self._router.send_command, data=payload)

    def enable(self):
        """Activate the system"""
        if self._session_id is None:
            return False

        payload = {
            'CommandType': 1,
            'ElementsClass': 1,
            'ElementsIndexes': 1,
            'sessionId': self._session_id,
        }
        self._session.post(self._router.send_command, data=payload)
