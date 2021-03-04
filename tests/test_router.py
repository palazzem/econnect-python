import pytest

from elmo.api.router import Router
from elmo.api.exceptions import ValidationError


def test_https_is_required():
    """Should accept only HTTPS URLs."""
    with pytest.raises(ValidationError):
        Router("http://connect.elmospa.com")
