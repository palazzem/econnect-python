import pytest

from elmo.conf.config import BaseConfig
from elmo.conf.options import Option
from elmo.conf.exceptions import OptionNotAvailable, ConfigNotValid


def test_config_constructor():
    """Should contain options registry only for attributes of type Option"""

    class ConfigTest(BaseConfig):
        home = Option()
        url = Option()
        objects = []

    config = ConfigTest()
    assert config._options == ["home", "url"]


def test_config_set_value():
    """Should set the underlying Option value"""

    class ConfigTest(BaseConfig):
        home = Option()

    config = ConfigTest()
    config.home = "test"
    option = config._get_option("home")
    assert option.value == "test"


def test_config_get_value():
    """Should get the underlying Option value"""

    class ConfigTest(BaseConfig):
        home = Option()

    config = ConfigTest()
    option = config._get_option("home")
    option.value = "test"
    assert config.home == "test"


def test_config_set_value_not_available():
    """Should raise an exception if the option is not present"""

    class ConfigTest(BaseConfig):
        pass

    config = ConfigTest()
    with pytest.raises(OptionNotAvailable):
        config.test = "test"


def test_config_get_value_not_available():
    """Should raise an exception if the option is not present"""

    class ConfigTest(BaseConfig):
        pass

    config = ConfigTest()
    with pytest.raises(OptionNotAvailable):
        config.test


def test_config_is_valid_all_options(mocker):
    """Should validate all Option attributes"""

    class ConfigTest(BaseConfig):
        option1 = Option()
        option2 = Option()

    config = ConfigTest()
    option1 = config._get_option("option1")
    option2 = config._get_option("option2")

    # Mock config options
    mocker.patch.object(option1, "_validate", return_value=(True, []))
    mocker.patch.object(option2, "_validate", return_value=(True, []))

    config.is_valid()
    assert option1._validate.call_count == 1
    assert option2._validate.call_count == 1


def test_config_is_valid(mocker):
    """Should return a success if the configuration is valid"""

    class ConfigTest(BaseConfig):
        home = Option()

    config = ConfigTest()
    option = config._get_option("home")

    # Mock config options
    mocker.patch.object(option, "_validate", return_value=(True, []))

    assert config.is_valid() == (True, [])


def test_config_is_not_valid(mocker):
    """Should return a failure if the configuration is not valid and raise_exception is False"""

    class ConfigTest(BaseConfig):
        home = Option()

    config = ConfigTest()
    option = config._get_option("home")

    # Mock config options
    mocker.patch.object(
        option, "_validate", return_value=(False, ["allow_null", "validator"])
    )

    assert config.is_valid(raise_exception=False) == (
        False,
        [{"home": ["allow_null", "validator"]}],
    )


def test_config_is_not_valid_exception(mocker):
    """Should raise an exception if the configuration is not valid and raise_exception is True"""

    class ConfigTest(BaseConfig):
        home = Option()

    config = ConfigTest()
    option = config._get_option("home")

    # Mock config options
    mocker.patch.object(option, "_validate", return_value=(False, ["validator"]))

    with pytest.raises(ConfigNotValid):
        assert config.is_valid()
