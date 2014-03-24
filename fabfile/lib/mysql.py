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
MySQL
"""

def install():
	util.start()
	# Install standard packages
	with settings(hide('warnings', 'stderr'), warn_only=True):
		result = sudo('dpkg-query --show mysql-server')
		if ("No packages" in result):
			print("Installing MySQL ...")
			sudo('echo "mysql-server-5.5 mysql-server/root_password password ' \
                 '%s" | debconf-set-selections' % env.password)
			sudo('echo "mysql-server-5.5 mysql-server/root_password_again password ' \
                 '%s" | debconf-set-selections' % env.password)
			sudo('apt-get install -yq mysql-server')
			# Load timezone info
			run('mysql_tzinfo_to_sql /usr/share/zoneinfo | mysql --user=%s --password=%s mysql' %
				('root', env.password))
			sudo('/etc/init.d/mysql restart')
	util.done()

def configure():
	util.start()
	# Open up mysql 
	sed('/etc/mysql/my.cnf', 
		'bind-address		= 127.0.0.1', 
		'bind-address		= 0.0.0.0', 
		use_sudo=True, backup='.bak', flags='')
	# Update root password (do we need to do this??)
	#query = "update user set password=PASSWORD('%s') where user='root';" % (env.password)
	#run('mysql --batch --raw --skip-column-names --user=root --execute="%s"' % query)
	#print("Updated database root user password")
	sudo('/etc/init.d/mysql restart')
	util.done()

def configure_master(host):
	util.start()
	util.done()

def configure_slave(host):
	util.start()
	util.done()



	
	
	



 	