from threading import Lock
from contextlib import contextmanager

from requests import Session

from .router import Router
from .exceptions import PermissionDenied, APIException
from .decorators import require_session, require_lock

from ..utils import parser


class ElmoClient(object):
    """ElmoClient class provides all the functionalities to connect
    to an Elmo system. During the authentication a short-lived token is stored
    in the instance and is used to arm/disarm the system.

    Usage:
        # Authenticate to the system (read-only mode)
        c = ElmoClient("https://example.com", "vendor")
        c.auth("username", "password")

        # Obtain a lock to do actions on the system (write mode)
        with c.lock("alarm_code"):
            c.arm()     # Arms all alarms
            c.disarm()  # Disarm all alarms
    """

    def __init__(self, base_url, vendor):
        self._router = Router(base_url, vendor)
        self._session = Session()
        self._session_id = None
        self._lock = Lock()

    def auth(self, username, password):
        """Authenticate the client and retrieves the access token.

        Args:
            username: the Username used for the authentication.
            password: the Password used for the authentication.
        Raises:
            PermissionDenied: if wrong credentials are used.
            APIException: if there is an error raised by the API (not 2xx response).
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
            code: the alarm code used to obtain the lock.
        Raises:
            PermissionDenied: if a wrong access token is used or expired.
            APIException: if there is an error raised by the API (not 2xx response).
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

    @require_session
    @require_lock
    def unlock(self):
        """Release the system lock so that other threads (or this instance) can
        acquire the lock again. This method requires a valid session ID and if called
        when a Lock() is not acquired it bails out.

        If there is a server error or if the call fails, the lock is not released
        so the current thread can do further work before letting another thread
        gain the lock.

        Raises:
            PermissionDenied: if a wrong access token is used or expired.
            APIException: if there is an error raised by the API (not 2xx response).
        Returns:
            A boolean if the lock has been released correctly.
        """
        payload = {"sessionId": self._session_id}
        response = self._session.post(self._router.unlock, data=payload)

        # Release the lock only in case of success, so that if it fails
        # the owner of the lock can properly unlock the system again
        # (maybe with a retry)
        if response.status_code == 200:
            self._lock.release()
            return True
        elif response.status_code == 403:
            raise PermissionDenied("You do not have permission to perform this action.")
        else:
            raise APIException(
                "Unexpected status code: {}".format(response.status_code)
            )

    @require_session
    @require_lock
    def arm(self):
        """Arm all system alarms without any activation delay. This API works only
        if a system lock has been obtained, otherwise the action ends with a failure.
        Note: API subject to changes when more configurations are allowed, such as
        enabling only some alerts.

        Raises:
            PermissionDenied: if a wrong access token is used or expired.
            APIException: if there is an error raised by the API (not 2xx response).
        Returns:
            A boolean if the system has been armed correctly.
        """
        payload = {
            "CommandType": 1,
            "ElementsClass": 1,
            "ElementsIndexes": 1,
            "sessionId": self._session_id,
        }
        response = self._session.post(self._router.send_command, data=payload)
        if response.status_code == 200:
            return True
        elif response.status_code == 403:
            raise PermissionDenied("You do not have permission to perform this action.")
        else:
            raise APIException(
                "Unexpected status code: {}".format(response.status_code)
            )

    @require_session
    @require_lock
    def disarm(self):
        """Deactivate all system alarms. This API works only if a system lock has been
        obtained, otherwise the action ends with a failure.
        Note: API subject to changes when more configurations are allowed, such as
        enabling only some alerts.

        Raises:
            PermissionDenied: if a wrong access token is used or expired.
            APIException: if there is an error raised by the API (not 2xx response).
        Returns:
            A boolean if the system has been disarmed correctly.
        """
        payload = {
            "CommandType": 2,
            "ElementsClass": 1,
            "ElementsIndexes": 1,
            "sessionId": self._session_id,
        }
        response = self._session.post(self._router.send_command, data=payload)
        if response.status_code == 200:
            return True
        elif response.status_code == 403:
            raise PermissionDenied("You do not have permission to perform this action.")
        else:
            raise APIException(
                "Unexpected status code: {}".format(response.status_code)
            )
