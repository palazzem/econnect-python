class ValidationError(Exception):
    """The configuration is not valid."""

    pass


class OptionNotAvailable(Exception):
    """The Option is not available in the current configuration."""

    pass
