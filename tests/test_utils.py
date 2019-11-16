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


def test_retrieve_areas_names():
    """Should retrieve Areas names from a raw HTML page."""
    html = """<div class="row output-table">
    <table class="input-table footable" data-page-size="5">
        <thead>
            <tr>
                <th class="area-first-column">
                    <h2 data-areaindex="1" id="hAreaName_3">Home</h2>
                </th>
                <th class="center" data-hide="">Status
                </th>
                <th class="center" data-hide="phone">Activable
                </th>
            </tr>
        </thead>
        <tbody>
            <tr class="odd">
                <td data-sectorindex="1" id="tdSectorName_0">Entryway</td>
                <td class="center">
                    <div><a class="status-armed sendcommand" data-commandtype="2" data-elementclass="9" data-index="1" href="javascript:void(0)" id="aArea_0"><i class="icn-status-armed"></i>Enabled</a></div>
                </td>
                <td class="center"><i class="icon-ok" id="iArmable_0"></i></td>
            </tr>
            <tr class="even">
                <td data-sectorindex="2" id="tdSectorName_1">Corridor</td>
                <td class="center">
                    <div><a class="status-armed sendcommand" data-commandtype="2" data-elementclass="9" data-index="2" href="javascript:void(0)" id="aArea_1"><i class="icn-status-armed"></i>Enabled</a></div>
                </td>
                <td class="center"><i class="icon-ok" id="iArmable_1"></i></td>
            </tr>
        </tbody>
    </table>
</div>
    """
    items = get_listed_items(html)
    assert items == ["Entryway", "Corridor"]


def test_retrieve_inputs_names():
    """Should retrieve Inputs names from a raw HTML page."""
    html = """<div class="row">
    <table class="input-table footable" data-page-size="5" id="tblInputs">
        <thead>
            <tr>
                <th>
                    <h2>Input</h2>
                </th>
                <th class="center" data-hide="">Status
                </th>
                <th class="center" data-hide="phone">Memory
                </th>
            </tr>
        </thead>
        <tbody>
            <tr class="odd">
                <td id="tdInput_0">Main door</td>
                <td class="center">
                    <div><a class="status-idle sendcommand" data-commandtype="2" data-elementclass="10" data-index="1" href="javascript:void(0)" id="aInput_0"><i class="icn-status-idle"></i>Wait</a></div>
                </td>
                <td class="center"><i class="icon-dash-gray" id="iMemoryAlarm_0"></i></td>
            </tr>
            <tr class="even">
                <td id="tdInput_1">Window</td>
                <td class="center">
                    <div><a class="status-idle sendcommand" data-commandtype="2" data-elementclass="10" data-index="2" href="javascript:void(0)" id="aInput_1"><i class="icn-status-idle"></i>Wait</a></div>
                </td>
                <td class="center"><i class="icon-dash-gray" id="iMemoryAlarm_1"></i></td>
            </tr>
            <tr class="odd">
                <td id="tdInput_2">Shade</td>
                <td class="center">
                    <div><a class="status-idle sendcommand" data-commandtype="2" data-elementclass="10" data-index="3" href="javascript:void(0)" id="aInput_2"><i class="icn-status-idle"></i>Wait</a></div>
                </td>
                <td class="center"><i class="icon-dash-gray" id="iMemoryAlarm_2"></i></td>
            </tr>
        </tbody>
    </table>
</div>
    """
    items = get_listed_items(html)
    assert items == ["Main door", "Window", "Shade"]
