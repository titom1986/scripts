#!/usr/bin/python

import ConfigParser
import logging
import logging.handlers
import os
import sys
import subprocess
import shutil

ERROR_STR= """Error removing %(path)s, %(error)s """

def rmgeneric(path, __func__):

    try:
        __func__(path)
        print 'Removed ', path
    except OSError, (errno, strerror):
        print ERROR_STR % {'path' : path, 'error': strerror }
            
def removeall(path):

    if not os.path.isdir(path):
        return
    
    files=os.listdir(path)

    for x in files:
        fullpath=os.path.join(path, x)
        if os.path.isfile(fullpath):
            f=os.remove
            rmgeneric(fullpath, f)
        elif os.path.isdir(fullpath):
            removeall(fullpath)
            f=os.rmdir
            rmgeneri(fullpath, f)

##################LOGGING####################
LOG_FILE = '/tmp/update_torrent.log'

my_logger = logging.getLogger()
my_logger.setLevel(logging.DEBUG)

handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=10485760, backupCount=5)

my_logger.addHandler(handler)

handler.setFormatter(logging.Formatter('%(asctime)s : %(levelname)s : %(message)s'))

###################CONFIG#####################
config = ConfigParser.ConfigParser()
config.read("/root/scripts/config")

retry = int(config.get("UpdateTorrent", "retry"))
local_folder = config.get("UpdateTorrent", "local_folder")
remote_folder = config.get("UpdateTorrent", "remote_folder")
login = config.get("Seedbox", "login")
mdp = config.get("Seedbox", "mdp")
host = config.get("Seedbox", "host")

for i in range(retry):
    proc = subprocess.Popen( "lftp -c open -e \"mirror -Re --verbose=6 \"{0}\" \"{1}\"\" -u {2},{3} \"{4}\"".format( local_folder, remote_folder, login, mdp, host ), stdout=subprocess.PIPE, shell=True )
    state = proc.communicate()[0]
    logging.info(state)

    if ( state.find( ".fail" ) != -1 ):
        subprocess.call(["/root/scripts/push.py",  "Torrent Failed !", state] )
        subprocess.call(["/root/resnatch.py", state] )
        sys.exit(0)

    if ( state.count( "Mirroring" ) == 1 ):
        logging.info("Deleting mirrored torrents.")
        removeall("/root/video/torrents/tv")
        sys.exit(0)

logging.warning("One or more mirroring failed.")
sys.exit(1)
