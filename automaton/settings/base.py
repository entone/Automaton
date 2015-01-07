# -*- coding: utf-8 -*-
import os
import sys
import logging
import hashlib
from pymongo.connection import Connection

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(BASE_DIR, '..'))

TEMPLATE_DIRS = ["%s/html" % PROJECT_DIR, "%s/html/templates" % PROJECT_DIR,]

LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_LEVEL = logging.INFO

logging.basicConfig(format=LOG_FORMAT, level=LOG_LEVEL)

CLIENT_SUB = 5554
CLIENT_PUB = 5555
CLIENT_RPC = 5556

NODE_SUB = 5557
NODE_PUB = 5558
NODE_RPC = 6000

IP_ADDRESS = '*'
NETWORK_INTERFACE = 'eth0'

LOG_INTERVAL = 10*60#10 minutes
CLOUD_LOG_INTERVAL = 10*60#10 minutes

IS_DEV = True

#MongoDB Settings
MONGO_HOST = "localhost"
MONGO_PORT = 27017
try:
	conn = Connection(MONGO_HOST, MONGO_PORT, network_timeout=1)
	conn.automaton.collection_names()
	IS_CLOUD = True
except Exception as e:
	IS_CLOUD = False



HISTORICAL_DISPLAY = 8#hours

#AES defaults
BLOCK_SIZE = 16
INTERRUPT = u'\u0000'
PAD = u'\u0000'
KEY = '!!++automaton!!!'

#Sensors

SENSORS = dict(
	temperature='&deg;C',
	ph='',
	humidity='%',
	etape='cm',
	ammonia='ppm',
	nitrite='ppm',
	nitrate='ppm',
	nitrogen='ppm',
	do='mg/L',
	do_percentage='%',
	ec='µs',
	tds='ppm',
	salinity='',
	orp='mV',
)

#Cloud settings

CLOUD_API = "http://localhost/api/"
WEBSOCKET_ENDPOINT = "ws://localhost"

#Timelapse Settings

TIMELAPSE_PATH = "img/snapshot.cgi?size=3&quality=1"
TIMELAPSE_SAVE_PATH = "/home/www/public/timelapse/"
TIMELAPSE_PERIOD = 60*60 #1 Hour
TIMELAPSE_URL = "http://automaton.s3.amazonaws.com/"

#Webcam Settings

WEBCAM_VIDEO = "img/video.mjpeg"

#AWS Settings

AWS_KEY = "AKIAJFUPTTPKUO73LRZA"
AWS_SECRET = "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"
S3_BUCKET = "automaton"
