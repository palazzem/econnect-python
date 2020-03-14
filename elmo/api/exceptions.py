class BaseException(Exception):
    """BaseException used for extension."""

    default_message = "BaseException."

    def __init__(self, message=None):
        self.message = message or self.default_message

    def __str__(self):
        return str(self.message)


class QueryNotValid(BaseException):
    """Exception raised when a Query is not valid."""

    default_message = "Query not available."


class APIException(BaseException):
    """Exception raised when there is an API error."""

    default_message = "A server error occurred"


class PermissionDenied(APIException):
    """Exception raised when a user doesn't have permission to perform this action."""

    default_message = "You do not have permission to perform this action"


class LockNotAcquired(Exception):
    """Exception raised when a Lock() is required to run the function."""

    default_message = "System lock not acquired"
