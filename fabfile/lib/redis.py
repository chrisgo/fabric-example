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
Redis
"""

def install():
	util.start()
	# If Redis host is not specified, that means we will run a local one
	if (env.redis_host and env.redis_host != ''):
	    print("Not installing Redis ...")
	    print("Using Redis @ %s:%s" % (env.redis_host, env.redis_port))
	else:
		print("Installing Redis ...")
		sudo('apt-get install -yq redis-server')
		# Secure Redis http://redis.io/topics/security
		sed('/etc/redis/redis.conf',
			'# requirepass foobared', 
			'# requirepass foobared\\nrequirepass %s' % env.password,
			use_sudo=True, backup='.bak', flags='')
		# Open redis to all IPs
		sed('/etc/redis/redis.conf',
			'#bind 127.0.0.1', 
			'#bind 127.0.0.1\\nbind 0.0.0.0',
			use_sudo=True, backup='.bak', flags='')
		# Restart redis
		sudo('/etc/init.d/redis-server restart')
	util.done()

def configure():
	util.start()
	#
	# Additionally, for extra security, we can use IP tables
	#
	# Comment out the bind 
	#sed('/etc/redis/redis.conf', 'bind 127.0.0.1', '#bind 127.0.0.1', use_sudo=True)
	# Restart redis
	#sudo('/etc/init.d/redis-server restart')
	# Setup IP tables 
	# Block Redis port (6379) and resque-web port (5678)
	#sudo('iptables -A INPUT -j DROP -p tcp --destination-port 6379 -i eth0')
	#sudo('iptables -A INPUT -j DROP -p tcp --destination-port 5678 -i eth0')
	# IPs for dev computers
	ips = ['68.111.83.216', '198.15.79.146']
	# IPs for Linode servers
	ips.extend(['173.255.196.166', '173.230.148.249', '173.255.255.61'])
	# IPs for Uptimerobot
	ips.extend(['74.86.158.106', '74.86.158.107', '74.86.179.130'])
	ips.extend(['74.86.179.131', '46.137.190.132', '122.248.234.23'])
	# Add back the IPs
	#for ip in ips:
    #	sudo('iptables -I INPUT -s %s -j ACCEPT' % ip)
	util.done()


 	