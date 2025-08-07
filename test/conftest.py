import pytest
from tags import Tags, TagLoc, MAX_LOC_BUFF_LEN
from cabinet import Cabinet, Cluster
from net.geo_packet_handler import Geomsg

class DummyGeomsg:
    """Dummy Geomsg to mimic the structure used in tags.py"""
    def __init__(self, fmsg):
        self.fmsg = fmsg
    def __getitem__(self, idx):
        return self.fmsg[idx]

@pytest.fixture
def sample_fmsg():
    # [ts, msgtype, tagid, name, zone, isalert, baoundary, motion, isloc, rngcnt, rngerr, prircv, prirng, x, y, z]
    return [
        123456, "locmon", 42, "Tag42", "ZoneA", 0, 0, 1, 1, 5, 0.1, 1, 2.5, 10.0, 20.0, 5.0
    ]

@pytest.fixture
def sample_cabinet_config():
    """Sample configuration for a cabinet"""
    return [{
        'cabinet_controller_id': 1,
        'zone': 'ZoneA',
        'shelf_height': 1.0,
        'shelf_width': 2.66,
        'location': (87.42, 13.0, 0.396)
    },]

@pytest.fixture
def sample_tagloc(sample_fmsg):
    """Sample TagLoc object"""
    tagloc = TagLoc(tagid=123)
    msg = DummyGeomsg(sample_fmsg)
    tagloc.add_locmon(msg)
    return tagloc

@pytest.fixture
def sample_tag_obj():
    """Sample TagLoc object"""
    tags = Tags()
    msg = DummyGeomsg(sample_fmsg)
    tagloc.add_locmon(msg)
    return tagloc