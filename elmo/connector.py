from requests import Session

from . import settings


class Connector(object):
    """Connector class provides all the functionalities to connect
    to an Elmo system. It stores login tokens via `Session` cookies
    and exposes actions. Available actions are:
        * `access` to have credentials to operate with the system
        * `disable` to deactivate the alerting system
        * `enable` to activate the alerting system
    """
    def __init__(self):
        # Connector Session must be preserved when operating
        # the system
        self._session = Session()

    def access(self, username, password, code):
        """Uses credentials to gain a login token via Cookies
        and then unlock the system with the given code
        """
        pass

    def disable(self):
        """Deactivate the system"""
        pass

    def enable(self):
        """Activate the system"""
        pass
