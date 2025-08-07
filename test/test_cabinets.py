""" Test the Cabinet class and the Cluster class with pytest"""
import pytest
from cabinet import Cabinet, Cluster
from net.geo_packet_handler import Geomsg
from tags import TagLoc, Tags

@pytest.fixture
def sample_cabinet_config():
    """Sample configuration for a cabinet"""
    return [{
        'cabinet_controller_id': 1,
        'zone': 'ZoneA',
        'height': 100,
    },]

@pytest.fixture
def sample_tagloc():
    """Sample TagLoc object"""
    tagloc = TagLoc(tagid=123)
    return tagloc

def test_cabinet_initialization(sample_cabinet_config):
    """Test if a Cabinet object is initialized correctly"""
    def dummy_send_fnc(msg):
        """Dummy function to simulate sending a message"""
        pass
    cabinet_obj = Cabinet(sample_cabinet_config[0], dummy_send_fnc)
    assert cabinet_obj.id == 1
    assert cabinet_obj.zone == 'ZoneA'
    assert cabinet_obj.send_geo_cmd == dummy_send_fnc


def test_cluster_initialization(sample_cabinet_config):
    """Test if a Cluster object is initialized correctly"""
    def dummy_send_fnc(msg):
        """Dummy function to simulate sending a message"""
        pass
    cluster_obj = Cluster({'cabinets': sample_cabinet_config}, dummy_send_fnc)
    assert len(cluster_obj.cabinets) == 1   


def test_new_tag_loc_calls_send_fnc(sample_cabinet_config, sample_tagloc):
    """Test if Cabinet.new_tag_loc calls the send function with correct Geomsg"""
    sent_msgs = []

    def dummy_send_fnc(msg):
        sent_msgs.append(msg)

    cabinet_obj = Cabinet(sample_cabinet_config[0], dummy_send_fnc)
    tags = Tags()

    assert len(sent_msgs) == 1
    assert isinstance(sent_msgs[0], Geomsg)
    assert sent_msgs[0].tag_id == tag_id
    assert sent_msgs[0].location == location




