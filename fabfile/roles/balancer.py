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
Balancer tasks

Note: We are now using DNS Failover using Amazon R53

"""

@task
@roles('linode-db', 'vagrant-db')
def server():
	"""
	Setup Load Balancer with basic software for "balancer" role
	"""
	print('==================================================')
	print('Building Load Balancer')
	print('==================================================')
	sudo('export DEBIAN_FRONTEND=noninteractive')
	# Set the user
	env.user = env.base_user
	env.password = env.base_password
	# Run apt update
	sudo('apt-get update')
	print('==================================================')
	print('... done Building Load Balancer')
	print('==================================================')

@task
@roles('linode-db', 'vagrant-db')
def project():
	"""
	Installs and setup Database server with project specifics
	"""
	print('==================================================')
	print('Setup/Install Project on Load Balancer')
	print('==================================================')
	sudo('export DEBIAN_FRONTEND=noninteractive')
	# Set the user
	env.user = env.base_user
	env.password = env.base_password
	print('==================================================')
	print('... done Setup/Install Project on Load Balancer')
	print('==================================================')
	
	