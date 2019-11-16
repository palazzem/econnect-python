class APIException(Exception):
    """Exception raised when there is an API error."""

    default_message = "A server error occurred"

    def __init__(self, message=None):
        self.message = message or self.default_message

    def __str__(self):
        return str(self.message)


class PermissionDenied(APIException):
    """Exception raised when a user doesn't have permission to perform this action."""

    default_message = "You do not have permission to perform this action"


class LockNotAcquired(Exception):
    """Exception raised when a Lock() is required to run the function."""

    default_message = "System lock not acquired"
