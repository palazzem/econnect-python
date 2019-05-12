class APIException(Exception):
    """Exception raised when there is an API error."""

    pass


class PermissionDenied(APIException):
    """Exception raised when a user doesn't have permission to perform this action."""

    pass


class LockNotAcquired(Exception):
    """Exception raised when a Lock() is required to run the function."""

    pass
