""" This file holds the Cabinet class.  It keeps track of the 
    light switch state on each of the 6 shelves.  It does this
    by monitoring the incoming LTSW messages.  It also keeps track of the
    which tag is on which shelf.  If a light switch state changes to active,
    it will turn on the light for that shelf.  It will also look for a tag 
    that has moved into the cabinegts zone and height.  If the light switch state
    changes to inactive, it will turn off the light for that shelf.  """

from tags import Tags, TagLoc, MAX_LOC_BUFF_LEN
from net.geo_packet_handler import Geomsg
import logging
from typing import Callable


SHELF_PARAM_BASE = 100
LED_OFF = 0
LED_RED = 1
LED_GREEN = 2
LED_BLUE = 4
LED_WHITE = 7


logger = logging.getLogger("app"+".__name__")
# logger = logging.getLogger("__name__")
logger.propagate = False


class Cabinet:
    def __init__(self, cabinet_config: dict, send_fnc: Callable[[str], None]): #controller_id: int, connection, zone: str):
        self.id = cabinet_config['cabinet_controller_id']
        self.zone = cabinet_config['zone']
        self.cmd_conn = send_fnc
        self.tags = [False] * 6
        self.light_switch_states = [False] * 6  # Assuming 6 shelves
        self.light_switch_events = 0 # Indicates new light switch event



    def store_light_switch_state(self, shelf_index, state):
        """Update the light switch state for a given shelf."""
        if 0 <= shelf_index < len(self.light_switch_states):
            self.light_switch_states[shelf_index] = state == 1
            self.light_switch_events |= (1 << shelf_index)
            # send light shelf led msg

    
    def send_shelf_led_msg(self, shelf_num:int, leds:int):
        param = SHELF_PARAM_BASE+shelf_num
        msg=f'RCVPRM, {self.id}, {param}={leds}\r\n'
        self.cmd_conn(msg) # add a callback
        logger.info(f"Send: {msg}")

    
    def add_ltsw_msg(self, msg: Geomsg):
        """Process a light switch message.
        msg format: ['ts':int, 'msgtype':str, 'Controller ID':int, 
                     'Sensor Type': str, 'shelf number': int, 'state':bool] """
        shelf_number = int(msg.fmsg[4])
        sw_state = int(msg.fmsg[5])
        self.store_light_switch_state(shelf_number-1, sw_state)

        
        logger.info(msg.msg)
        color = LED_OFF
        if sw_state == 1:
            color = LED_RED        
        self.send_shelf_led_msg(shelf_number, color)

    def add_locmon_msg(self, msg: Geomsg):
        """Process a location monitoring message."""
        if self.light_switch_events == 0:
            return
        
        tag_id = int(msg.fmsg[2])
        tag_loc = Tags().get_tag(tag_id)
        if tag_loc:
            tag_loc.add_locmon(msg)
            # Check if the tag is in the cabinet's zone and height
            if tag_loc.get_latest_zone() == self.zone:
                # Check if the tag is on a shelf
                shelf_index = self.get_shelf_index(tag_loc)
                if shelf_index is not None:
                    self.tags[shelf_index] = True
                    # If the light switch for that shelf is active, turn on the light
                    if self.light_switch_states[shelf_index]:
                        self.light_switch_events |= (1 << shelf_index)


class Cluster:
    """ A Cluster of Cabinet objects.  It is used to manage multiple cabinets.
        Route LTSW message to the appropriate cabinet. """
    def __init__(self, config: dict, send_fnc: Callable[[str], None]):
        """ create a Cabinet object for each cabinet in the config """
        self.cabinets = {}
        self.ltsw_path = {}
        for cabinet in config.get('cabinets', []):
            cabinet_id = cabinet.get('cabinet_controller_id', None)
            self.cabinets[cabinet_id] = Cabinet(cabinet, send_fnc=send_fnc)
            self.ltsw_path[cabinet_id] = self.cabinets[cabinet_id].add_ltsw_msg

    def add_ltsw_msg(self, msg: Geomsg):
        """ Add a light switch message to the appropriate cabinet. """
        cabinet_id = int(msg.fmsg[2])
        self.ltsw_path[cabinet_id](msg)


    def get_cabinet(self, cabinet_id: int) -> Cabinet:
        """ Get a Cabinet object by its ID. """
        return self.cabinets.get(cabinet_id, None)
