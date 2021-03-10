from threading import Lock
from contextlib import contextmanager
from functools import lru_cache

from requests import Session
from requests.exceptions import HTTPError

from .router import Router
from .decorators import require_session, require_lock
from .exceptions import (
    QueryNotValid,
    CredentialError,
    CodeError,
    InvalidSector,
    LockError,
)

from .. import query as q


class ElmoClient(object):
    """ElmoClient class provides all the functionalities to connect
    to an Elmo system. During the authentication a short-lived token is stored
    in the instance and is used to arm/disarm the system.

    Usage:
        # Authenticate to the system (read-only mode)
        c = ElmoClient()
        c.auth("username", "password")

        # Obtain a lock to do actions on the system (write mode)
        with c.lock("alarm_code"):
            c.arm()     # Arms all alarms
            c.disarm()  # Disarm all alarms
    """

    def __init__(self, base_url=None, domain=None, session_id=None):
        self._router = Router(base_url)
        self._domain = domain
        self._session = Session()
        self._session_id = session_id
        self._session_expire = 0
        self._lock = Lock()
        self._strings = None
        # TODO: this item doesn't belong to the client. Split the stateful
        # implementation from the client, so that it can stay stateless.
        self._latestEntryId = {
            q.SECTORS: 0,
            q.INPUTS: 0,
        }

    def auth(self, username, password):
        """Authenticate the client and retrieves the access token. This method uses
        the Authentication API.

        Args:
            username: the Username used for the authentication.
            password: the Password used for the authentication.
        Raises:
            HTTPError: if there is an error raised by the API (not 2xx response).
        Returns:
            The access token retrieved from the API. The token is also cached in
            the `ElmoClient` instance.
        """
        try:
            payload = {"username": username, "password": password}
            if self._domain is not None:
                payload["domain"] = self._domain

            response = self._session.get(self._router.auth, params=payload)
            response.raise_for_status()
        except HTTPError as err:
            # 403: Incorrect username or password
            if err.response.status_code == 403:
                raise CredentialError
            raise err

        # Store the session_id
        data = response.json()
        self._session_id = data["SessionId"]

        # Register the redirect URL and try the authentication again
        if data["Redirect"]:
            self._router._base_url = data["RedirectTo"]
            redirect = self._session.get(self._router.auth, params=payload)
            redirect.raise_for_status()
            data = redirect.json()
            self._session_id = data["SessionId"]

        return self._session_id

    @contextmanager
    @require_session
    def lock(self, code):
        """Context manager to obtain a system lock. The alerting system allows
        only one user at a time and obtaining the lock is mandatory. When the
        context manager is closed, the lock is automatically released.

        Args:
            code: the alarm code used to obtain the lock.
        Raises:
            CodeError: if used `code` is not valid.
            LockError: if the server is refusing to assign the lock. It could mean
            that an unexpected issue happened, or that another application is
            holding the lock. It's possible to retry the operation.
            HTTPError: if there is an error raised by the API (not 2xx response).
        Returns:
            A client instance with an acquired lock.
        """
        payload = {"userId": 1, "password": code, "sessionId": self._session_id}
        response = self._session.post(self._router.lock, data=payload)

        try:
            response.raise_for_status()
        except HTTPError as err:
            # 403: Not possible to obtain the lock, probably because of a race condition
            # with another application
            if err.response.status_code == 403:
                raise LockError
            raise err

        # A wrong code returns 200 with a fail state
        body = response.json()
        if not body[0]["Successful"]:
            raise CodeError

        self._lock.acquire()
        try:
            yield self
        finally:
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
    def arm(self, sectors=None):
        """Arm system alarms without any activation delay. This API works only
        if a system lock has been obtained, otherwise the action ends with a failure.
        It is possible to enable ALL sectors, or provide a list of sectors such as:

            client.arm()        # Arms all sectors
            client.arm([3, 4])  # Arms only sectors 3 and 4

        Args:
            sector: (optional) list of sectors that must be armed. If the variable is
            empty, ALL is assumed and the entire system is armed. If multiple items
            are in the list, multiple requests are sent to arm given sectors.
        Raises:
            HTTPError: if there is an error raised by the API (not 2xx response).
        Returns:
            A boolean if the system has been armed correctly.
        """
        payloads = []
        sectors = sectors or []

        if sectors:
            # Arm only selected sectors
            for sector in sectors:
                payloads.append(
                    {
                        "CommandType": 1,
                        "ElementsClass": 9,
                        "ElementsIndexes": sector,
                        "sessionId": self._session_id,
                    }
                )
        else:
            # Arm ALL sectors
            payloads = [
                {
                    "CommandType": 1,
                    "ElementsClass": 1,
                    "ElementsIndexes": 1,
                    "sessionId": self._session_id,
                }
            ]

        # Arming multiple sectors requires multiple requests
        errors = []
        for payload in payloads:
            response = self._session.post(self._router.send_command, data=payload)
            response.raise_for_status()

            # A not existing sector returns 200 with a fail state
            body = response.json()
            if not body[0]["Successful"]:
                errors.append(payload["ElementsIndexes"])

        # Raise an exception if errors are detected
        if errors:
            invalid_sectors = ",".join(str(x) for x in errors)
            raise InvalidSector(
                "Selected sectors don't exist: {}".format(invalid_sectors)
            )

        return True

    @require_session
    @require_lock
    def disarm(self, sectors=None):
        """Disarm system alarms. This API works only if a system lock has been
        obtained, otherwise the action ends with a failure.
        It is possible to disable ALL sectors, or provide a list of sectors such as:

            client.disarm()     # Disarms all sectors
            client.disarm([3])  # Disarms only sector 3

        Args:
            sector: (optional) list of sectors that must be disarmed. If the variable is
            empty, ALL is assumed and the entire system is disarmed. If multiple items
            are in the list, multiple requests are sent to disarm given sectors.
        Raises:
            HTTPError: if there is an error raised by the API (not 2xx response).
        Returns:
            A boolean if the system has been disarmed correctly.
        """
        payloads = []
        sectors = sectors or []

        if sectors:
            # Disarm only selected sectors
            for sector in sectors:
                payloads.append(
                    {
                        "CommandType": 2,
                        "ElementsClass": 9,
                        "ElementsIndexes": sector,
                        "sessionId": self._session_id,
                    }
                )
        else:
            # Disarm ALL sectors
            payloads = [
                {
                    "CommandType": 2,
                    "ElementsClass": 1,
                    "ElementsIndexes": 1,
                    "sessionId": self._session_id,
                }
            ]

        # Disarming multiple sectors requires multiple requests
        errors = []
        for payload in payloads:
            response = self._session.post(self._router.send_command, data=payload)
            response.raise_for_status()

            # A not existing sector returns 200 with a fail state
            body = response.json()
            if not body[0]["Successful"]:
                errors.append(payload["ElementsIndexes"])

        # Raise an exception if errors are detected
        if errors:
            invalid_sectors = ",".join(str(x) for x in errors)
            raise InvalidSector(
                "Selected sectors don't exist: {}".format(invalid_sectors)
            )

        return True

    @lru_cache(maxsize=1)
    @require_session
    def _get_descriptions(self):
        """Retrieve Sectors and Inputs names to map `Class` and `Index` into a
        human readable description. This method calls the E-Connect API, but the
        result is cached for the entire `ElmoClient` life-cycle.

        Raises:
            HTTPError: if there is an error raised by the API (not 2xx response).
        Returns:
            A dictionary having `Class` as key, and a dictionary of strings (`Index`)
            as a value, to map sectors and inputs names.
        """
        payload = {"sessionId": self._session_id}
        response = self._session.post(self._router.descriptions, data=payload)
        response.raise_for_status()

        # Transform the list of items in a dict -> dict of strings
        descriptions = {}
        for item in response.json():
            classes = descriptions.get(item["Class"], {})
            classes[item["Index"]] = item["Description"]
            descriptions[item["Class"]] = classes

        return descriptions

    @require_session
    def query(self, query):
        """Query an Elmo System to retrieve registered entries. Items are grouped
        by "Active" status. It's possible to query different part of the system
        using the `elmo.query` module:

            from elmo import query

            sectors_armed, sectors_disarmed = client.query(query.SECTORS)
            inputs_alerted, inputs_wait = client.query(query.INPUTS)

        Raises:
            QueryNotValid: if the query is not recognized.
            HTTPError: if there is an error raised by the API (not 2xx response).
        Returns:
            A tuple containing two list `(active, not_active)`. Every item is an entry
            (sector or input) represented by a `dict` with the following fields: `id`,
            `index`, `element`, `name`.
        """
        # Query detection
        if query == q.SECTORS:
            endpoint = self._router.sectors
            status = "Active"
        elif query == q.INPUTS:
            status = "Alarm"
            endpoint = self._router.inputs
        else:
            # Bail-out if the query is not recognized
            raise QueryNotValid()

        response = self._session.post(endpoint, data={"sessionId": self._session_id})
        response.raise_for_status()

        # Retrieve cached descriptions
        descriptions = self._get_descriptions()

        # Filter only entries that are used
        active = []
        not_active = []
        entries = response.json()

        # The last entry ID is used in `self.poll()` long-polling API
        self._latestEntryId[query] = entries[-1]["Id"]

        # Massage data
        for entry in entries:
            if entry["InUse"]:
                item = {
                    "id": entry["Id"],
                    "index": entry["Index"],
                    "element": entry["Element"],
                    "name": descriptions[query][entry["Index"]],
                }

                if entry[status]:
                    active.append(item)
                else:
                    not_active.append(item)

        return active, not_active

    @require_session
    def check(self):
        """Check the Elmo System to get the status of armed or disarmed sectors or inputs
        that are in alerted state or that are waiting. This method checks:
            * If any sector is in alerted state
            * If the alarm for each sector is armed or disarmed
            * If the alarm for each input is in alerted state or not

        This method is considered a shortcut that calls `client.query()` with `SECTORS`
        and `INPUTS` queries.

        Raises:
            HTTPError: if there is an error raised by the API (not 2xx response).
        Returns:
            A `dict` object that includes all the above information. The `dict` is in
            the following format:
            {
              "sectors_armed": [{"id": 0, "name": "Entryway", "element": 1, "index": 0}, ...],
              "sectors_disarmed": [{"id": 1, "name": "Kitchen", "element": 2, "index": 1}, ...],
              "inputs_alerted": [{"id": 0, "name": "Door", "element": 3, "index": 0}, ...],
              "inputs_wait": [{"id": 1, "name": "Window", "element": 4, "index": 1}, ...],
            }
        """
        # Retrieve sectors and inputs
        sectors_armed, sectors_disarmed = self.query(q.SECTORS)
        inputs_alerted, inputs_wait = self.query(q.INPUTS)

        return {
            "sectors_armed": sectors_armed,
            "sectors_disarmed": sectors_disarmed,
            "inputs_alerted": inputs_alerted,
            "inputs_wait": inputs_wait,
        }
