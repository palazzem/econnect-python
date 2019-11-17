import pytest
import responses

from elmo.api.client import ElmoClient


@pytest.fixture
def client():
    """Create an ElmoClient with a default base URL."""
    client = ElmoClient("https://example.com", "vendor")
    yield client


@pytest.fixture
def server():
    """Create a `responses` mock."""
    with responses.RequestsMock() as resp:
        yield resp


@pytest.fixture
def areas_html():
    """HTML raw page fixture for Areas dashboard."""
    return """<div class="row output-table">
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


@pytest.fixture
def inputs_html():
    """HTML raw page fixture for Inputs dashboard."""
    return """<div class="row">
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


@pytest.fixture
def areas_data():
    return """[{"Active":true,"ActivePartial":false,"Max":false,"Activable":true,"ActivablePartial":false,"InUse":true,"Id":1,"Index":0,"Element":1,"CommandId":0,"InProgress":false},{"Active":false,"ActivePartial":false,"Max":false,"Activable":true,"ActivablePartial":false,"InUse":true,"Id":2,"Index":1,"Element":1,"CommandId":0,"InProgress":false}]"""


@pytest.fixture
def inputs_data():
    return """[{"Alarm":false,"MemoryAlarm":false,"Excluded":false,"InUse":true,"IsVideo":false,"Id":1,"Index":0,"Element":1,"CommandId":0,"InProgress":false},{"Alarm":false,"MemoryAlarm":false,"Excluded":false,"InUse":true,"IsVideo":false,"Id":2,"Index":1,"Element":1,"CommandId":0,"InProgress":false}]"""
