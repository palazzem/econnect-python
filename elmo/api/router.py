class Router(object):
    """API router class that holds a list of endpoints
    grouped by action type.
    """

    def __init__(self, base_url):
        self._base_url = base_url

    @property
    def auth(self):
        return "{}/api/login".format(self._base_url)

    @property
    def strings(self):
        return "{}/api/strings".format(self._base_url)

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
    def areas(self):
        return "{}/api/areas".format(self._base_url)

    @property
    def inputs(self):
        return "{}/api/inputs".format(self._base_url)
