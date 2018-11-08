#!/usr/bin/python

import sys
import ConfigParser
import requests
import logging
import logging.handlers
from pushbullet import PushBullet

if ( len(sys.argv) != 3 ):
    print "Usage : push.py <TITLE> <BODY>"
    exit(1)

LOG_FILE = '/tmp/push.log'

config = ConfigParser.ConfigParser()
config.read("/root/scripts/config")

my_logger = logging.getLogger()
my_logger.setLevel(logging.DEBUG)

handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=10485760, backupCount=5)

my_logger.addHandler(handler)

handler.setFormatter(logging.Formatter('%(asctime)s : %(levelname)s : %(message)s'))

api_key = config.get("Pushbullet", "API")
pb = PushBullet(api_key)
device = pb.devices[0]

try:
    pb.push_note(sys.argv[1], sys.argv[2])
    logging.info('Notif : %s >> SENT to device : %s', str(sys.argv[1]), str(device))
except requests.exceptions.RequestException as e:
    logging.warning('Push note to Pushbullet failed.')
