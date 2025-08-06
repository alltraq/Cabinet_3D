""" Create and manage Tag class """

from net.geo_packet_handler import Geomsg
from collections import deque
import logging


MAX_LOC_BUFF_LEN = 10




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
        """ add lomon msg to que. 
         tag message format: ['ts':int, 'msgtype':str, 'tagid':int, 'name':str, /
                          'zone':str, 'isalert':int, 'boundary':int, 'motion':int, /
                          'isloc':int, 'rngcnt':int, 'rngerr':float, 'prircv':int, /
                          'prirng':float, 'x':float, 'y':float, 'z':float]
        """
        try:
            self.ts.append(int(msg.fmsg[0]))
            self.x.append(float(msg.fmsg[13]))
            self.y.append(float(msg.fmsg[14]))
            self.z.append(float(msg.fmsg[15]))
            self.zone.append(msg.fmsg[4])
            self.motion.append(bool(msg.fmsg[7]))
        except Exception as e:
            logging.exception("TagLoc.add_locmon exception:", e)

    def add_lctn(self, msg:Geomsg):
        """ add LCTN message to queue.
           LCTN message format: ['ts':int, 'msgtype':str, 'tagid':int, 'tagname':str,
                         'zonename':str, 'inmotion':int, 'isalert':int, 
                         'rngcnt':int, 'rngerr':float, 'prircv':int, 'prirng':float,
                         'locx':float, 'locy':float, 'locz':float]
        """
        
        try:
            self.ts.append(int(msg.fmsg[0]))
            self.x.append(float(msg.fmsg[11]))
            self.y.append(float(msg.fmsg[12]))
            self.z.append(float(msg.fmsg[13]))
            self.zone.append(msg.fmsg[4])
            self.motion.append(bool(msg.fmsg[5]))
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

class Tags():
    """ Class to manage tags.  Holds a dictionary of TagLoc objects.
        Each TagLoc object buffers location data for a tag. """
    def __init__(self):
        self.tags = {}

    def add_locmon(self, msg:Geomsg) -> TagLoc:
        """ add a locmon message to the appropriate tag.  Create a new TagLoc
            object if the tag does not exist. """
        tagid = int(msg.fmsg[2])  # tagid is at index 2
        if tagid not in self.tags:
            self.tags[tagid] = TagLoc(tagid)
        self.tags[tagid].add_locmon(msg)
        return self.tags[tagid]

    def add_lctn(self, msg:Geomsg) -> TagLoc:
        """ add a lctn message to the appropriate tag.  Create a new TagLoc
            object if the tag does not exist. """
        tagid = int(msg.fmsg[2])  # tagid is at index 2
        if tagid not in self.tags:
            self.tags[tagid] = TagLoc(tagid)
        self.tags[tagid].add_lctn(msg)
        return self.tags[tagid]


    # def __setitem__(self, tagid:int, tagloc:TagLoc):
    #     """ Allow Tags object to be used like a dictionary """
    #     self.tags[tagid] = tagloc

    def __getitem__(self, tagid:int) -> TagLoc:
        """ Allow Tags object to be used like a dictionary """
        return self.tags.get(tagid, None)
    
    def __contains__(self, tagid:int) -> bool:
        """ Check if a tag exists in the Tags object """
        return tagid in self.tags

    # def add_tag(self, tagid:int):
    #     """ add a new tag to the tags dict """
    #     if tagid not in self.tags:
    #         self.tags[tagid] = TagLoc(tagid)
        

    def get_tag(self, tagid:int) -> 'TagLoc':
        """ get a TagLoc object for the given tagid """
        return self.tags.get(tagid, None)
    