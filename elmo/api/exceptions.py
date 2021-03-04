class BaseException(Exception):
    """BaseException used for extension."""

    default_message = "BaseException."

    def __init__(self, message=None):
        self.message = message or self.default_message

    def __str__(self):
        return str(self.message)


class ValidationError(BaseException):
    """Exception raised when a Validator fails."""

    default_message = "Client configuration is invalid."


class QueryNotValid(BaseException):
    """Exception raised when a Query is not valid."""

    default_message = "Query not available."


class APIException(BaseException):
    """Exception raised when there is an API error."""

    default_message = "A server error occurred"


class MissingToken(APIException):
    """Exception raised when a client is used without prior authentication."""

    default_message = "No token is present. You must authenticate to use the client."


class LockNotAcquired(BaseException):
    """Exception raised when a Lock() is required to run the function."""

    default_message = "System lock not acquired"
