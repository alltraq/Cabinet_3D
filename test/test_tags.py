import pytest
from tags import Tags, TagLoc, MAX_LOC_BUFF_LEN


class DummyGeomsg:
    """Dummy Geomsg to mimic the structure used in tags.py"""
    def __init__(self, fmsg):
        self.fmsg = fmsg
    def __getitem__(self, idx):
        return self.fmsg[idx]
    

def test_tags_add_and_get_tag(sample_fmsg):
    tags_obj = Tags()
    msg = DummyGeomsg(sample_fmsg)
    tags_obj.add_locmon(msg)
    tagloc = tags_obj.get_tag(42)
    assert isinstance(tagloc, TagLoc)
    assert tagloc.tagid == 42

def test_tagloc_add_locmon_and_latest_location(sample_fmsg):
    tagloc = TagLoc(tagid=42)
    msg = DummyGeomsg(sample_fmsg)
    tagloc.add_locmon(msg)
    x, y, z = tagloc.get_latest_location()
    assert x == 10.0
    assert y == 20.0
    assert z == 5.0

def test_tagloc_zone_and_motion(sample_fmsg):
    tagloc = TagLoc(tagid=42)
    msg = DummyGeomsg(sample_fmsg)
    tagloc.add_locmon(msg)
    assert tagloc.get_latest_zone() == "ZoneA"
    assert tagloc.motion[-1] is True

def test_tags_add_tag_only_once():
    tags_obj = Tags()
    tags_obj.add_tag(100)
    tags_obj.add_tag(100)
    assert len(tags_obj.tags) == 1

def test_tagloc_buffer_length(sample_fmsg):
    tagloc = TagLoc(tagid=1, max_len=3)
    for i in range(5):
        fmsg = sample_fmsg.copy()
        fmsg[13] = float(i)
        fmsg[14] = float(i + 1)
        fmsg[15] = float(i + 2)
        msg = DummyGeomsg(fmsg)
        tagloc.add_locmon(msg)
    assert len(tagloc.x) == 3
    assert tagloc.x[-1] == 4.0
    assert tagloc.x[0] == 2.0
