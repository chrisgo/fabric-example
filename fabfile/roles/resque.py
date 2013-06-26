from __future__ import with_statement
from fabric.api import *
from fabric.contrib.console import confirm
from fabric.contrib.files import *
import paramiko
import os
import json
import datetime

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
	# Run update
	sudo('apt-get update')
	# Install basic Ruby stuff
	sudo('apt-get install -y ruby1.8 ruby1.8-dev rails rake gem rubygems')
	# Install nginx, redis-server
	sudo('apt-get install -y nginx')
	# If Redis host is not specified, that means we will run a local one
	if (env.redis_host and env.redis_host != ''):
	    print("Not installing Redis ...")
	    print("Using Redis @ %s:%s" % (env.redis_host, env.redis_port))
	else:
		print("Installing Redis ...")
		sudo('apt-get install -y redis-server')
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
	# Install gems: resque + unicorn
	sudo('gem install --no-rdoc --no-ri bundler')
	sudo('gem install --no-rdoc --no-ri json')
	sudo('gem install --no-rdoc --no-ri resque')
	sudo('gem install --no-rdoc --no-ri unicorn')
	# Create the resque-web directory structure
	sudo('mkdir -p /etc/unicorn')
	sudo('mkdir -p /var/www/resque-web')
	sudo('mkdir -p /var/www/resque-web/shared')
	sudo('mkdir -p /var/www/resque-web/config')
	sudo('mkdir -p /var/www/resque-web/log')
	sudo('mkdir -p /var/www/resque-web/shared')
	sudo('chown -R www-data:www-data /var/www/resque-web')
	sudo('chmod -R 775 /var/www/resque-web')
	put('fabfile/lib/resque/etc-init.d-unicorn', '/etc/init.d/unicorn', use_sudo=True)
	put('fabfile/lib/resque/etc-nginx-resque-web', '/etc/nginx/sites-available/resque-web', use_sudo=True)
	put('fabfile/lib/resque/etc-unicorn-resque-web.conf', '/etc/unicorn/resque-web.conf', use_sudo=True)
	put('fabfile/lib/resque/var-www-config.ru', '/var/www/resque-web/config.ru', use_sudo=True)
	put('fabfile/lib/resque/var-www-unicorn.rb', '/var/www/resque-web/config/unicorn.rb', use_sudo=True)
	put('fabfile/lib/resque/var-www-resque.rb', '/var/www/resque-web/config/resque.rb', use_sudo=True)
	# Munge the server_names to create a unique list
	# TODO: Move to separate function
	server_names = env.config.get('server_names', "")
	if (server_names != "" and server_names['resque'] != ""):
		server_names = server_names['resque']
		server_names.append(env.host_string)
		server_names = set(server_names)
		nginx_server_name = " ".join(server_names)
	else:
		nginx_server_name = env.host_string
	print("Setting nginx server_name: %s" % nginx_server_name)
	sed('/etc/nginx/sites-available/resque-web',
		'\{\{localhost\}\}', 
		'%s' % nginx_server_name,
		use_sudo=True, backup='.bak', flags='')
	# Configure resque to the correct Redis server
	redis_host = 'localhost'
	redis_port = 6379
	redis_password = env.password
	if (env.redis_host and env.redis_host != ''):
		redis_host = env.redis_host
		redis_port = env.redis_port
		redis_password = env.redis_password
		print("Using redis server @ %s:%s" % (redis_host, redis_port))
	sed('/var/www/resque-web/config.ru',
		'\{\{host\}\}', 
		'%s' % redis_host,
		use_sudo=True, backup='.bak', flags='')
	sed('/var/www/resque-web/config.ru',
		'\{\{port\}\}', 
		'%s' % redis_port,
		use_sudo=True, backup='.bak', flags='')
	sed('/var/www/resque-web/config.ru',
		'\{\{password\}\}', 
		'%s' % redis_password,
		use_sudo=True, backup='.bak', flags='')
	# Continue configuring resque server
	sed('/var/www/resque-web/config/resque.rb',
		'\{\{password\}\}', 
		'%s' % env.password,
		use_sudo=True, backup='.bak', flags='')
	if not exists('/etc/nginx/sites-enabled/resque-web'):
		sudo('ln -s /etc/nginx/sites-available/resque-web /etc/nginx/sites-enabled/resque-web')
	sudo('chown root:root /etc/init.d/unicorn')
	sudo('chmod 775 /etc/init.d/unicorn')
	# Have unicorn (resque-web) start on boot
	sudo('update-rc.d unicorn defaults')
	# Nginx configuration changes
	sed('/etc/nginx/nginx.conf', 
		'# server_names_hash_bucket_size 64', 
		'server_names_hash_bucket_size 64', 
		use_sudo=True, backup='.bak', flags='')
	# Nginx breaks due to 2 port 80 listeners
	sed('/etc/nginx/sites-available/default', 
		'listen ', 
		'#listen ', 
		use_sudo=True, flags='')
	# Restart unicorn and nginx
	sudo('/etc/init.d/unicorn restart')
	sudo('/etc/init.d/nginx restart')
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
	# Set up queues
	
	
	print('==================================================')
	print('... done Setup/Install Project on Resque Server')
	print('==================================================')

