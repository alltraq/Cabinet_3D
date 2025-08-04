from net import rcvr_parser, geo_packet_handler, tnttcp
import logging, logging.config, json, pathlib, time
import msg_handler, cabinet
from geotraqr import geo_cmd
import yaml



# Not sure what the use of this is yet.
# Answer - the "app" logger can be configured seperately
# from the root logger.  Different handlers and filters
# can be applied.
logger = logging.getLogger("app")
logger.propagate = False

def setup_logging():
    """ if config is stored as JSON file """
    config_file = pathlib.Path("logconfig.json")
    with open(config_file) as f_in:
        config = json.load(f_in)
    logging.config.dictConfig(config)

    
def main():
    """ Main function to start the application. """
    setup_logging()
    logger.info("Starting Cabinet 3D Application")

    # Load configuration
    config_file = pathlib.Path("config/config.yaml")
    with open(config_file) as f_in:
        config = yaml.safe_load(f_in)


    # create Cluster for Cabinet objects
    

    # # Start the receiver parser
    # rcvr_parser.start_receiver(config, msg_handler.handle_message)

    # # Start the cabinet controller
    # cabinet_controller = cabinet.Cabinet(1, tnttcp.TNTTCPConnection(), "zone1")
    
    # # Main loop
    # while True:
    #     time.sleep(1)  # Simulate doing work
    #     logger.debug("Running main loop...")


if __name__ == "__main__":
    main()
