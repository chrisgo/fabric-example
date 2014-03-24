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
AutoMysqlBackup
"""

def install():
	util.start()
	# Install automysqlbackup
	sudo('apt-get install -yq automysqlbackup')
	util.done()

def configure():
	util.start()

	util.done()
