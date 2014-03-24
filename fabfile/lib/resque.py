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
Resque
"""

def install():
	util.start() 
	 # Install basic Ruby stuff
	sudo('apt-get install -yq ruby1.8 ruby1.8-dev rails rake gem rubygems')
	# Install gems: resque + unicorn
	sudo('gem install --no-rdoc --no-ri bundler')
	sudo('gem install --no-rdoc --no-ri json')
	sudo('gem install --no-rdoc --no-ri resque')
	sudo('gem install --no-rdoc --no-ri unicorn')
	util.done()
	

def configure():
	util.start()
	# Create the resque-web directory structure
	sudo('mkdir -p /etc/unicorn')
	sudo('mkdir -p /var/www/resque-web')
	sudo('mkdir -p /var/www/resque-web/shared')
	sudo('mkdir -p /var/www/resque-web/config')
	sudo('mkdir -p /var/www/resque-web/log')
	sudo('mkdir -p /var/www/resque-web/shared')
	sudo('chown -R www-data:www-data /var/www/resque-web')
	sudo('chmod -R 775 /var/www/resque-web')
	put(util.template('etc-init.d-unicorn'), '/etc/init.d/unicorn', use_sudo=True)
	put(util.template('etc-nginx-resque-web'), '/etc/nginx/sites-available/resque-web', use_sudo=True)
	put(util.template('etc-unicorn-resque-web.conf'), '/etc/unicorn/resque-web.conf', use_sudo=True)
	put(util.template('var-www-config.ru'), '/var/www/resque-web/config.ru', use_sudo=True)
	put(util.template('var-www-unicorn.rb'), '/var/www/resque-web/config/unicorn.rb', use_sudo=True)
	put(util.template('var-www-resque.rb'), '/var/www/resque-web/config/resque.rb', use_sudo=True)
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
	# Restart unicorn and nginx
	sudo('/etc/init.d/unicorn restart')
	sudo('/etc/init.d/nginx restart')
	util.done()


 	