""" Test the Cabinet class and the Cluster class with pytest"""
import pytest
from cabinet import Cabinet, Cluster
from net.geo_packet_handler import Geomsg

@pytest.fixture
def sample_cabinet_config():
    """Sample configuration for a cabinet"""
    return [{
        'cabinet_controller_id': 1,
        'zone': 'ZoneA',
        'height': 100,
    },]

def test_cabinet_initialization(sample_cabinet_config):
    """Test if a Cabinet object is initialized correctly"""
    def dummy_send_fnc(msg):
        """Dummy function to simulate sending a message"""
        pass
    cabinet_obj = Cabinet(sample_cabinet_config[0], dummy_send_fnc)
    assert cabinet_obj.id == 1
    assert cabinet_obj.zone == 'ZoneA'
    assert cabinet_obj.cmd_conn == dummy_send_fnc


def test_cluster_initialization(sample_cabinet_config):
    """Test if a Cluster object is initialized correctly"""
    def dummy_send_fnc(msg):
        """Dummy function to simulate sending a message"""
        pass
    cluster_obj = Cluster({'cabinets': sample_cabinet_config}, dummy_send_fnc)
    assert len(cluster_obj.cabinets) == 1   

def test_cabinet_add_ltsw_msg(sample_cabinet_config):
    """Test if a light switch message is processed correctly"""
    test_msg = {}

    def test_send_fnc(msg):
        """Dummy function to simulate sending a message"""
        test_msg['value'] = msg

    cabinet_obj = Cabinet(sample_cabinet_config[0], test_send_fnc)
    
    # Simulate a light switch message
    msg = Geomsg("123456,SENS0,1,LTSW,1,1\r\n")
    cabinet_obj.add_ltsw_msg(msg)
    
    # Check if the light switch state is updated
    assert cabinet_obj.light_switch_states[0] is True
    assert test_msg['value'] == "RCVPRM, 1, 101=1\r\n"

