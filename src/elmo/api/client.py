import logging
from contextlib import contextmanager
from functools import lru_cache
from threading import Lock

from requests import Session
from requests.exceptions import HTTPError

from .. import query as q
from ..utils import _camel_to_snake_case, _sanitize_session_id
from .decorators import require_lock, require_session
from .exceptions import (
    CodeError,
    CredentialError,
    InvalidInput,
    InvalidSector,
    LockError,
    ParseError,
    QueryNotValid,
)
from .router import Router

_LOGGER = logging.getLogger(__name__)


class ElmoClient:
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
        self._lock = Lock()
        # Debug
        _LOGGER.debug(f"Client | Router: {self._router._base_url}")
        _LOGGER.debug(f"Client | Domain: {self._domain}")

    def auth(self, username, password):
        """Authenticate the client and retrieves the access token. This method uses
        the Authentication API.

        Args:
            username: the Username used for the authentication.
            password: the Password used for the authentication.
        Raises:
            HTTPError: if there is an error raised by the API (not 2xx response).
            CredentialError: if credentials are not correct
        Returns:
            The access token retrieved from the API. The token is also cached in
            the `ElmoClient` instance.
        """
        try:
            payload = {"username": username, "password": password}
            if self._domain is not None:
                payload["domain"] = self._domain

            _LOGGER.debug("Client | Client Authentication")
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
            _LOGGER.debug(f"Redirect URL detected: {data['RedirectTo']}")
            self._router._base_url = data["RedirectTo"]
            redirect = self._session.get(self._router.auth, params=payload)
            redirect.raise_for_status()
            data = redirect.json()
            self._session_id = data["SessionId"]

        _LOGGER.debug(f"Client | Authentication successful: {_sanitize_session_id(self._session_id)}")
        return self._session_id

    @require_session
    def poll(self, ids):
        """Use a long-polling API to identify when something changes in the
        system. Calling this method blocks the thread for 15 seconds, waiting
        for a backend response that happens only when the alarm system status
        changes. Don't call this method from your main thread otherwise the
        application hangs.

        When the API returns that something is changed, you must call the
        `client.check()` to update your identifiers. Missing this step means
        that the next time you will call `client.poll()` the API returns immediately
        with an old result.

        Raises:
            HTTPError: if there is an error raised by the API (not 2xx response).
            ParseError: if the response cannot be parsed because the format is unexpected.
        Returns:
            A dictionary that includes what items have been changed. The following
            structure means that `areas` are not changed, while inputs are:
                {
                    "areas": False,
                    "inputs": True,
                }
        """
        payload = {
            "sessionId": self._session_id,
            "Areas": ids[q.SECTORS],
            "Inputs": ids[q.INPUTS],
            "CanElevate": "1",
            "ConnectionStatus": "1",
        }
        response = self._session.post(self._router.update, data=payload)
        response.raise_for_status()

        # Don't use state["HasChanges"] because it takes into account also events
        # that this client is ignoring. It forces the device to update too often.
        state = response.json()
        try:
            update = {
                "has_changes": state["Areas"] or state["Inputs"],
                "areas": state["Areas"],
                "inputs": state["Inputs"],
            }
        except KeyError as err:
            raise ParseError(f"Client | Unable to parse poll response: {err} is missing") from err

        _LOGGER.debug(f"Client | Polling result: {update}")
        return update

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
        _LOGGER.debug(f"Client | Lock acquired with response {body}")
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

        _LOGGER.debug(f"Client | Lock released with response {response.text}")
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
            _LOGGER.debug(f"Client | Arming sectors: {sectors}")
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
            _LOGGER.debug("Client | Arming all sectors")
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
            _LOGGER.debug(f"Client | Arming response: {body}")
            if not body[0]["Successful"]:
                errors.append(payload["ElementsIndexes"])

        # Raise an exception if errors are detected
        if errors:
            invalid_sectors = ",".join(str(x) for x in errors)
            raise InvalidSector("Selected sectors don't exist: {}".format(invalid_sectors))

        _LOGGER.debug("Client | Arming successful")
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
            _LOGGER.debug(f"Client | Disarming sectors: {sectors}")
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
            _LOGGER.debug("Client | Disarming all sectors")
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
            _LOGGER.debug(f"Client | Disarming response: {body}")
            if not body[0]["Successful"]:
                errors.append(payload["ElementsIndexes"])

        # Raise an exception if errors are detected
        if errors:
            invalid_sectors = ",".join(str(x) for x in errors)
            raise InvalidSector("Selected sectors don't exist: {}".format(invalid_sectors))

        _LOGGER.debug("Client | Disarming successful")
        return True

    @require_session
    @require_lock
    def exclude(self, inputs):
        """Exclude passed inputs: they are not alarmed
        when you arm the area they belongs to.

        This API provides the same effects as turning them
        from "idle" to "bypassed" on the E-Connect web UI.

        This API works only if a system lock has been
        obtained, otherwise the action ends with a failure.
        It is possible to provide a list of inputs such as:

            client.exclude([3])  # Excludes only input 3
            client.exclude([3, 5])  # Excludes input 3 and 5

        Args:
            inputs: list of inputs that must be excluded. If multiple items
            are in the list, multiple requests are sent to exclude given inputs.
        Raises:
            HTTPError: if there is an error raised by the API (not 2xx response).
        Returns:
            A boolean if the input has been excluded correctly.
        """
        payloads = []

        # Exclude only selected inputs
        _LOGGER.debug(f"Client | Excluding inputs: {inputs}")
        for element in inputs:
            payloads.append(
                {
                    "CommandType": 2,
                    "ElementsClass": 10,
                    "ElementsIndexes": element,
                    "sessionId": self._session_id,
                }
            )

        # Excluding multiple inputs requires multiple requests
        errors = []
        for payload in payloads:
            response = self._session.post(self._router.send_command, data=payload)
            response.raise_for_status()

            # A not existing input returns 200 with a fail state
            body = response.json()
            _LOGGER.debug(f"Client | Excluding response: {body}")
            if not body[0]["Successful"]:
                errors.append(payload["ElementsIndexes"])

        # Raise an exception if errors are detected
        if errors:
            invalid_inputs = ",".join(str(x) for x in errors)
            raise InvalidInput("Selected inputs don't exist: {}".format(invalid_inputs))

        _LOGGER.debug("Client | Excluding successful")
        return True

    @require_session
    @require_lock
    def include(self, inputs):
        """Include system inputs: they are alarmed
        when you arm the area they belongs to.

        This API provides the same effects as turning them
        from "bypassed" to "idle" on the E-Connect web UI.

        This API works only if a system lock has been
        obtained, otherwise the action ends with a failure.
        It is possible to provide a list of inputs such as:

            client.include([3])  # Includes only input 3
            client.include([3, 5])  # Includes input 3 and 5

        Args:
            inputs: list of inputs that must be included. If multiple items
            are in the list, multiple requests are sent to include given inputs.
        Raises:
            HTTPError: if there is an error raised by the API (not 2xx response).
        Returns:
            A boolean if the input has been included correctly.
        """
        payloads = []

        # Include only selected inputs
        _LOGGER.debug(f"Client | Including inputs: {inputs}")
        for element in inputs:
            payloads.append(
                {
                    "CommandType": 1,
                    "ElementsClass": 10,
                    "ElementsIndexes": element,
                    "sessionId": self._session_id,
                }
            )

        # Including multiple inputs requires multiple requests
        errors = []
        for payload in payloads:
            response = self._session.post(self._router.send_command, data=payload)
            response.raise_for_status()

            # A not existing input returns 200 with a fail state
            body = response.json()
            _LOGGER.debug(f"Client | Including response: {body}")
            if not body[0]["Successful"]:
                errors.append(payload["ElementsIndexes"])

        # Raise an exception if errors are detected
        if errors:
            invalid_inputs = ",".join(str(x) for x in errors)
            raise InvalidInput("Selected inputs don't exist: {}".format(invalid_inputs))

        _LOGGER.debug("Client | Including successful")
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
        items = response.json()
        _LOGGER.debug(f"Client | Descriptions response: {items}")
        for item in items:
            classes = descriptions.get(item["Class"], {})
            classes[item["Index"]] = item["Description"]
            descriptions[item["Class"]] = classes

        _LOGGER.debug(f"Client | Descriptions retrieved (in-cache): {descriptions}")
        return descriptions

    @require_session
    def query(self, query):
        """Query an Elmo System to retrieve registered entries. It's possible to query
        different part of the system using the `elmo.query` module:

            from elmo import query

            sectors = client.query(query.SECTORS).get("sectors")
            inputs = client.query(query.INPUTS).get("inputs")

        Raises:
            QueryNotValid: if the query is not recognized.
            HTTPError: if there is an error raised by the API (not 2xx response).
            ParseError: if the response cannot be parsed because the format is unexpected.
        Returns:
            A dict representing the raw query retrieved by the backend call. The structure is the following:
                {
                    'last_id': 3,
                    'sectors': {
                        0: {
                            'id': 1,
                            'index': 0,
                            'element': 1,
                            'excluded': False,
                            'status': True,
                            'name': 'S1 Living Room'
                        },
                        1: {
                            'id': 2,
                            'index': 1,
                            'element': 2,
                            'excluded': False,
                            'status': True,
                            'name': 'S2 Bedroom'
                        },
                    },
                }
            `last_id`: is the last ID of the query, used to retrieve new state changes
            `sectors`: is the key you use to retrieve sectors if that was the query
            `inputs`: is the key you use to retrieve inputs if that was the query
        """
        # Query detection
        if query == q.SECTORS:
            status = "Active"
            key_group = "sectors"
            endpoint = self._router.sectors
            _LOGGER.debug("Client | Querying sectors")
        elif query == q.INPUTS:
            status = "Alarm"
            key_group = "inputs"
            endpoint = self._router.inputs
            _LOGGER.debug("Client | Querying inputs")
        elif query == q.ALERTS:
            endpoint = self._router.status
            _LOGGER.debug("Client | Querying alerts")
        else:
            # Bail-out if the query is not recognized
            raise QueryNotValid()

        response = self._session.post(endpoint, data={"sessionId": self._session_id})
        response.raise_for_status()

        if query in [q.SECTORS, q.INPUTS]:
            # Retrieve description or use the cache
            descriptions = self._get_descriptions()

            # Filter only entries that are used
            # `excluded` field is available only on inputs, but to return the same `dict`
            # structure, we default "excluded" as False for sectors. In fact, sectors
            # are never excluded.
            entries = response.json()
            _LOGGER.debug(f"Client | Query response: {entries}")
            items = {}
            result = {
                "last_id": entries[-1]["Id"],
                key_group: items,
            }
            try:
                for entry in entries:
                    if entry["InUse"]:
                        # Address potential data inconsistency between cloud data and main unit.
                        # In some installations, they may be out of sync, resulting in the cloud
                        # providing a sector/input that doesn't actually exist in the main unit.
                        # To handle this, we default the name to "Unknown" if its description
                        # isn't found in the cloud data to prevent KeyError.
                        name = descriptions[query].get(entry["Index"], "Unknown")
                        item = {
                            "id": entry.get("Id"),
                            "index": entry.get("Index"),
                            "element": entry.get("Element"),
                            "excluded": entry.get("Excluded", False),
                            "status": entry.get(status, False),
                            "name": name,
                        }

                        items[entry.get("Index")] = item
            except KeyError as err:
                raise ParseError(f"Client | Unable to parse query response: {err}") from err

            _LOGGER.debug(f"Client | Query parsed successfully: {result}")
            return result
        elif query == q.ALERTS:
            try:
                # Check if the response has the expected format
                msg = response.json()
                status = msg["PanelLeds"]
                anomalies = msg["PanelAnomalies"]
            except (KeyError, ValueError):
                raise ParseError("Unexpected response format from the server.")

            # Merge the 'status' and 'anomalies' dictionaries
            merged_dict = {**status, **anomalies}

            # Convert the dict to a snake_case one to simplify the usage in other modules, and sort alphabetically
            new_dict = {
                i: {"name": _camel_to_snake_case(k), "status": v}
                for i, (k, v) in enumerate(sorted(merged_dict.items()))
            }
            _LOGGER.debug(f"Client | Status retrieved: {new_dict}")

            return new_dict
        else:
            raise QueryNotValid()  # pragma: no cover
