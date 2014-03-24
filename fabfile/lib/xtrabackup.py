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
Percona Xtrabackup
"""

def install():
	util.start()
	# Install Percona XtraBackup (Hot backup software)
	put('fabfile/lib/database/etc-apt-percona.list', 
		'/etc/apt/sources.list.d/percona.list', 
		use_sudo=True)
	sudo('apt-key adv --keyserver keys.gnupg.net --recv-keys 1C4CBDCDCD2EFD2A')
	sudo('apt-get update')
	sudo('apt-get install -yq xtrabackup')
	util.done()

def configure():
	util.start()
	util.done()


	
	
	



 	