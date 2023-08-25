from urllib.parse import urlparse

from .exceptions import ValidationError


class Router(object):
    """API router class that holds a list of endpoints
    grouped by action type.
    """

    def __init__(self, base_url):
        # Enforce the value is a valid URL behind HTTPS
        base_url = base_url or "https://connect.elmospa.com"
        url = urlparse(base_url)
        if url.scheme != "https":
            raise ValidationError("The schema must be HTTPS")

        self._base_url = base_url

    @property
    def auth(self):
        return "{}/api/login".format(self._base_url)

    @property
    def descriptions(self):
        return "{}/api/strings".format(self._base_url)

    @property
    def update(self):
        return "{}/api/updates".format(self._base_url)

    @property
    def lock(self):
        return "{}/api/panel/syncLogin".format(self._base_url)

    @property
    def unlock(self):
        return "{}/api/panel/syncLogout".format(self._base_url)

    @property
    def send_command(self):
        return "{}/api/panel/syncSendCommand".format(self._base_url)

    @property
    def sectors(self):
        return "{}/api/areas".format(self._base_url)

    @property
    def inputs(self):
        return "{}/api/inputs".format(self._base_url)
