#!/usr/bin/python

import subprocess

def searchSub( lang, filename, retry, user, password, error, doNotif ):
    for i in range( int(retry) ):
	print ("/usr/local/bin/subliminal --addic7ed {0} {1} download -f -l {2} \"{3}\" 2>&1".format( user, password, lang, filename))
        proc = subprocess.Popen("/usr/local/bin/subliminal --addic7ed {0} {1} download -f -l {2} \"{3}\" 2>&1".format( user, password, lang, filename  ), stdout=subprocess.PIPE, shell=True)
        ret = proc.communicate()[0]

        if ( ret.find( error ) != -1 and doNotif ):
            subprocess.Popen("/root/scripts/push.py Subtitle \"{0} {1}\" 2>&1".format( filename, lang ), shell=True)
            return True
    return False
