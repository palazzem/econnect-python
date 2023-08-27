import logging

_LOGGER = logging.getLogger(__name__)


def _filter_data(data, key, status):
    """Filters the given data based on the provided key and status.

    This function attempts to filter the data dictionary based on the key and status
    provided. If the key is not found in the data, an error is logged, and an empty
    dictionary is returned.

    Args:
        data (dict): The dictionary containing the data to be filtered.
        key (str): The key in the data dictionary to filter on.
        status (bool): The status value to filter the data by.

    Returns:
        dict: A filtered dictionary containing only items that match the given status.

    Raises:
        KeyError: If the key is not found in the data dictionary. This exception is caught
            and handled within the function by logging an error and returning an empty
            dictionary.
    """
    try:
        if not data or not key:
            return {}
        filtered_data = {k: v for k, v in data[key].items() if v["status"] == status}
    except KeyError as err:
        _LOGGER.error(f"Utils | Error filtering {key} query: {err}")
        raise err
    return filtered_data
