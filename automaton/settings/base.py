import os
import sys
import logging
import hashlib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(BASE_DIR, '..'))

TEMPLATE_DIRS = ["%s/html/templates" % PROJECT_DIR,]

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

LOG_INTERVAL = 10*60#seconds

HISTORICAL_DISPLAY = 8#hours

#AES defaults
BLOCK_SIZE = 16
INTERRUPT = u'\u0000'
PAD = u'\u0000'
KEY = '!!++automaton!!!'

#Sensors

SENSORS = dict(
	Temperature='&deg;C',
	PH='',
	Humidity='%',
	ETape='cm',
)