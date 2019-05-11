import pytest

from elmo.conf.exceptions import ValidationError
from elmo.conf.validators import not_null, is_https_url


def test_not_null_boolean():
    """Should succeed with a not None value"""
    assert not_null(True) is True
    assert not_null(False) is True


def test_not_null_with_string():
    """Should succeed with a not None value"""
    assert not_null("test") is True


def test_not_null_with_number():
    """Should succeed with a not None value"""
    assert not_null(0) is True
    assert not_null(42) is True


def test_not_null_with_false():
    """Should fail with a None value"""
    with pytest.raises(ValidationError):
        not_null(None)


def test_not_null_with_empty_string():
    """Should fail with an empty string"""
    with pytest.raises(ValidationError):
        not_null("")


def test_url_validator():
    """Should succeed with a valid HTTPS URL"""
    assert is_https_url("https://example.com") is True


def test_url_without_schema():
    """Should reject a URL without a schema"""
    with pytest.raises(ValidationError):
        is_https_url("example.com")


def test_url_with_path():
    """Should reject a URL with only a path"""
    with pytest.raises(ValidationError):
        is_https_url("/example.com")


def test_url_wrong_values():
    """Should reject a URL without HTTPS"""
    with pytest.raises(ValidationError):
        is_https_url("http://foo")
