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
    def lock(self):
        return "{}/api/panel/syncLogin".format(self._api_url)

    @property
    def unlock(self):
        return "{}/api/panel/syncLogout".format(self._api_url)

    @property
    def send_command(self):
        return "{}/api/panel/syncSendCommand".format(self._api_url)

    @property
    def areas(self):
        return "{}/api/areas".format(self._api_url)

    @property
    def areas_list(self):
        # Returns a HTML page that requires parsing
        return "{}/{}/Areas".format(self._base_url, self._vendor)

    @property
    def inputs(self):
        return "{}/api/inputs".format(self._api_url)

    @property
    def inputs_list(self):
        # Returns a HTML page that requires parsing
        return "{}/{}/Inputs".format(self._base_url, self._vendor)
