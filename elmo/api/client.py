from threading import Lock
from contextlib import contextmanager

from requests import Session

from .router import Router
from .exceptions import PermissionDenied, APIException
from .decorators import require_session

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
        self._lock = Lock()

    def auth(self, username, password):
        """Authenticate the client and retrieves the access token.

        Args:
            username: the Username used for the authentication
            password: the Password used for the authentication
        Raises:
            PermissionDenied: if wrong credentials are used
            APIException: if there is an error raised by the API (not 2xx response)
        """
        payload = {"UserName": username, "Password": password, "RememberMe": False}
        response = self._session.post(self._router.auth, data=payload)
        if response.status_code == 200:
            self._session_id = parser.get_access_token(response.text)
        else:
            raise APIException(
                "Unexpected status code: {}".format(response.status_code)
            )

        if self._session_id is None:
            raise PermissionDenied("You do not have permission to perform this action.")

    @contextmanager
    @require_session
    def lock(self, code):
        """Context manager to obtain a system lock. The alerting system allows
        only one user at a time and obtaining the lock is mandatory. When the
        context manager is closed, the lock is automatically released.

        Args:
            code: the private access code to obtain the lock.
        Returns:
            A client instance with an acquired lock.
        """
        payload = {"userId": 1, "password": code, "sessionId": self._session_id}
        response = self._session.post(self._router.lock, data=payload)
        if response.status_code == 200:
            self._lock.acquire()
            yield self
            self.unlock()
        elif response.status_code == 403:
            raise PermissionDenied("You do not have permission to perform this action.")
        else:
            raise APIException(
                "Unexpected status code: {}".format(response.status_code)
            )

    def unlock(self):
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
