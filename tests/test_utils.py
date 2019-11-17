from elmo.utils.parser import get_access_token, get_listed_items
from elmo.utils.response_helper import slice_list


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


def test_slice_areas():
    """Should slice properly an Area list."""
    items = [
        {
            "Active": True,
            "ActivePartial": False,
            "Max": False,
            "Activable": True,
            "ActivablePartial": False,
            "InUse": True,
            "Id": 1,
            "Index": 0,
            "Element": 1,
            "CommandId": 0,
            "InProgress": False,
        },
        {
            "Active": False,
            "ActivePartial": False,
            "Max": False,
            "Activable": True,
            "ActivablePartial": False,
            "InUse": True,
            "Id": 2,
            "Index": 1,
            "Element": 1,
            "CommandId": 0,
            "InProgress": False,
        },
    ]
    names = ["Entryway", "Corridor"]
    areas_active, areas_inactive = slice_list(items, names, "Active")
    assert len(areas_active) == 1
    assert len(areas_inactive) == 1
    assert areas_active[0] == {"id": 1, "name": "Entryway"}
    assert areas_inactive[0] == {"id": 2, "name": "Corridor"}


def test_slice_inputs():
    """Should slice properly an Input list."""
    items = [
        {
            "Alarm": True,
            "MemoryAlarm": False,
            "Excluded": False,
            "InUse": True,
            "IsVideo": False,
            "Id": 1,
            "Index": 0,
            "Element": 1,
            "CommandId": 0,
            "InProgress": False,
        },
        {
            "Alarm": False,
            "MemoryAlarm": False,
            "Excluded": False,
            "InUse": True,
            "IsVideo": False,
            "Id": 2,
            "Index": 1,
            "Element": 1,
            "CommandId": 0,
            "InProgress": False,
        },
    ]
    names = ["Door", "Window"]
    inputs_alerted, inputs_wait = slice_list(items, names, "Alarm")
    assert len(inputs_alerted) == 1
    assert len(inputs_wait) == 1
    assert inputs_alerted[0] == {"id": 1, "name": "Door"}
    assert inputs_wait[0] == {"id": 2, "name": "Window"}


def test_slice_not_enough_names():
    """Should slice properly an Area list, even if the names list is shorter."""
    items = [
        {
            "Active": True,
            "ActivePartial": False,
            "Max": False,
            "Activable": True,
            "ActivablePartial": False,
            "InUse": True,
            "Id": 1,
            "Index": 0,
            "Element": 1,
            "CommandId": 0,
            "InProgress": False,
        },
        {
            "Active": False,
            "ActivePartial": False,
            "Max": False,
            "Activable": True,
            "ActivablePartial": False,
            "InUse": True,
            "Id": 2,
            "Index": 1,
            "Element": 1,
            "CommandId": 0,
            "InProgress": False,
        },
    ]
    names = ["Entryway"]
    areas_active, areas_inactive = slice_list(items, names, "Active")
    assert len(areas_active) == 1
    assert len(areas_inactive) == 1
    assert areas_active[0] == {"id": 1, "name": "Entryway"}
    assert areas_inactive[0] == {"id": 2, "name": "Unknown"}
