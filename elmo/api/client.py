from requests import Session

from .router import Router
from .exceptions import PermissionDenied

from ..conf import settings
from ..utils import parser


class ElmoClient(object):
    """ElmoClient class provides all the functionalities to connect
    to an Elmo system. During the authentication a short-lived token is stored
    in the instance and is used to arm/disarm the system.

    Usage:
        TODO API

    * I need a lock() and unlock()
    * it could lead to a context manager
    * Add a decorator to define a function that requires an access token
    ##
    c = ElmoClient()
    c.auth(username, password)
    with c.lock():
        c.arm()  # this may have a parameter to define what to arm (None means all)
        c.disarm()
    """

    def __init__(self):
        # Client session must be preserved when operating the system
        self._router = Router(settings.base_url, settings.vendor)
        self._session = Session()
        self._session_id = None

    def auth(self, username, password):
        """Authenticate the client and retrieves the access token.

        Args:
            username: the Username used for the authentication
            password: the Password used for the authentication
        Raises:
            AuthenticationFailed: if wrong credentials are used
        """
        payload = {"UserName": username, "Password": password, "RememberMe": False}
        response = self._session.post(self._router.auth, data=payload)
        self._session_id = parser.get_access_token(response.text)

        if self._session_id is None:
            raise PermissionDenied("You do not have permission to perform this action.")

    def connect(self, username, password, code):
        """Uses credentials to gain a login token via Cookies
        and then unlock the system with the given code.
        """
        # Access to the system
        # TODO: Split connect from retrieve Session ID
        payload = {"UserName": username, "Password": password, "RememberMe": False}
        # Parse the Authentication page to retrieve the Session ID
        resp = self._session.post(self._router.auth, data=payload)
        start = resp.text.find("var sessionId = '") + 17
        end = start + 36
        # TODO: validate Session ID
        self._session_id = resp.text[start:end]

        # Set the current session as active
        payload = {"userId": 1, "password": code, "sessionId": self._session_id}
        # TODO: check if it was a success (i.e. concurrent connect are not allowed)
        self._session.post(self._router.connect, data=payload)

    def disconnect(self):
        """Disconnect the system clearing the local cache"""
        if self._session_id is None:
            return False

        payload = {"sessionId": self._session_id}
        self._session.post(self._router.disconnect, data=payload)

        # TODO: check if the logout is a success
        self._session_id = None

    def disable(self):
        """Deactivate the system"""
        if self._session_id is None:
            return False

        payload = {
            "CommandType": 2,
            "ElementsClass": 1,
            "ElementsIndexes": 1,
            "sessionId": self._session_id,
        }
        self._session.post(self._router.send_command, data=payload)

    def enable(self):
        """Activate the system"""
        if self._session_id is None:
            return False

        payload = {
            "CommandType": 1,
            "ElementsClass": 1,
            "ElementsIndexes": 1,
            "sessionId": self._session_id,
        }
        self._session.post(self._router.send_command, data=payload)
