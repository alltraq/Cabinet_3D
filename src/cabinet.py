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
from geotraqr import geo_cmd


SHELF_PARAM_BASE = 100
LED_OFF = 0
LED_RED = 1
LED_GREEN = 2
LED_BLUE = 4
LED_WHITE = 7


logger = logging.getLogger("app"+".__name__")
# logger = logging.getLogger("__name__")
logger.propagate = True


class Cabinet:
    def __init__(self, cabinet_config: dict, send_cmd_fnc: Callable[[str], None]):
        """ Initialize the Cabinet object with its configuration.
            Args:
                cabinet_config: dict containing cabinet configuration
                send_cmd_fnc: Function to call to send the geotraqr a message. It should
                follow the fnc(msg, callback) scheme. See geo_cmd.Connect.send(). """
        self.id = cabinet_config['cabinet_controller_id']
        self.zone = cabinet_config['zone']

        self.send_geo_cmd = send_cmd_fnc
        self.tags = [False] * 6 # Keeps trach of tags ids and which shelf they are on
        self.light_switch_states = [False] * 6  # Assuming 6 shelves
        self.light_switch_events = 0 # Indicates new light switch event and correlated shelf

    def store_light_switch_state(self, shelf_index, state):
        """Update the light switch state for a given shelf."""
        if 0 <= shelf_index < len(self.light_switch_states):
            self.light_switch_states[shelf_index] = state == 1
            self.light_switch_events |= (1 << shelf_index)
            # send light shelf led msg

    def get_light_switch_state(self, shelf_index) -> bool:
        return self.light_switch_states[shelf_index]
    
    def get_tags(self):
        """ Get the tags on the shelves. """
        return self.tags

    
    def send_shelf_led_msg(self, shelf_num:int, leds:int):
        """Send a message to set the LED state for a shelf.
           shelf_num: 1-6, leds: bitmask of LED states"""
        param = SHELF_PARAM_BASE+shelf_num
        msg=f'RCVPRM, {self.id}, {param}={leds}\r\n'
        self.send_geo_cmd(msg) # add a callback
        logger.info(f"Send: {msg}")

    
    def add_ltsw_msg(self, msg: Geomsg):
        """Process a light switch message.
        LTSW Geomsg format: ['ts':int, 'msgtype':str, 'Controller ID':int, 
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

    def _init_states(self):
        self._request_switch_states()
        self._request_led_states()
        self.initialized = False

    def _request_switch_states(self):
        msg = f"RCVCMD, {self.dev_id}, GETRCVP, 97\r\n"
        logger.info(f"Send: {msg}")
        self.cmd_conn(msg, self._parse_switch_state_response)

    def _request_led_states(self):
        msg = f"RCVCMD, {self.dev_id}, GETRCVP, 101, 102, 103, 104, 105, 106\r\n"
        logger.info(f"Send: {msg}")
        self.cmd_conn(msg, self._parse_led_param_response)


    def _parse_led_param_response(self, msg:geo_cmd.Message):
        """ Callback for RCVCMD 101, . """
        if msg.err == "ERROR":
            return
        
        logger.debug(f"_parse_led_param_response. msg.rspns: {msg.rspns}")
        try:
            vals = msg.rspns.replace(" ", "").split(",")
        except Exception as e:
            logger.error('_parse_led_patam_response exception. ', e)

        for idx, val in enumerate(vals):
            try:
                val=int(val)
                self.set_sw_state(idx+1, val)
            except:
                logger.exception(f'Exception parsing led state response')
                return
        self.initialized = True

    def _parse_switch_state_response(self, msg:geo_cmd.Message):
        """ Callback for RCVCMD 97, switch states. """
        if msg.err == "ERROR":
            
            return
        
        logger.debug(f"_parse_switch_state_response. msg.rspns: {msg.rspns}")

        try:
            val=int(msg.rspns)
        except:
            logger.exception(f'Exception parsing switch state response')
            return
        self.sw_states = val
        self.initialized = True

class Cluster:
    """ A Cluster of Cabinet objects.  It is used to manage multiple cabinets.
        Route LTSW message to the appropriate cabinet. """
    def __init__(self, config: dict, send_fnc: Callable[[str], None]):
        """ create a Cabinet object for each cabinet in the config """
        self.cabinets = {}
        self.ltsw_path = {}
        for cabinet in config.get('cabinets', []):
            cabinet_id = cabinet.get('cabinet_controller_id', None)
            self.cabinets[cabinet_id] = Cabinet(cabinet, send_cmd_fnc=send_fnc)
            self.ltsw_path[cabinet_id] = self.cabinets[cabinet_id].add_ltsw_msg

    def add_ltsw_msg(self, msg: Geomsg):
        """ Add a light switch message to the appropriate cabinet. """
        logger.debug(f"Received message: {msg.msg}")
        cabinet_id = int(msg.fmsg[2])
        self.ltsw_path[cabinet_id](msg)


    def get_cabinet(self, cabinet_id: int) -> Cabinet:
        """ Get a Cabinet object by its ID. """
        return self.cabinets.get(cabinet_id, None)
