from __future__ import with_statement
from fabric.api import *
from fabric.contrib.console import confirm
from fabric.contrib.files import *
import paramiko
import os
import json
import datetime
from fabfile.lib import util

"""
Papertrail
"""

def install():
	util.start()
	util.done()

def configure():
	util.start()
	if (not(env.papertrail_key)):
		util.done('Missing Key')
		return
	if (not(util.is_production())):
		util.done('Not PRODUCTION')
		return
	# Papertrail
	# Add this to end of rsyslog
	# *.*          @logs.papertrailapp.com:31784
	# Restart
	#sudo /etc/init.d/rsyslog restart
	util.done()


 	