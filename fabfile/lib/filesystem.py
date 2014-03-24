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
Filesystem
"""

def install():
	util.start()
	util.done()

def configure(mount_root):
	util.start()
	# Create document root
	mount_root = env.config.get('mount_root')
	if ('%s' in document_root):
		mount_root = mount_root % env.git_project.lower()
	# Create document root directory if it doesn't exist
	if not exists(mount_root):
		sudo("mkdir -m 775 -p %s" % mount_root)
	util.done()

def mkdirs(directories):
	util.start()
	if (directories):
		for directory in directories:
			print("Processing dir: %s" % directory)
			if not exists(directory):
				sudo("mkdir -m 777 -p %s" % directory)
	util.done()
	



 	