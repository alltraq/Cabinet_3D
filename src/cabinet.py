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
        self.shelf_height = float(cabinet_config.get('shelf_height', 0.0))
        self.shelf_offset_height = 0.396 # float(cabinet_config.get('location')[2])  # Z coordinate of the shelf
        self.shelf_prox_shreshold = float(cabinet_config.get('height_proximity_threshold', 1.0))

        self.send_geo_cmd = send_cmd_fnc
        self.tags = {num:False for num in range(1,7)} # Keeps trach of tags ids and which shelf they are on}
        self.light_switch_states = {num:False for num in range(1,7)}  # Assuming 6 shelves
        self.light_switch_events = [] # Indicates new light switch event and correlated shelf
        # self.light_switch_events.append(1)
        self.store_light_switch_state(3, True)

    def store_light_switch_state(self, shelf_index, state):
        """Update the light switch state for a given shelf."""
        if 1 <= shelf_index < len(self.light_switch_states):
            self.light_switch_states[shelf_index] = state
            self.update_light_switch_events(shelf_index, state)
            # send light shelf led msg

    def update_light_switch_events(self, shelf_index, state):
        """ if a new event, add to the list. If a light switch goes off, remove it from the list. "
        """
        if shelf_index < 1 or shelf_index > 6:
            return
        
        if state:
            if shelf_index not in self.light_switch_events:
                self.light_switch_events.append(shelf_index)
        else:
            pass
            # try:
            #     self.light_switch_events.remove(shelf_index)
            # except ValueError:
            #     pass

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
        self.store_light_switch_state(shelf_number, sw_state)

        
        logger.info(msg.msg)
        color = LED_OFF
        if sw_state == 1:
            color = LED_RED        
        self.send_shelf_led_msg(shelf_number, color)

    def get_shelf_height(self, shelf_num:int) -> float:
        """ Get the height of the shelf. """
        if shelf_num < 1 or shelf_num > 6:
            raise ValueError("Shelf number must be between 1 and 6.")
        middle_of_shelf_1 = self.shelf_offset_height + (self.shelf_height / 2)
        return middle_of_shelf_1 + ((shelf_num-1) * self.shelf_height)
    
    def get_distance_to_shelf(self, tag: TagLoc, shelf_num:int) -> float:
        """ Get the vertical distance from the tag to the shelf. """
        if shelf_num < 1 or shelf_num > 6:
            raise ValueError("Shelf number must be between 1 and 6.")
        tag_z = tag.get_latest_location()[2]
        shelf_z = self.get_shelf_height(shelf_num)
        logger.debug(f"Cabinet {self.id} shelf {shelf_num} height: {shelf_z:.2f}, tag {tag.tagid} height: {tag_z:.2f}")
        return abs(tag_z - shelf_z)

    def new_tag_loc(self, tag: TagLoc):
        """Process a location monitoring message."""
        if len(self.light_switch_events) == 0:
            return
        
        logger.debug(f"Cabinet {self.id} processing new tag location for tag {tag.tagid}.")
        
        tagid = tag.tagid
        if tagid in self.tags:
            return
        
        logger.debug(f"Tag {tagid} is not currently assigned to any shelf in cabinet {self.id}.")
        
        for shelf in self.light_switch_events:
            logger.debug(f"Checking shelf {shelf} for tag {tagid}. Light switch state: {self.get_light_switch_state(shelf)}")
            if self.get_light_switch_state(shelf):
                dist = self.get_distance_to_shelf(tag, shelf)
                logger.debug(f"Checking shelf {shelf} for tag {tagid}. Distance to shelf: {dist:.2f}")
                if dist <= self.shelf_prox_shreshold:
                    logger.info(f"Tag {tagid} is near shelf {shelf} (dist={dist:.2f}).")
                    self.tags[shelf] = tagid
                    self.send_shelf_led_msg(shelf, LED_BLUE)
                    self.light_switch_events.remove(shelf)
        

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
        self.cabinets: dict[int, Cabinet] = {}
        for cabinet in config.get('cabinets', []):
            cabinet_id = cabinet.get('cabinet_controller_id', None)
            self.cabinets[cabinet_id] = Cabinet(cabinet, send_cmd_fnc=send_fnc)

    def add_ltsw_msg(self, msg: Geomsg):
        """ Add a light switch message to the appropriate cabinet. """
        logger.debug(f"Received message: {msg.msg}")
        cabinet_id = int(msg.fmsg[2])
        self.cabinets[cabinet_id].add_ltsw_msg(msg)


    def get_cabinet(self, cabinet_id: int) -> Cabinet:
        """ Get a Cabinet object by its ID. """
        return self.cabinets.get(cabinet_id, None)
    
    def get_cabinets(self) -> dict:
        """ Get all Cabinet objects. """
        return self.cabinets
