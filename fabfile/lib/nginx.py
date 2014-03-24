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
Nginx
"""

def install():
	util.start()
	sudo('apt-get install -yq nginx')
	util.done()

def configure():
	util.start()
	# Nginx conf changes
	sed('/etc/nginx/nginx.conf',
		'# server_names_hash_bucket_size 64',
		'server_names_hash_bucket_size 64',
		use_sudo=True, backup='.bak', flags='')
	# Nginx breaks due to 2 port 80 listeners
	sed('/etc/nginx/sites-available/default',
		'listen ',
		'#listen ',
		use_sudo=True, flags='')
	# Restart nginx
	sudo('/etc/init.d/nginx restart')
	# TODO: Load up check.php for Amazon health check
	put(util.template('check.php'), '/usr/share/nginx/html/check.php', use_sudo=True)
	util.done()

def add_host(project_name, 
			 www_root, 
			 host_string,
			 environment = "DEVELOPMENT",
			 server_names = ""):
	util.start()
	project_name = project_name.lower()
	# Add new virtual host
	print('Adding new virtual host: %s' % host_string)
	# Delete old virtual host file
	if exists('/etc/nginx/sites-available/%s' % project_name):
		print('Found old virtual host, archiving')
		orig = '/etc/nginx/sites-available/%s' % project_name
		backup = '/etc/nginx/sites-available/%s' % util.timestamp(project_name)
		sudo('mv %s %s' % (orig, backup))
		#sudo('rm -fR /etc/nginx/sites-available/%s' % project_name)
		sudo('rm -fR /etc/nginx/sites-enabled/%s' % project_name)
	# Deal with SSL portion of site
	if (util.enabled('ssl')):
		# Copy some files from lib/ssl to server
		run('rm -fR ~/ssl')
		run('mkdir ~/ssl')
		put('fabfile/project/ssl/%s.com.bundle.crt' % project_name, 
			'~/ssl/%s.com.bundle.crt' % project_name)
		put('fabfile/project/ssl/%s.com.key' % project_name, 
			'~/ssl/%s.com.key' % project_name)
		nginx_site_file = "nginx-site-ssl";
	else:
		nginx_site_file = "nginx-site";
		print('Copying from local project virtual host')
	put(util.template("%s") % nginx_site_file,
		'/etc/nginx/sites-available/%s' % project_name,
		use_sudo=True)
	print('Replacing some tokens')
	# TODO: Token needs to be sync'd with Vagrantfile share folders
	# TODO: Token needs to by sync'd with dev_chris.py
	# TODO: Token needs to by sync'd with main fabric __init__.py
	sed('/etc/nginx/sites-available/%s' % project_name,
		'\{\{www_root\}\}',
		'%s' % www_root,
		use_sudo=True, backup='.bak', flags='')
	# Munge the server_names to create a unique list
	# TODO: Move to separate function
	if (server_names != "" and server_names['www'] != ""):
		server_names = server_names['www']
		server_names.append(host_string)
		server_names = set(server_names)
		nginx_server_name = " ".join(server_names)
	else:
		nginx_server_name = host_string
	print("Setting nginx server_name: %s" % nginx_server_name)
	sed('/etc/nginx/sites-available/%s' % project_name,
		'\{\{localhost\}\}',
		'%s' % nginx_server_name,
		use_sudo=True, backup='.bak', flags='')
	sed('/etc/nginx/sites-available/%s' % project_name,
		'\{\{environment\}\}',
		'%s' % environment,
		use_sudo=True, backup='.bak', flags='')
	util.done()



 	