import os 
import sys
import logging

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(BASE_DIR, '..'))

TEMPLATE_DIRS = ["%s/templates/" % PROJECT_DIR,]

LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_LEVEL = logging.DEBUG

logging.basicConfig(format=LOG_FORMAT, level=LOG_LEVEL)

CLIENT_SUB = 5554
CLIENT_PUB = 5555
CLIENT_RPC = 5556

NODE_SUB = 5557
NODE_PUB = 5558
NODE_RPC = 6000

IP_ADDRESS = '*'
NETWORK_INTERFACE = 'eth0'



