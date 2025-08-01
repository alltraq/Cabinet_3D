from net import rcvr_parser, geo_packet_handler, tnttcp
import logging.config, json, pathlib, time
import msg_handler, cabinet, rcvr_id_handler
from geotraqr import geo_cmd



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

    