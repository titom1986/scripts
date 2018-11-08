#!/usr/bin/python

import ConfigParser
import logging
import logging.handlers
import os
import shutil
import fcntl
import requests
import datetime
import time
import sys
from xml.etree import ElementTree
from HTMLParser import HTMLParser

def GetShows():
        show_req = "http://" + plex_ip + ":" + plex_port + "/library/sections/2/all?X-Plex-Token=" + plex_token 
        show_res = requests.get(show_req)
        show_xml_tree = ElementTree.fromstring(show_res.content)
        for show in show_xml_tree:
	    shows.append(int(show.attrib['ratingKey']))

def GetNewestFiles():
	now = datetime.datetime.now()
	ago = now - datetime.timedelta(days=retention)

	for root, dirs, files in os.walk(series_dir):  
	    for fname in files:
	        path = os.path.join(root,fname)
	        st = os.stat(path)    
	        mtime = datetime.datetime.fromtimestamp(st.st_mtime)
	        if mtime > ago:
                    newest.append(path)

def CopyNewestUnwatched():
    logging.info("######################## COPY ########################")
    
    h = HTMLParser()
    for new_episode in newest:
        for unwatched_episode in unwatched:
            basename_new = os.path.basename(new_episode)
            basename_unwatched_episode = os.path.basename(h.unescape(unwatched_episode).encode('utf-8'))

            if basename_new == basename_unwatched_episode:
                copy_dest = os.path.join(copy_dir, basename_new)
                if not os.path.isfile(copy_dest):
                    shutil.copy2(new_episode, copy_dest)
                    logging.info("Copied : " + new_episode)

                sub = os.path.splitext(new_episode)[0] + ".fr.srt"
                subCopy = os.path.join(copy_dir, os.path.basename(sub))
                if os.path.isfile(sub):
                    if (os.path.isfile(subCopy) and (os.path.getsize(sub) != os.path.getsize(subCopy))) or not os.path.isfile(subCopy):
                        shutil.copy2(sub, subCopy)
                        logging.info("Copied : " + sub)

                sub = os.path.splitext(new_episode)[0] + ".en.srt"
                subCopy = os.path.join(copy_dir, os.path.basename(sub))
                if os.path.isfile(sub):
                    if (os.path.isfile(subCopy) and (os.path.getsize(sub) != os.path.getsize(subCopy))) or not os.path.isfile(subCopy):
                        shutil.copy2(sub, subCopy)
                        logging.info("Copied : " + sub)

if __name__ == '__main__':
    
    LOG_FILE="/tmp/new_episodes.log"
    my_logger = logging.getLogger()
    my_logger.setLevel(logging.DEBUG)

    handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=10485760, backupCount=5)

    my_logger.addHandler(handler)

    handler.setFormatter(logging.Formatter('%(asctime)s : %(levelname)s : %(message)s'))

    lockFile = open("/tmp/new_episodes.lock", 'w+')
    try:
        fcntl.flock(lockFile,fcntl.LOCK_EX|fcntl.LOCK_NB )
    except IOError, e:
        logging.warning('new_episodes is already running.')
        sys.exit(1)

    try:
        ##################CONFIG#####################
        config = ConfigParser.ConfigParser()
        config.read("/root/scripts/config")

        retention = int(config.get("NewEpisodes", "retention"))
        plex_ip = config.get("NewEpisodes", "plex_ip")
        plex_port = config.get("NewEpisodes", "plex_port")
        plex_token = config.get("NewEpisodes", "plex_token")
        copy_dir = config.get("NewEpisodes", "copy_dir")
        series_dir = config.get("NewEpisodes", "series_dir")

        ignored = [] 
        ignored_shows = config.get("NewEpisodes", "ignored_shows")
        for id_show in ignored_shows.split(';'):
            ignored.append(int(id_show))

        ext = [".mov", ".mp4", ".avi", ".mkv"]
        shows = []

        GetShows()
	
	keep = [x for x in ignored if x in shows]
	print (keep) 

        #GetNewestFiles()
        #PurgeCopiedFiles()
        #CopyNewestUnwatched()

    finally:
        fcntl.flock(lockFile, fcntl.LOCK_UN)
