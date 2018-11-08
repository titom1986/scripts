#!/usr/bin/python

import argparse
import multiprocessing
import subprocess
import ConfigParser
import logging
import logging.handlers
import sys
import glob
import os
import fcntl
from datetime import datetime
import time
import Queue
import threading
from lang_sub import searchSub

class UpdateSubs(object):

    def __init__(self):
        parser = argparse.ArgumentParser(
            description='Find or count subtitles within a range of time or directory',
            usage='''update_subs.py <command> [<args>]

Commands are:
   recent     Find missing subtitles in fr/en for videos since <NB> days in movies and series folder.
   count      Count videos in <DIR> (default movies and series) and missing subtitles for fr and en.
   dir        Find missing subtitles in fr/en for videos in directory
''')
        parser.add_argument('command', help='Subcommand to run')
        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            print 'Unrecognized command'
            parser.print_help()
            exit(1)
        
        getattr(self, args.command)()


    def recent(self):
        parser = argparse.ArgumentParser( description='Find Subtitles for videos since N days' )
        parser.add_argument('days', action='store')
        parser.add_argument('--force', action='store_true', default=False)
        args = parser.parse_args(sys.argv[2:])
        midnight_timestamp = time.mktime(datetime.now().replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=None).timetuple())
        limit_time = midnight_timestamp - int(args.days) * 86400
       
        for directory in directories :
            for root, dirs, files in os.walk(directory):
                for filename in files:
                    filepath = os.path.join(root, filename)
                    if ( filepath.endswith(tuple(ext)) ):
                        if os.stat(filepath).st_mtime > limit_time:
                            filebasename = os.path.splitext(os.path.basename(filepath))[0]
                            if not os.path.isfile(os.path.join(root, filebasename + ".fr.srt")):
                                searchSub("fr", filepath, retry, addicted_user, addicted_passwd, error, True)
                            elif args.force:
                                searchSub("fr", filepath, retry, addicted_user, addicted_passwd, error, False)
                            if not os.path.isfile(os.path.join(root, filebasename + ".en.srt")):
                                searchSub("en", filepath, retry, addicted_user, addicted_passwd, error, True)
                            elif args.force:
                                searchSub("en", filepath, retry, addicted_user, addicted_passwd, error, False)

    def dir(self):
        parser = argparse.ArgumentParser( description='Find Subtitles for videos in a directory' )
        parser.add_argument('dir', action='store')
        parser.add_argument('--force', action='store_true', default=False)
        args = parser.parse_args(sys.argv[2:])

        for root, dirs, files in os.walk(args.dir):
            for filename in files:
                filepath = os.path.join(root, filename)
                if ( filepath.endswith(tuple(ext)) ):
                    filebasename = os.path.splitext(os.path.basename(filepath))[0]
                    if not os.path.isfile(os.path.join(root, filebasename + ".fr.srt")):
			print ("search fr" + filebasename)
                        searchSub("fr", filepath, retry, addicted_user, addicted_passwd, error, True)
                    elif args.force:
                        searchSub("fr", filepath, retry, addicted_user, addicted_passwd, error, False)
                    if not os.path.isfile(os.path.join(root, filebasename + ".en.srt")):
                        searchSub("en", filepath, retry, addicted_user, addicted_passwd, error, True)
                    elif args.force:
                        searchSub("en", filepath, retry, addicted_user, addicted_passwd, error, False)


if __name__ == '__main__':
    
    LOG_FILE="/tmp/subs.log"
    my_logger = logging.getLogger()
    my_logger.setLevel(logging.DEBUG)

    handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=10485760, backupCount=5)

    my_logger.addHandler(handler)

    handler.setFormatter(logging.Formatter('%(asctime)s : %(levelname)s : %(message)s'))

    lockFile = open("/tmp/subs.lock", 'w+')
    try:
        fcntl.flock(lockFile,fcntl.LOCK_EX|fcntl.LOCK_NB )
    except IOError, e:
        logging.warning('update_subs is already running.')
        sys.exit(1)

    try:
            ##################CONFIG#####################
            config = ConfigParser.ConfigParser()
            config.read("/root/scripts/config")

            retry = int(config.get("Subs", "retry"))
            addicted_user = config.get("Subs", "login_addic7ed")
            addicted_passwd = config.get("Subs", "mdp_addic7ed")
            error = config.get("Subs", "error")
            movies = config.get("Subs", "movies")
            series = config.get("Subs", "series")
            ext = ['.mov', '.mp4', '.avi', '.mkv']
           
            directories = []
            directories.append(movies)
            directories.append(series)
	    print (series)
            UpdateSubs()

    finally:
        fcntl.flock(lockFile, fcntl.LOCK_UN)
    #pool = multiprocessing.Pool(None)
    #ret = pool.map_async( lang_sub.searchSub, lang, filenames['en'], retry, user, password, error )
    #ret.wait()
