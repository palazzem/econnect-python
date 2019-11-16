from elmo.utils.parser import get_access_token, get_listed_items


def test_retrieve_access_token():
    """Should retrieve an access token from the given HTML page."""
    html = """<script type="text/javascript">
        var apiURL = 'https://example.com';
        var sessionId = '00000000-0000-0000-0000-000000000000';
        var canElevate = '1';
    """
    token = get_access_token(html)
    assert token == "00000000-0000-0000-0000-000000000000"


def test_retrieve_access_token_wrong():
    """Should retrieve an access token from the given HTML page."""
    html = """<script type="text/javascript">
        var apiURL = 'https://example.com';
        var sessionId = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa';
        var canElevate = '1';
    """
    token = get_access_token(html)
    assert token is None


def test_retrieve_access_token_empty():
    """Should retrieve an access token from the given HTML page."""
    token = get_access_token("")
    assert token is None


def test_retrieve_areas_names(areas_html):
    """Should retrieve Areas names from a raw HTML page."""
    items = get_listed_items(areas_html)
    assert items == ["Entryway", "Corridor"]


def test_retrieve_inputs_names(inputs_html):
    """Should retrieve Inputs names from a raw HTML page."""
    items = get_listed_items(inputs_html)
    assert items == ["Main door", "Window", "Shade"]
