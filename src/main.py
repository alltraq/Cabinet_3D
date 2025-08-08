from net import rcvr_parser, geo_packet_handler, tnttcp
import logging, logging.config, json, pathlib, time
import msg_handler
from geotraqr import geo_cmd
import yaml
from typing import Callable
from zones import Zones
from cabinet import Cabinet, Cluster

geo_cmd_connection = None

# LOGGING_LEVEL = logging.WARNING  # Default logging level
# Not sure what the use of this is yet.
# Answer - the "app" logger can be configured seperately
# from the root logger.  Different handlers and filters
# can be applied.
logger = logging.getLogger("app")
logger.propagate = True
# logger.setLevel(logging.ERROR)
# logging.getLogger().setLevel(logging.ERROR)  # Root logger level

def setup_logging():
    """ if config is stored as JSON file """
    config_file = pathlib.Path("logconfig.json")
    with open(config_file) as f_in:
        config = json.load(f_in)
    logging.config.dictConfig(config)

def geo_cmd_send(msg, callback:Callable[[geo_cmd.Message], None]=None):
    """Send a command to the geotraqr."""
    logger.info(f"Sending command: {msg}")
    if geo_cmd_connection is None:
        logger.error("Geo command connection is not established.")
    else:
        geo_cmd_connection.send(msg, callback_fnc=callback)


def run(geo_conn, cmd_conn:geo_cmd.Connect, msg_handler:msg_handler.MsgHandler):
    """
    """

    while(1):
        
        if geo_conn.is_connected():
            msg = geo_conn.rcv()
        else: # if its not connected just return and let context mangager deal
            return
        
        if msg is not None:
            msg_handler.handle_message(msg)
        else:
            time.sleep(0.1)

        if not cmd_conn.is_connected():
            return
        try:
            msg = cmd_conn.rcv()
        except geo_cmd.GeoError as err:
            logger.error(f"{err}")
            

def main():
    """ Main function to start the application. """
    global geo_cmd_connection

    setup_logging()
    logger.info("Starting Cabinet 3D Application")

    # Load configuration
    config_file = pathlib.Path("config/config.yaml")
    with open(config_file) as f_in:
        config = yaml.safe_load(f_in)

    handler = msg_handler.MsgHandler()

    # create Cluster for Cabinet objects
    cluster = Cluster(config, geo_cmd_send)


    handler.register_sens0_type("LTSW", cluster.add_ltsw_msg)

    zones = Zones()
    cabs = cluster.cabinets
    for cab_id, cabinet in cabs.items():
        zones.add_cabinet(cabinet, cabinet.zone)
    
    # handler.register_msg_type("LOCMON", zones.add_locmon)
    handler.register_msg_type("LCTN", zones.add_lctn)
    

    # # Start the receiver parser
    # rcvr_parser.start_receiver(config, msg_handler.handle_message)

    # # Start the cabinet controller
    # cabinet_controller = cabinet.Cabinet(1, tnttcp.TNTTCPConnection(), "zone1")

    

    # Get network configuration
    net_conf = config['network']
    geo_address = net_conf['geotraqr_address']
    geo_cmd_port = net_conf['geo_cmd_port']
    geo_data_port = net_conf['geo_data_port']
    
    parser = rcvr_parser.RcvrParser(geo_packet_handler.Geomsg)
    
    # Main loop
    while True:
        try:
            with tnttcp.client_connect(geo_address, geo_data_port, parser=parser) as geo_out, \
                    geo_cmd.Connect(geo_address, geo_cmd_port) as cmd_conn:
                logger.info("Connected to GeoTraqr")
                geo_cmd_connection = cmd_conn
                run(geo_out, cmd_conn, handler)

        except TimeoutError:
            logger.error("Connection Timed Out")
            time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Closing connection.")
            return
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            time.sleep(5)
        finally:
            geo_cmd_connection = None

if __name__ == "__main__":
    main()
