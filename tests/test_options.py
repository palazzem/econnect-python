import pytest

from elmo.conf.options import Option
from elmo.conf.exceptions import ValidationError


def test_default_constructor():
    """Should create a permissive config option"""
    option = Option()
    assert option.value is None
    assert option.default is None
    assert option.validators == []


def test_default_change_value():
    """Setting a default should change the value"""
    option = Option(default="test")
    assert option.value == "test"


def test_validators_list():
    """Should expect validators to be a list"""

    def fn(value):
        pass

    option = Option(validators=[fn])
    assert option.validators == [fn]


def test_validators_not_alist():
    """Should fail if validators are not a list"""

    def fn(value):
        pass

    with pytest.raises(TypeError):
        Option(validators=fn)


def test_validate_ok():
    """Validate should succeed with permissive defaults"""
    option = Option()
    assert option._validate() == (True, [])


def test_validate_allow_null_ok():
    """Validate should succeed if the field has None value"""
    option = Option(allow_null=True)
    option.value = None
    assert option._validate() == (True, [])


def test_validate_allow_null_fail():
    """Validate should fail if the field has None value"""
    option = Option(allow_null=False)
    option.value = None
    assert option._validate() == (False, [{"not_null": "The value must not be None"}])


def test_validate_with_validators_ok():
    """Validate should succeed if validators return True"""

    def v1(value):
        return True

    def v2(value):
        return True

    option = Option(validators=[v1, v2])
    assert option._validate() == (True, [])


def test_validate_with_all_validators_fail():
    """Validate should fail if all validators return False"""

    def v1(value):
        raise ValidationError("test")

    def v2(value):
        raise ValidationError("test")

    option = Option(validators=[v1, v2])
    assert option._validate() == (False, [{"v1": "test"}, {"v2": "test"}])


def test_validate_with_validators_fail():
    """Validate should fail if a validator returns False"""

    def v1(value):
        return True

    def v2(value):
        raise ValidationError("test")

    option = Option(validators=[v1, v2])
    assert option._validate() == (False, [{"v2": "test"}])
