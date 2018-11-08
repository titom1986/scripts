#!/usr/bin/python

import sys
import os
import json
import string
import logging
import logging.handlers
import ConfigParser
from urllib2 import Request, urlopen, URLError

def Sickbeard ( torrent ):
    apiKey = config.get("Sickbeard", "API")
    url = config.get("Sickbeard", "URL")
    command = config.get("Sickbeard", "CMD")

    request = Request(url + '/api/' + apiKey + '/?cmd=' + command)
    requested = dict()

    try:
        logging.info(request)
        result = urlopen(request)
        histo = json.loads(result.read())
        for data in histo['data']:
            if (not requested.has_key(data['tvdbid'])):
                requested[data['tvdbid']] = dict()
            if (not requested[data['tvdbid']].has_key(data['season'])):
                requested[data['tvdbid']][data['season']] = dict()
            if ((data['resource'] == torrent) and (not requested[data['tvdbid']][data['season']].has_key(data['episode']))):
                request = Request(url + '/api/' + apiKey + '?cmd=episode.search&tvdbid=' + str(data['tvdbid']) + '&season=' + str(data['season']) + '&episode=' + str(data['episode']))
                result = urlopen(request)
                status = json.loads(result.read())
                if (status['result'] == "success"):
                    requested[data['tvdbid']][data['season']][data['episode']] = 1
                    os.system("python /home/titom/scripts/push.py \"Torrent Resnatched\" \"" + torrent + "\"")
                else:
                    os.system("python /home/titom/scripts/push.py \"resnatch.py\" \"Failed to force search : " + torrent + "\"")

    except URLError, e:
        print ('Error')
    return

def Couchpotato ( torrent ):
    apiKey = config.get("Couchpotato", "API")
    url = config.get("Couchpotato", "URL")
    command = config.get("Couchpotato", "CMD")

    request = Request(url + '/api/' + apiKey + '/' + command)
    requested = dict()
    
    torrent = torrent.rsplit(".", 1)[0]
    
    try:
        logging.info(request)
        result = urlopen(request)
        snatched_movie = json.loads(result.read())
        for movie in snatched_movie["movies"]:
            for release in movie["releases"]:
                if release["status"] == "snatched":
                    if release["info"]["name"] == torrent:
                        request = Request(url + '/api/' + apiKey + '/' + "release.manual_download/?id=" + release["_id"])
                        result = urlopen(request)
                        status = json.loads(result.read())
                        if (status['success'] == "true"):
                            os.system("python /home/titom/scripts/push.py \"Torrent Resnatched\" \"" + torrent + "\"")
                        else:
                            os.system("python /home/titom/scripts/push.py \"resnatch.py\" \"Failed to force search : " + torrent + "\"")
                                                
    except URLError, e:
        print ('Error')
    return

######MAIN#########

if (len(sys.argv) != 2):
    print ("Usage : resnatch.py <LFTP_MIRRORING_LOG>")
    sys.exit(1)

log=sys.argv[1]
torrent=""
config = ConfigParser.ConfigParser()
config.read("/home/titom/scripts/config")

LOG_FILE = '/tmp/resnatch.log'
my_logger = logging.getLogger()
my_logger.setLevel(logging.DEBUG)
handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=10485760, backupCount=5)
my_logger.addHandler(handler)

for line in log.splitlines():
    torrent = ""
    if (line.find(".torrent.fail") != -1):
        split=line.split('/')
        index = len(split) - 1
        if (index >= 0):
            torrent = split[len(split) - 1]
            torrent = torrent[0:-14] #Removing ".torrent.fail'"

        if not torrent:
            continue
    
        index = len(split) - 2
        if (index >= 0):
            if (split[len(split) - 2].find("tv") != -1):
                logging.info("Resnatch Sickbeard : %s", torrent)
                Sickbeard(torrent)
            elif (split[len(split) - 2].find("movie") != -1):
                logging.info("Resnatch Couchpotato : %s", torrent)
                Couchpotato(torrent)
