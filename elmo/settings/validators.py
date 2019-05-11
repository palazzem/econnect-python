from urllib.parse import urlparse

from .exceptions import ValidationError


def not_null(value):
    """Validate if Option is not None.
    Args:
        value: the Option value.
    Raises:
        ValidationError: if the Option is None
    """
    if value is None or value == "":
        raise ValidationError("The value must not be None")

    return True


def is_https_url(value):
    """Validate if the Option is a valid URL with HTTPS schema.

    Args:
        value: the Option value.
    Raises:
        ValidationError: if the Option is not a valid URL with 'https' schema
    """
    url = urlparse(value)

    if url.scheme != "https":
        raise ValidationError("The schema must be HTTPS")

    if url.netloc is None or url.netloc == "":
        raise ValidationError("The URL is missing the net location")

    return True
