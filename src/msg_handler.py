
import net.geo_packet_handler as geo_packet_handler


class MsgHandler():
    def __init__(self):
        self.lookup = {"SENS0": self._handle_sens0}
        self.sens0_lookup = {}

    def register_msg_type(self, msg_type:str, callback_fnc):

        if msg_type in self.lookup:
            del self.lookup[msg_type]
            
        self.lookup[msg_type] = callback_fnc

    def register_sens0_type(self, sens_type, callback_fnc):
        
        if sens_type in self.sens0_lookup:
            del self.sens0_lookup[sens_type]
            
        self.sens0_lookup[sens_type] = callback_fnc


    def handle_message(self, msg:geo_packet_handler.Geomsg):

        if msg.type in self.lookup:
            self.lookup[msg.type](msg)

    def _handle_sens0(self, msg:geo_packet_handler.Geomsg):

        if msg.sens_type in self.sens0_lookup:
            self.sens0_lookup[msg.sens_type](msg)
