""" Keeps track of which tags are in which zones.  Notifies a cabinet 
    object when a tag has entered its zone. Allows user to get a list
    of tags in a zone, and the latest location of a tag.
"""

from net.geo_packet_handler import Geomsg
import logging
from tags import TagLoc, Tags
from typing import Callable
from cabinet import Cabinet


logger = logging.getLogger("app."+__name__)
# logger.propagate = True
# logger.setLevel(logging.INFO)

class Zones():
    """ Class to manage zones.  Holds a dictionary of TagLoc objects.
        Each TagLoc object buffers location data for a tag. """
    def __init__(self, tags:Tags=None):
        self.zones: dict[str, list[int]] = {} # Zone name -> list of tag ids
        if not tags:
            self.tags:Tags = Tags()  # Class that holds all TagLoc objects
        self.cabinets: dict[str, Cabinet] = {}  # Zone name -> Cabinet object
        self.last_zone: dict[int, str] = {}  # Last zone tag was in

    def add_locmon(self, msg:Geomsg):
        """ add a locmon message to Tags.  Update zones with tagid. """
        tagloc = self.tags.add_locmon(msg)  # Add to Tags object
        self.update_zones(tagloc)
        self.inform_cabinet(tagloc)  # Inform the cabinet object of the tag's latest location

    def add_lctn(self, msg:Geomsg):
        """ add a lctn message to Tags.  Update zones with tagid. """
        tagloc = self.tags.add_lctn(msg)  # Add to Tags object
        self.update_zones(tagloc)
        self.inform_cabinet(tagloc)  # Inform the cabinet object of the tag's latest location
        
    def inform_cabinet(self, tag:TagLoc):
        """ Inform the cabinet object of a tag's latest location. """
        zone = tag.get_latest_zone()
        if zone in self.cabinets:
            cabinet = self.cabinets[zone]
            cabinet.new_tag_loc(tag)

    def add_cabinet(self, cabinet:Cabinet, zone_name:str):
        self.cabinets[zone_name] = cabinet

    def update_zones(self, tag:TagLoc):
        """ Update zones dict with latest tag zone. Latest tag is last in the list."""
        zone = tag.get_latest_zone()
        if zone not in self.zones:
            self.zones[zone] = []
            logger.debug(f"Created new zone: {zone}")
        last_zone = self.last_zone.get(tag.tagid, None)
        if last_zone is None:
            self.zones[zone].append(tag)
            logger.debug(f"Tag {tag.tagid} added to zone {zone}")
        else:
            self.zones[last_zone].remove(tag)
            self.zones[zone].append(tag)
            if zone != last_zone:
                logger.debug(f"Tag {tag.tagid} moved from zone {last_zone} to {zone}")  
        self.last_zone[tag.tagid] = zone

    def get_tags_in_zone(self, zone_name:str):
        """ Get all tags in a specific zone """
        return self.zones.get(zone_name, [])
