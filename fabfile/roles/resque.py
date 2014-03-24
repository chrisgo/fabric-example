from __future__ import with_statement
from fabric.api import *
from fabric.contrib.console import confirm
from fabric.contrib.files import *
import paramiko
import os
import json
import datetime
from fabfile.lib import *

"""
Resque Server Build and Setup

Source: http://etagwerker.wordpress.com/2011/06/27/how-to-setup-resque-web-with-nginx-and-unicorn/
"""

def server_setup():
	"""
	Setup Resque (Redis) Server with basic software for "resque" role 
	"""
	print('==================================================')
	print('Building Resque Server')
	print('==================================================')
	sudo('export DEBIAN_FRONTEND=noninteractive')
	# Run update
	sudo('apt-get update')
	nginx.install()
	nginx.configure()
	redis.install()
	redis.configure()
	resque.install()
	resque.configure()
	print('==================================================')
	print('... done Building Resque Server')
	print('==================================================')


def project_setup():
	"""
	Installs and setup Resque server with project specifics
	"""
	print('==================================================')
	print('Setup/Install Project on Resque Server')
	print('==================================================')
	sudo('export DEBIAN_FRONTEND=noninteractive')
	# Set up queues
	
	
	print('==================================================')
	print('... done Setup/Install Project on Resque Server')
	print('==================================================')

