""" This file holds the Cabinet class.  It keeps track of the 
    light switch state on each of the 6 shelves.  It does this
    by monitoring the incoming LTSW messages.  It also keeps track of the
    which tag is on which shelf.  If a light swith state changes to active,
    it will turn on the light for that shelf.  It will also look for a tag 
    that has moved into the cabinegts zone and height.  If the light switch state
    changes to inactive, it will turn off the light for that shelf.  """

from tags import Tags, TagLoc, MAX_LOC_BUFF_LEN
from net.geo_packet_handler import Geomsg
import logging


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
    def __init__(self, controller_id: int, connection, zone: str):
        self.id = controller_id
        self.cmd_conn = connection
        self.zone = zone
        self.tags = [False] * 6
        self.light_switch_states = [False] * 6  # Assuming 6 shelves
        self.light_switch_events = 0 # Indicates new light switch event

    def update_light_switch(self, shelf_index, state):
        """Update the light switch state for a given shelf."""
        if 0 <= shelf_index < len(self.light_switch_states):
            self.light_switch_states[shelf_index] = state
            self.light_switch_events |= (1 << shelf_index)
            # send light shelf led msg

    
    def update_shelf_leds(self, shelf_num:int, leds:int):
        param = SHELF_PARAM_BASE+shelf_num
        msg=f'RCVPRM, {self.id}, {param}={leds}\r\n'
        self.cmd_conn(msg) # add a callback
        logger.info(f"Send: {msg}")
    
    def add_ltsw_msg(self, msg: Geomsg):
        """Process a light switch message.
        msg format: ['ts':int, 'msgtype':str, 'Controller ID':int, 
                     'Sensor Type': str, 'state':bool] """
        shelf_number = int(msg.fmsg[4])
        sw_state = int(msg.fmsg[5])
        self.update_light_switch(shelf_number-1, sw_state)

        
        logger.info(msg.msg)
        color = LED_OFF
        if sw_state == 1:
            color = LED_RED        
        self.update_shelf_leds(shelf_number, color)

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