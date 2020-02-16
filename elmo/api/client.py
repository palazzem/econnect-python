from contextlib import contextmanager
from threading import Lock

from requests import Session

from .decorators import require_lock, require_session
from .exceptions import PermissionDenied
from .router import Router


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

    def __init__(self, base_url, vendor, session_id=None):
        self._router = Router(base_url)
        self._vendor = vendor
        self._session = Session()
        self._session_id = session_id
        self._lock = Lock()
        self._strings = None

    def auth(self, username, password):
        """Authenticate the client and retrieves the access token. This API uses
        the authentication API. 
        Args:
            username: the Username used for the authentication.
            password: the Password used for the authentication.
        Raises:
            HTTPError: if there is an error raised by the API (not 2xx response).
        Returns:
            The access token retrieved from the API. The token is also
            cached in the `ElmoClient` instance.
        """
        payload = {"username": username, "password": password, "domain": self._vendor}
        response = self._session.get(self._router.auth, params=payload)
        response.raise_for_status()

        data = response.json()
        self._session_id = data["SessionId"]

        if data["Redirect"]:
            self._router = Router(data["RedirectTo"])
            self._session_id = self.auth(username, password)
            return self._session_id

        return self._session_id

    @require_session
    def _update_strings(self):
        payload = {"sessionId": self._session_id}

        response = self._session.post(self._router.strings, data=payload)
        response.raise_for_status()

        self._strings = response.json()

    @contextmanager
    @require_session
    def lock(self, code):
        """Context manager to obtain a system lock. The alerting system allows
        only one user at a time and obtaining the lock is mandatory. When the
        context manager is closed, the lock is automatically released.

        Args:
            code: the alarm code used to obtain the lock.
        Raises:
            HTTPError: if there is an error raised by the API (not 2xx response).
        Returns:
            A client instance with an acquired lock.
        """
        payload = {"userId": 1, "password": code, "sessionId": self._session_id}
        response = self._session.post(self._router.lock, data=payload)
        response.raise_for_status()

        self._lock.acquire()
        yield self
        self.unlock()

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
            HTTPError: if there is an error raised by the API (not 2xx response).
        Returns:
            A boolean if the lock has been released correctly.
        """
        payload = {"sessionId": self._session_id}
        response = self._session.post(self._router.unlock, data=payload)
        response.raise_for_status()

        # Release the lock only in case of success, so that if it fails
        # the owner of the lock can properly unlock the system again
        # (maybe with a retry)
        self._lock.release()
        return True

    @require_session
    @require_lock
    def arm(self):
        """Arm all system alarms without any activation delay. This API works only
        if a system lock has been obtained, otherwise the action ends with a failure.
        Note: API subject to changes when more configurations are allowed, such as
        enabling only some alerts.

        Raises:
            HTTPError: if there is an error raised by the API (not 2xx response).
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
        response.raise_for_status()
        return True

    @require_session
    @require_lock
    def disarm(self):
        """Deactivate all system alarms. This API works only if a system lock has been
        obtained, otherwise the action ends with a failure.
        Note: API subject to changes when more configurations are allowed, such as
        enabling only some alerts.

        Raises:
            HTTPError: if there is an error raised by the API (not 2xx response).
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
        response.raise_for_status()
        return True

    @require_session
    @require_lock
    def arm_sector(self, sector_number):
        """Arm selected sector without any activation delay. This API works only
        if a system lock has been obtained, otherwise the action ends with a failure.
        Note: API subject to changes when more configurations are allowed, such as
        enabling only some alerts.

        Raises:
            HTTPError: if there is an error raised by the API (not 2xx response).
        Returns:
            A boolean if the sector has been armed correctly.
        """
        payload = {
            "CommandType": 1,
            "ElementsClass": 9,
            "ElementsIndexes": sector_number,
            "sessionId": self._session_id,
        }
        response = self._session.post(self._router.send_command, data=payload)
        response.raise_for_status()
        return True

    @require_session
    @require_lock
    def disarm_sector(self, sector_number):
        """Deactivate selected sector alarm. This API works only if a system lock has been
        obtained, otherwise the action ends with a failure.
        Note: API subject to changes when more configurations are allowed, such as
        enabling only some alerts.

        Raises:
            HTTPError: if there is an error raised by the API (not 2xx response).
        Returns:
            A boolean if the sector has been disarmed correctly.
        """
        payload = {
            "CommandType": 2,
            "ElementsClass": 9,
            "ElementsIndexes": sector_number,
            "sessionId": self._session_id,
        }
        response = self._session.post(self._router.send_command, data=payload)
        response.raise_for_status()
        return True

    @require_session
    def _get_names(self, element, class_):
        """Generic function that retrieves items from Elmo dashboard.

        Raises:
            HTTPError: if there is an error raised by the API (not 2xx response).
        Returns:
            A list of strings (names) for areas or system inputs.
        """
        index = element["Index"]

        name = next(
            filter(
                lambda x: x["Class"] == class_ and x["Index"] == index, self._strings
            ),
            None,
        )["Description"]

        element["Name"] = name
        return element

    @require_session
    def check(self):
        """Check the Elmo System to get the status of armed or disarmed areas, inputs
        that are in alerted state or that are waiting. With this method you can check:
            * The global status if any area is in alerted state
            * The status for each area, if the alarm is armed or disarmed
            * The status for each area, if the area is in alerted state

        Raises:
            HTTPError: if there is an error raised by the API (not 2xx response).
        Returns:
            A `dict` object that includes all the above information. The `dict` is in
            the following format:
            {
                "areas_armed": [{"id": 0, "name": "Entryway"}, ...],
                "areas_disarmed": [{"id": 1, "name": "Kitchen"}, ...],
                "inputs_alerted": [{"id": 0, "name": "Door"}, ...],
                "inputs_wait": [{"id": 1, "name": "Window"}, ...],
            }
        """
        # Retrieves strings if not present
        if not self._strings:
            self._update_strings()

        payload = {"sessionId": self._session_id}

        # Retrieve areas
        response = self._session.post(self._router.areas, data=payload)
        response.raise_for_status()

        areas = response.json()
        areas = list(filter(lambda area: area["InUse"], areas))
        areas = list(map(lambda x: self._get_names(x, 9), areas))

        areas_armed = list(filter(lambda area: area["Active"], areas))
        areas_disarmed = list(filter(lambda area: not area["Active"], areas))

        # Retrieve inputs
        response = self._session.post(self._router.inputs, data=payload)
        response.raise_for_status()

        inputs = response.json()
        inputs = list(filter(lambda input_: input_["InUse"], inputs))
        inputs = list(map(lambda x: self._get_names(x, 10), inputs))

        inputs_alerted = list(filter(lambda input_: input_["Alarm"], inputs))
        inputs_wait = list(filter(lambda input_: not input_["Alarm"], inputs))

        def set_output_dict(item):
            entry = {
                "id": item["Id"],
                "index": item["Index"],
                "element": item["Element"],
                "name": item["Name"],
            }
            return entry

        areas_armed = list(map(lambda x: set_output_dict(x), areas_armed))
        areas_disarmed = list(map(lambda x: set_output_dict(x), areas_disarmed))
        inputs_alerted = list(map(lambda x: set_output_dict(x), inputs_alerted))
        inputs_wait = list(map(lambda x: set_output_dict(x), inputs_wait))

        return {
            "areas_armed": areas_armed,
            "areas_disarmed": areas_disarmed,
            "inputs_alerted": inputs_alerted,
            "inputs_wait": inputs_wait,
        }
