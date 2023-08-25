import pytest

from elmo.api.exceptions import ValidationError
from elmo.api.router import Router


def test_https_is_required():
    """Should accept only HTTPS URLs."""
    with pytest.raises(ValidationError):
        Router("http://connect.elmospa.com")
