class ValidationError(Exception):
    """Exception raised when a Validator fails."""

    pass


class ConfigNotValid(Exception):
    """Exception raised when any validator fails for a Config object."""

    pass


class OptionNotAvailable(Exception):
    """The Option is not available in the current configuration."""

    pass
