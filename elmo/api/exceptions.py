class AuthenticationFailed(Exception):
    """Exception raised when authentication credentials are incorrect."""

    pass


class PermissionDenied(Exception):
    """Exception raised when a user doesn't have permission to perform this action."""

    pass
