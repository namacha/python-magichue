class HTTPError(Exception):
    """An error on HTTP connection"""

    pass


class MagicHueAPIError(Exception):
    """Something gone wrong on MagicHue API"""

    pass


class InvalidData(Exception):
    """Received data is invalid"""

    pass


class DeviceOffline(Exception):
    """Device is offline"""

    pass


class DeviceDisconnected(Exception):
    """Local device is disconnected"""

    pass
