from elmo.utils.parser import get_access_token


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
