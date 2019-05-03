from .options import Option
from .exceptions import OptionNotAvailable


class BaseConfig(object):
    """Configuration base class that must be extended to define application settings.
    Every setting must be of type ``Option`` otherwise it's not taken in consideration
    during the validation process.

    Example:

        class Settings(BaseConfig):
            url = Option()
            dry_run = Option(validators=[is_a_boolean])

        settings = Settings()
        settings.url = "http://example.com""
        settings.dry_run = False
        settings.is_valid()  # returns True
    """

    def __init__(self):
        """Store options defined as class attributes in a local registry."""
        self._options = []
        for attr, value in self.__class__.__dict__.items():
            option = self._get_option(attr)
            if isinstance(option, Option):
                self._options.append(attr)

    def __setattr__(self, name, value):
        """Config attributes must be of type Option. This setattr() ensures that the
        Option.value is properly set.

        Args:
            name: the name of the attribute.
            value: the value of the attribute.
        Raise:
            OptionNotAvailable: set attribute is not present as class Attribute.
        """
        if name == "_options":
            object.__setattr__(self, name, value)
            return

        if name in object.__getattribute__(self, "_options"):
            option = self._get_option(name)
            option.value = value
        else:
            raise OptionNotAvailable("the option is not present in the current config")

    def __getattribute__(self, name):
        """Config attributes must be of type Option. This getattr() ensures that the
        Option.value is properly get.

        Args:
            name: the attribute name to retrieve.
        Return:
            The Option value if the attribute is in the options list. Otherwise
            ``object.__getattribute__()`` is called.
        """
        if name in object.__getattribute__(self, "_options"):
            option = self._get_option(name)
            return option.value
        else:
            return object.__getattribute__(self, name)

    def __getattr__(self, name):
        """``__getattr__`` is called whenever the ``__getattribute__()`` didn't
        find the attribute. In that case it means the given attribute is not
        a configuration option that was defined as class attributes.

        Args:
            name: the attribute name to retrieve.
        Raise:
            OptionNotAvailable: the configuration option is not present.
        """
        raise OptionNotAvailable("the option is not present in the current config")

    def _get_option(self, name):
        """Retrieve the Option instance instead of proxying the call to retrieve
        the ``Option.value``.

        Args:
            name: the ``Option`` name.

        Return:
            An ``Option`` instance.
        """
        return object.__getattribute__(self, name)

    def is_valid(self, raise_exception=True):
        """TODO: missing implementation"""
        pass
