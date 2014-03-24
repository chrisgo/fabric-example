from __future__ import with_statement
from fabric.api import *
from fabric.contrib.console import confirm
from fabric.contrib.files import *
from ilogue.fexpect import expect, expecting
from ilogue.fexpect import run as expect_run #not to confuse with fabric.api.run
import paramiko
import os
import json
import datetime
from fabfile.lib import *

__all__ = ['balancer', 'cron', 'database', 'resque', 'www', 'worker']

@task
def server_normalize():	
	"""
	*** SUB-TASK *** Builds a server after normalization of systems/providers

	Set up the correct apt repositories so we can get the 
	# correct packages (Nginx 1.x, PHP-FPM)
	"""
	print('==================================================')
	print('Server Normalize (Common)')
	print('==================================================')
	# Set the debian apt-get non-interactive shell
	sudo('export DEBIAN_FRONTEND=noninteractive')
	# Add SSH key
	base.add_keys()
	# Install base packages 
	base.install()
	base.configure()
	ufw.install()
	ufw.configure()
	environment	= env.config.get('environment', "")
	# Install S3FS
	if (util.enabled('s3fs')):
		s3fs.install()
	# Install NewRelic
	if (util.enabled('newrelic')):
		newrelic.install()
	# Done
	print('==================================================')
	print('... done Server Normalize (Common)')
	print('==================================================')


