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
MariaDB
"""

def install():
	util.start()
	# Get MariaDB Repo
	sudo('apt-get install -y python-software-properties')
	sudo('apt-key adv --recv-keys --keyserver keyserver.ubuntu.com 0xcbcb082a1bb943db')
	put('fabfile/lib/database/etc-apt-mariadb.list', 
		'/etc/apt/sources.list.d/mariadb.list', 
		use_sudo=True)
	sudo('apt-get update')
	# See if we can pad the mariadb install for unattended more
	#sudo('echo "mysql-server-5.5 mysql-server/root_password password ' \
    #     '%s" | debconf-set-selections' % env.password)
	#sudo('echo "mysql-server-5.5 mysql-server/root_password_again password ' \
    #     '%s" | debconf-set-selections' % env.password)
	# Install MariaDB Galera Cluster
	sudo('apt-get install -yq rsync mariadb-galera-server galera')
	sudo('/etc/init.d/mysql stop')
	util.done()

def configure():
	util.start()
	# Configure 
	put('fabfile/lib/database/galera.cnf', 
		'/etc/mysql/conf.d/galera.cnf', 
		use_sudo=True)
	# Set the ips
	ips = env.config.get('ips')
	ips_string = ','.join(ips['database'])
	sed('/etc/mysql/conf.d/galera.cnf',
		'\{\{ips\}\}',
		ips_string, 
		use_sudo=True, flags='')
	# Set the current box hostname and IP
	current_ip = get_current_ip()
	sed('/etc/mysql/conf.d/galera.cnf',
		'\{\{ip\}\}',
		current_ip, 
		use_sudo=True, flags='')
	sed('/etc/mysql/conf.d/galera.cnf',
		'\{\{hostname\}\}',
		env.host_string, 
		use_sudo=True, flags='')
	# We have to start the first cluster with a special flag
	# roledefs = env.config.get('roledefs')
	# first_host = roledefs[0]
	# if env.host_string == first_host:
	#     sudo('/etc/init.d/mysql start --wsrep-new-cluster')
	# else:
	# 	  sudo('/etc/init.d/mysql start')
    # Now we have to copy /etc/mysql/debian.cnf from one to others
	put('fabfile/lib/database/etc-mysql-debian.cnf', 
   	    '/etc/mysql/debian.cnf', 
	    use_sudo=True)
	util.done()

 	