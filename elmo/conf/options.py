from .exceptions import InvalidConfig


class Option(object):
    """Settings option that includes built-in validation."""

    def __init__(
        self,
        read_only=False,
        required=False,
        default=None,
        allow_null=True,
        validators=None,
    ):
        """Initialize the option field with permissive defaults.
        By default the field is not required and None value is permitted.
        """
        # Assert invalid kwargs
        if required and not default:
            raise InvalidConfig("Required option cannot default to empty value")

        self.read_only = read_only
        self.required = required
        self.default = default
        self.allow_null = allow_null

        if validators is not None:
            self.validators = list(validators)
        else:
            self.validators = []
