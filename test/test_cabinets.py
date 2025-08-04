""" Test the Cabinet class and the Cluster class with pytest"""
import pytest
from cabinet import Cabinet, Cluster

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
