from uuid import UUID


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
