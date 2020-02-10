from uuid import UUID
from bs4 import BeautifulSoup
import re


def get_access_token(html):
    """Retrieve the access token from a HTML page.

    Args:
        html: the HTML body containing the access token
    Returns:
        A string with the access token, None otherwise
    """
    start = html.find("var sessionId = '") + 17
    end = start + 36
    token = html[start:end]

    try:
        # Validate if the token is a valid UUID
        UUID(token, version=4)
    except ValueError:
        token = None

    return token


def get_listed_items(html):
    """Retrieve items listed inside a HTML Table object. This
    function is used to extract Areas and Input names from a raw
    HTML page.

    Args:
        html: the HTML body containing the access token
    Returns:
        A list with the associated names (if any)
    """
    tree = BeautifulSoup(html, "html.parser")
    rows = tree.select("tbody > tr")
    return [x.getText().split("\n")[1] for x in rows]


def get_api_url(html):
    """Retrieve the url for API requests from a HTML page.

    Args:
        html: the HTML body containing the apiURL
    Returns:
        A string with the apiURL, None otherwise
    """
    apiURL = re.search(r"var apiURL = '(.+)/api/';", html).group(1)

    return apiURL
    