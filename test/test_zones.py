import pytest
from zones import Zones
from tags import TagLoc, Tags
from cabinet import Cabinet
from net.geo_packet_handler import Geomsg

class DummyGeomsg:
    def __init__(self, fmsg):
        self.fmsg = fmsg

@pytest.fixture
def sample_tagloc():
    tagloc = TagLoc(tagid=42)
    tagloc.zone.append("ZoneA")
    return tagloc

@pytest.fixture
def zones_obj():
    return Zones()

def test_add_cabinet(zones_obj):
    cabinet = Cabinet({'cabinet_controller_id': 1, 
                       'zone': 'ZoneA', 
                       'shelf_height': 100, 
                       'location':(0.0 , 0.0, 0.0)}, lambda x: None)
    zones_obj.add_cabinet(cabinet, "ZoneA")
    assert "ZoneA" in zones_obj.cabinets
    assert zones_obj.cabinets["ZoneA"] == cabinet

def test_update_zones_add_new_tag(zones_obj, sample_tagloc):
    zones_obj.update_zones(sample_tagloc)
    assert "ZoneA" in zones_obj.zones
    assert sample_tagloc in zones_obj.zones["ZoneA"]

def test_update_zones_move_tag(zones_obj, sample_tagloc):
    zones_obj.update_zones(sample_tagloc)
    # Simulate tag moving to ZoneB
    sample_tagloc.zone.append("ZoneB")
    zones_obj.last_zone[sample_tagloc.tagid] = "ZoneA"
    zones_obj.update_zones(sample_tagloc)
    assert sample_tagloc not in zones_obj.zones["ZoneA"]
    assert sample_tagloc in zones_obj.zones["ZoneB"]

def test_get_tags_in_zone(zones_obj, sample_tagloc):
    zones_obj.update_zones(sample_tagloc)
    tags_in_zone = zones_obj.get_tags_in_zone("ZoneA")
    assert sample_tagloc in tags_in_zone

def test_inform_cabinet(zones_obj, sample_tagloc):
    called = {}
    class DummyCabinet:
        def new_tag_loc(self, tag):
            called['tagid'] = tag.tagid
    zones_obj.cabinets["ZoneA"] = DummyCabinet()
    zones_obj.inform_cabinet(sample_tagloc)
    assert called['tagid'] == 42

def test_add_locmon(zones_obj):
    # Setup dummy Tags and TagLoc
    fmsg = [
        123456, "LOCMON", 99, "Tag99", "ZoneX", 0, 0, 1, 1, 5, 0.1, 1, 2.5, 10.0, 20.0, 5.0
    ]
    msg = DummyGeomsg(fmsg)
    zones_obj.add_locmon(msg)
    assert "ZoneX" in zones_obj.zones
    taglocs = zones_obj.zones["ZoneX"]
    assert any(t.tagid == 99 for t in taglocs)