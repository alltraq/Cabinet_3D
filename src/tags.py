""" Create an manage Tag class """

from net.geo_packet_handler import Geomsg
from collections import deque

MAX_LOC_BUFF_LEN = 10

class Tags():
    """ Class to manage tags.  Holds a dictionary of TagLoc objects.
        Each TagLoc object buffers location data for a tag. """
    def __init__(self):
        self.tags = {}

    def add_locmon(self, msg:Geomsg):
        """ add a locmon message to the appropriate tag.  Create a new TagLoc
            object if the tag does not exist. 
         tag message format: ['ts':int, 'msgtype':str, 'tagid':int, 'name':str, /
                          'zone':str, 'isalert':int, 'baoundary':int, 'motion':int, /
                          'isloc':int, 'rngcnt':int, 'rngerr':float, 'prircv':int, /
                          'prirng':float, 'x':float, 'y':float, 'z':float] """
        tagid = msg.fmsg[2]  # tagid is at index 2
        if tagid not in self.tags:
            self.add_tag(tagid)
        self.tags[tagid].add_locmon(msg)

    def add_tag(self, tagid:int):
        """ add a new tag to the tags dict """
        if tagid not in self.tags:
            self.tags[tagid] = TagLoc(tagid)

    def get_tag(self, tagid:int) -> 'TagLoc':
        """ get a TagLoc object for the given tagid """
        return self.tags.get(tagid, None)


class TagLoc():
    """ Buffers up location data for a tag. Gets the latest location, mean, median.
        Gets the latest zone. """
    def __init__(self, tagid:int, max_len:int=MAX_LOC_BUFF_LEN):
        self.tagid = tagid
        self.x = deque(maxlen=max_len)
        self.y = deque(maxlen=max_len)
        self.z = deque(maxlen=max_len)
        self.zone = deque(maxlen=max_len)
        self.motion = deque(maxlen=max_len)
        self.ts = deque(maxlen=max_len)


    def add_locmon(self, msg:Geomsg):
        """ add lomon msg to que """
        try:
            self.ts.append(int(msg[0]))
            self.x.append(float(msg[13]))
            self.y.append(float(msg[14]))
            self.z.append(float(msg[15]))
            self.zone.append(msg[4])
            self.motion.append(bool(msg[3]))
        except Exception as e:
            print("TagLoc.add_locmon exception:", e)


    def get_latest_location(self) -> tuple[float, float, float]:
        """ get the last x, y, z location """
        return (self.x[-1], self.y[-1], self.z[-1])

    def get_mean_location(self) -> tuple[float, float, float]:
        pass

    def get_median_location(self) -> tuple[float, float, float]:
        pass

    def get_latest_height(self):
        pass

    def get_average_height(self):
        pass

    def get_median_height(self):
        pass

    def get_latest_zone(self):
        return self.zone[-1] if len(self.zone) > 0 else None
