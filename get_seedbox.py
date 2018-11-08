#!/usr/bin/python

import fcntl
import ConfigParser
import logging
import logging.handlers
import subprocess
import os
import sys
import shutil
from collections import defaultdict

LOG_FILE = '/tmp/get_seedbox.log'

my_logger = logging.getLogger()
my_logger.setLevel(logging.DEBUG)

handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=10485760, backupCount=5)

my_logger.addHandler(handler)

handler.setFormatter(logging.Formatter('%(asctime)s : %(levelname)s : %(message)s'))

lockFile = open("/tmp/get_seedbox.lock", 'w+')
try:
	fcntl.flock(lockFile,fcntl.LOCK_EX|fcntl.LOCK_NB )
except IOError, e:
	logging.warning('Synctorrent is already running.')
        sys.exit(1)

try:
        ##################CONFIG#####################
        config = ConfigParser.ConfigParser()
        config.read("/root/scripts/config")

        retry = int(config.get("GetSeedbox", "retry"))
        login = config.get("Seedbox", "login")
        mdp = config.get("Seedbox", "mdp")
        host = config.get("Seedbox", "host")
        min_file_size = config.get("GetSeedbox", "min_file_size")
        
        directories = []

        directories.append( {"remote" : config.get("GetSeedbox", "remote_dir_movie"), "local_temp" : config.get("GetSeedbox", "local_dir_movie_temp"), "local" : config.get("GetSeedbox", "local_dir_movie") } )
        directories.append( {"remote" : config.get("GetSeedbox", "remote_dir_tv"), "local_temp" : config.get("GetSeedbox", "local_dir_tv_temp"), "local" : config.get("GetSeedbox", "local_dir_tv") } )
        directories.append( {"remote" : config.get("GetSeedbox", "remote_dir_zik"), "local_temp" : config.get("GetSeedbox", "local_dir_zik_temp"), "local" : config.get("GetSeedbox", "local_dir_zik") } )

        #MUST ALWAYS BE AT LAST POSITION TO AVOID DELETING >50Mo FILES IN FOLDER OLD 
        #TODO MAKE IT AS AN OPTION FOR FOLDER (CLEAN)
        directories.append( {"remote" : config.get("GetSeedbox", "remote_dir_old"), "local_temp" : config.get("GetSeedbox", "local_dir_old_temp"), "local" : config.get("GetSeedbox", "local_dir_old") } )
        ##################END CONFIG##################

        for i in range(0, len(directories)):
		if not (os.path.exists(directories[i]['local_temp']) and os.path.exists(directories[i]['local'])):
			continue
                for j in range(retry):
                        state = os.system( "lftp -c open -e \"set ftp:list-options -a; mirror -e -c --Remove-source-files \"{0}\" \"{1}\"\" -u \"{2}\",\"{3}\" \"{4}\"".format( directories[i]['remote'], directories[i]['local_temp'], login, mdp, host ) )
			print "lftp -c open -e \"set ftp:list-options -a; mirror -e -c --Remove-source-files \"{0}\" \"{1}\"\" -u \"{2}\",\"{3}\" \"{4}\"".format( directories[i]['remote'], directories[i]['local_temp'], login, mdp, host )
                        logging.info( directories[i]['remote'] + ' : ' + str(state) )
                        if (state == 0):
                                files = os.listdir( directories[i]['local_temp'] )
                                for f in files:
                                        if ( not os.path.isfile( os.path.join( directories[i]['local'], f ) ) and not os.path.isdir( os.path.join( directories[i]['local'], f ) ) ):
                                                full_file_name = os.path.join( directories[i]['local_temp'], f )
                                                shutil.move( full_file_name, directories[i]['local'] )
                                if ( i != len(directories) - 1 ): #CAREFUL WITH THIS
                                        for root, dirs, files in os.walk( directories[i]['local'], topdown=True ):
                                                for name in files:
                                                        file_stat = os.stat(os.path.join(root, name))
                                                        if ( file_stat.st_size <= int(min_file_size) ):
                                                                os.remove(os.path.join(root, name))
                                        for root, dirs, files in os.walk( directories[i]['local'], topdown=False ):
                                                for name in dirs:
                                                        if ( not os.listdir(os.path.join(root, name)) ):
                                                                shutil.rmtree(os.path.join(root, name))
                                break
finally:
        fcntl.flock(lockFile, fcntl.LOCK_UN)
