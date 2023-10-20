import logging
import re
from functools import lru_cache

_LOGGER = logging.getLogger(__name__)


def _sanitize_session_id(session_id):
    """Obfuscates a session ID, preserving the first 8 characters and dashes.

    This function retains the first 8 characters of the given session ID, and replaces
    the subsequent characters with 'X', except for dashes, which are preserved.

    Args:
        session_id (str): The session ID to be sanitized.

    Returns:
        str: The sanitized session ID.
    """
    sanitized = session_id[:8] + "".join("-" if char == "-" else "X" for char in session_id[8:])
    return sanitized


@lru_cache(maxsize=42)
def _camel_to_snake_case(name):
    """
    Convert a CamelCase string to snake_case.

    This function implements an LRU cache to avoid doing the operation multiple times. As
    it is used with a very limited set of inputs, the cache size is set to 42 as the usual
    expected input is 21 distinct strings.

    Args:
        name (str): The CamelCase string to be converted.

    Returns:
        str: The converted snake_case string.

    Example:
        >>> _camel_to_snake_case("CamelCaseString")
        'camel_case_string'
    """
    # Handle the all-uppercase special case first
    if name.isupper():
        return name.lower()

    # Convert camelCased portions to snake_case
    name = re.sub("([a-z0-9])([A-Z])", r"\1_\2", name)

    # Insert underscores between letters and digits
    name = re.sub("([a-z])([0-9])", r"\1_\2", name)
    name = re.sub("([0-9])([a-z])", r"\1_\2", name)

    # Replace non-alphanumeric characters (excluding underscores) with underscores
    name = re.sub(r"[^\w]", "_", name)

    # Handle the remaining uppercase letters
    name = name.lower()

    return name
