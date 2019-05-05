from . import validators as v
from .exceptions import ValidationError


class Option(object):
    """Settings option that includes built-in validation."""

    def __init__(self, default=None, allow_null=True, validators=None):
        """Initialize the option field with permissive defaults.
        By default the field is not required and None value is permitted.
        """
        self.value = default if default else None
        self.default = default

        if validators is not None:
            self.validators = list(validators)
        else:
            self.validators = []

        # Some validators are available via kwarg because they're common
        # and generic enough. If a validator is too specific, it must
        # be added in the ``validators`` module.
        if allow_null is False:
            self.validators.append(v.not_null)

    def _validate(self):
        """Validate this Option based on attributes and validators.

        Return:
            A boolean that is True if the option honors all validators, False otherwise.
        """
        failed_validators = []

        for validator in self.validators:
            # Validators must raise a ValidationError. Exception message
            # is used to bubble up the failure reason.
            try:
                validator(self.value)
            except ValidationError as e:
                failed_validators.append({validator.__name__: "{}".format(e)})

        is_valid = len(failed_validators) == 0
        return is_valid, failed_validators
