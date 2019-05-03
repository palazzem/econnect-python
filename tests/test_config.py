import pytest

from elmo.conf.config import BaseConfig
from elmo.conf.options import Option
from elmo.conf.exceptions import OptionNotAvailable


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
