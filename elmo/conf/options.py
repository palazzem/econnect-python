class Option(object):
    """Settings option that includes built-in validation."""

    def __init__(self, default=None, allow_null=True, validators=None):
        """Initialize the option field with permissive defaults.
        By default the field is not required and None value is permitted.
        """
        self.value = default if default else None
        self.default = default
        self.allow_null = allow_null

        if validators is not None:
            self.validators = list(validators)
        else:
            self.validators = []

    def _validate(self):
        """Validate this Option based on attributes and validators.

        Return:
            A boolean that is True if the option honors all validators, False otherwise.
        """
        failed_validators = []
        if self.allow_null is False and self.value is None:
            failed_validators.append("allow_null")

        for validator in self.validators:
            if validator(self.value) is False:
                failed_validators.append(validator.__name__)

        is_valid = len(failed_validators) == 0
        return is_valid, failed_validators
