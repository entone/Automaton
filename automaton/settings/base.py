import os 
import sys
import logging
from logging.handlers import SysLogHandler

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(BASE_DIR, '..'))

TEMPLATE_DIRS = ["%s/templates/" % PROJECT_DIR,]

LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_LEVEL = logging.DEBUG

logging.basicConfig(format=LOG_FORMAT, level=LOG_LEVEL)

CLIENT_SUB = 5554
CLIENT_PUB = 5555
NODE_SUB = 5556
NODE_PUB = 5557
NODE_RPC = 6000

def get_logger(name):
    if sys.platform == "darwin":
        # Apple made 10.5 more secure by disabling network syslog:
        address = "/var/run/syslog"
    else:
        address = '/dev/log'
    logger = logging.getLogger(name)
    handler = SysLogHandler(address=address)
    logger.addHandler(handler)
    return logger



