import pytest

from elmo.conf.exceptions import InvalidConfig
from elmo.conf.options import Option


def test_default_constructor():
    """Should create a permissive config option"""
    option = Option()
    assert option.read_only is False
    assert option.required is False
    assert option.allow_null is True
    assert option.validators == []


def test_invalid_required_default():
    """Should raise an exception if invalid configuration is used"""
    with pytest.raises(InvalidConfig):
        Option(required=True)


def test_valid_required_default():
    """Should accept required kwarg with a default"""
    option = Option(required=True, default="test")
    assert option.required is True
    assert option.default == "test"


def test_validators_list():
    """Should expect validators to be a list"""

    def fn():
        pass

    option = Option(validators=[fn])
    assert option.validators == [fn]
