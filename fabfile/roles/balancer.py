from __future__ import with_statement
from fabric.api import *
from fabric.contrib.console import confirm
from fabric.contrib.files import *
import paramiko
import os
import json
import datetime

"""
Balancer tasks
"""

@task
@roles('linode-db', 'vagrant-db')
def server():
	"""
	Setup Database Server with basic software for "database" role
	"""
	print('==================================================')
	print('Building Database Server')
	print('==================================================')
	# Set the user
	env.user = env.base_user
	env.password = env.base_password
	# Run apt update
	sudo('apt-get update')
	# Install standard packages
	sudo('apt-get install -y mysql-server')
	# Open up mysql 
	sed('/etc/mysql/my.cnf', 
		'bind-address		= 127.0.0.1', 
		'bind-address		= 0.0.0.0', 
		use_sudo=True, backup='.bak', flags='')
	sudo('/etc/init.d/mysql restart')
	print('==================================================')
	print('... done Building Database Server')
	print('==================================================')

@task
@roles('linode-db', 'vagrant-db')
def project():
	"""
	Installs and setup Database server with project specifics
	"""
	print('==================================================')
	print('Setup/Install Project on Database Server')
	print('==================================================')
	# Set the user
	env.user = env.base_user
	env.password = env.base_password
	# Create new database 
	# Create user + grant
	# SCP database from backup 
	# Run mysqldump to database
	print('==================================================')
	print('... done Setup/Install Project on Database Server')
	print('==================================================')
	
	