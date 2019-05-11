class Router(object):
    """API router class that holds a list of endpoints
    grouped by action type.
    """

    def __init__(self, base_url, vendor):
        self._vendor = vendor
        self._base_url = base_url

    @property
    def auth(self):
        return "{}/{}".format(self._base_url, self._vendor)

    @property
    def connect(self):
        return "{}/api/panel/syncLogin".format(self._base_url)

    @property
    def disconnect(self):
        return "{}/api/panel/syncLogout".format(self._base_url)

    @property
    def send_command(self):
        return "{}/api/panel/syncSendCommand".format(self._base_url)
