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

"""
Web+App Server Build and Setup
"""

def server_setup():
	"""
	Setup Web+App Server with basic software for "www" role
	"""
	print('==================================================')
	print('Building Web+App Server')
	print('==================================================')
	# Run apt update
	sudo('apt-get update')
	# Install standard packages
	sudo('apt-get install -y nginx')
	sudo('apt-get install -y php5-fpm')
	sudo('apt-get install -y php5-mysql')
	sudo('apt-get install -y php5-gd')
	sudo('apt-get install -y php5-curl')
	sudo('apt-get install -y php5-suhosin')
	sudo('apt-get install -y php-apc')
	sudo('apt-get install -y php-pear')
	sudo('apt-get install -y mcrypt')
	sudo('apt-get install -y php5-mcrypt')
	# Mount S3FS if needed
	mount_s3fs = env.config.get('mount_s3fs')
	document_root = env.config.get('document_root')
	if ('%s' in document_root):
		document_root = document_root % env.git_project.lower()
	# Create document root directory if it doesn't exist
	if not exists(document_root):
		sudo("mkdir -m 775 -p %s" % document_root)
	if (mount_s3fs):
		print("Mounting S3FS to %s" % document_root)
		# Make backup for fstab before we edit
	 	if not exists('/etc/fstab.orig'):
			sudo('cp /etc/fstab /etc/fstab.orig')
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
	# Have php-fpm use a unix socket
	print('Switching php-fpm to socket')
	sed('/etc/php5/fpm/pool.d/www.conf',
		'listen = 127.0.0.1:9000',
		';listen = 127.0.0.1:9000\\nlisten = /var/run/php5-fpm.sock',
		use_sudo=True, backup='.bak', flags='')
	# Enable php for nginx
	print('Routing .php from nginx to php-fpm')
	if exists('/etc/nginx/conf.d/php.conf'):
		sudo('rm /etc/nginx/conf.d/php.conf')
	put('fabfile/lib/www/php.conf', '/etc/nginx/conf.d/php.conf', use_sudo=True)
	# Add custom php.ini settings
	print('Adding custom php.ini settings')
	if exists('/etc/nginx/conf.d/php.conf'):
		if exists('/etc/php5/fpm/conf.d/php-custom.ini'):
			sudo('rm /etc/php5/fpm/conf.d/php-custom.ini')
	put('fabfile/lib/www/php-custom.ini', '/etc/php5/fpm/conf.d/php-custom.ini', use_sudo=True)
	# Restart nginx
	sudo('/etc/init.d/nginx restart')
	# Reload php-fpm
	sudo('/etc/init.d/php5-fpm restart')
	# Install NewRelic PHP Agent
	sudo('wget -O - http://download.newrelic.com/548C16BF.gpg | apt-key add -')
	sudo('echo "deb http://apt.newrelic.com/debian/ newrelic non-free" > /etc/apt/sources.list.d/newrelic.list')
	sudo('apt-get update')
	sudo('apt-get install -y newrelic-php5')
	sudo('newrelic-install')
	sudo('/etc/init.d/newrelic-daemon restart')
	sudo('/etc/init.d/php5-fpm restart')
	sudo('/etc/init.d/nginx restart')
	print('==================================================')
	print('... done Building Web+App Server')
	print('==================================================')


def project_setup():
	"""
	Installs and setup web+app server with project specifics

	This could include:
	(1) Checking out source code for the first time
	    - more work than you would think
	(2) Change web server document root
	(3) Mounting S3 file systems
	(4) Setting timezone
	(5) Possibly refresh database from latest backup
	(6) Install other non-standard software like PEAR
	"""
	print('==================================================')
	print('Setup/Install Project on Web+App Server')
	print('==================================================')
	# Create a unique filename for public key
	# Format is <user>@<host>.pub (the <host> part hopefully is unique)
	user_key = '%s@%s' % (env.user, env.host_string)
	# Grab the public key of the <user> on new machine to the machine
	# currently running the fabric script (local)
	get('/home/%s/.ssh/id_rsa.pub' % env.user, '/tmp/%s.pub' % user_key)
	# Then from local, SCP to git server
	# Hopefully system running fabric (local) can scp to git server
	local('scp /tmp/%s.pub git@%s:/home/git/.ssh/%s.pub' % (user_key, env.git_server, user_key))
	print('SSH into git server @ %s' % env.git_server)
	# SSH into git server and add public key of new machine to git user
	ssh = paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	ssh.connect(env.git_server, username='git')
	print('Add %s public key to authorized_keys of git user' % user_key)
	stdin, stdout, stderr = ssh.exec_command(
		'cat /home/git/.ssh/%s.pub >> /home/git/.ssh/authorized_keys' % user_key)
	stdin, stdout, stderr = ssh.exec_command(
		'mv /home/git/.ssh/%s.pub /home/git/.ssh/x_%s.pub' % (user_key, user_key))
	print stdout.readlines()
	ssh.close();
	# Check out source code for the first time (always use master)
	print('Checking out code for the first time')
	if not exists("%s" % env.project_dir):
		run('mkdir -p %s' % env.project_dir)
	if not exists("%s/%s" % (env.project_dir, env.git_project)):
		with cd(env.project_dir):
			if (env.branch != "" and env.branch != None):
				run('git clone -b %s ssh://git@%s/var/git/%s.git %s' %
					(env.branch, env.git_server, env.git_project, env.git_project))
			else:
				run('git clone ssh://git@%s/var/git/%s.git %s' %
					(env.git_server, env.git_project, env.git_project))
	# Install other software
	# Barcode (Datamatrix)
	sudo('apt-get install -y libdmtx-utils')
	# PDF
	sudo('apt-get install -y pdftk')
	# Mail_Queue
	with settings(warn_only=True):
		sudo('pear install --alldeps Mail_Queue')
		sed('/usr/share/php/Mail/Queue.php',
    		'function isError($value)',
    		'function isError($value, $dummy = "")',
    		use_sudo=True, flags='')
		sudo('pear install --alldeps MDB2-2.5.0b5')
		sudo('pear install --alldeps MDB2_Driver_mysql-1.5.0b4')
	# Get the www_root
	# Do some token replacements if needed
	www_root = env.config.get('www_root')
	if ('%s' in www_root):
		www_root = www_root % env.git_project.lower()
	# Install PEAR Libraries
	# Create new folder in preparation for virtual host
	# TODO: Move/abstract vagrant specific stuff to the provider code??
	provider = env.config.get('provider')
	if (provider == 'vagrant'):
		# Less to do, we just link to the directory
		# on the local machine that has the code for hot deploy
		print("Vagrant project directory already created")
		print("during VM boot in Vagrantfile")
		print("Guest: /var/www/<project>/web")
		print("Host:  ~/Projects/<project>/src/php/kohana")
	else:
		# Check to make sure directory exists
		if not exists(www_root):
			print('Creating project folder for web server: %s' % www_root)
			sudo('mkdir -p %s' % www_root)
			sudo('chown -R %s:%s %s' % (env.user, env.user, www_root))
			sudo('chmod -R 775 %s' % www_root)
		# Rsync the entire directory over
		print('Performing rsync to %s' % www_root)
		source = '%s%s/%s' % (env.project_dir, env.git_project, env.app_root)
		target = www_root
		run("rsync -oavz --exclude 'application/log*' \
					     --exclude 'application/cache*' \
					     %s %s" %
					     (source, target))
		run('mkdir -p %sapplication/cache' % www_root)
		run('mkdir -p %sapplication/logs' % www_root)
		run('chmod -R 777 %sapplication/cache' % www_root)
		run('chmod -R 777 %sapplication/logs' % www_root)
		# Also rsync the 3 legacy folders (asc, business & lib)
		# TODO: Remove this once the legacy stuff is deprecated
		source_base_dir = os.path.dirname(source.rstrip('/'))
		target_base_dir = os.path.dirname(www_root.rstrip('/'))
		sudo('chown -R %s:%s %s' % (env.user, env.user, target_base_dir))
		# (1) asc folder
		run("rsync -oavz %s/asc %s" % (source_base_dir, target_base_dir))
		# (2) business folder
		run("rsync -oavz %s/business %s" % (source_base_dir, target_base_dir))
		# (3) lib folder
		run("rsync -oavz %s/lib %s" % (source_base_dir, target_base_dir))
	# Add new virtual host
	print('Adding new virtual host: %s' % env.host_string)
	# Delete old virtual host file
	if exists('/etc/nginx/sites-available/%s' % env.git_project.lower()):
		print('Found old virtual host, deleting')
		sudo('rm -fR /etc/nginx/sites-available/%s' % env.git_project.lower())
		sudo('rm -fR /etc/nginx/sites-enabled/%s' % env.git_project.lower())
	# Check if we need SSL or not
	enable_ssl = env.config.get('enable_ssl')
	# Deal with SSL portion of site
	if (enable_ssl):
		# Copy some files from lib/ssl to server
		run('rm -fR ~/ssl')
		run('mkdir ~/ssl')
		put('fabfile/lib/ssl/propertyrate.com.bundle.crt', '~/ssl/propertyrate.com.bundle.crt')
		put('fabfile/lib/ssl/www.propertyrate.com.key', '~/ssl/www.propertyrate.com.key')
		nginx_site_file = "nginx-site-ssl";
	else:
		nginx_site_file = "nginx-site";
	print('Copying from local project virtual host')
	put('fabfile/lib/www/%s' % nginx_site_file,
		'/etc/nginx/sites-available/%s' % env.git_project.lower(),
		use_sudo=True)
	print('Replacing some tokens')
	# TODO: Token needs to be sync'd with Vagrantfile share folders
	# TODO: Token needs to by sync'd with dev_chris.py
	# TODO: Token needs to by sync'd with main fabric __init__.py
	sed('/etc/nginx/sites-available/%s' % env.git_project.lower(),
		'\{\{www_root\}\}',
		'%s' % www_root,
		use_sudo=True, backup='.bak', flags='')
	# Munge the server_names to create a unique list
	# TODO: Move to separate function
	server_names = env.config.get('server_names', "")
	if (server_names != "" and server_names['www'] != ""):
		server_names = server_names['www']
		server_names.append(env.host_string)
		server_names = set(server_names)
		nginx_server_name = " ".join(server_names)
	else:
		nginx_server_name = env.host_string
	print("Setting nginx server_name: %s" % nginx_server_name)
	sed('/etc/nginx/sites-available/%s' % env.git_project.lower(),
		'\{\{localhost\}\}',
		'%s' % nginx_server_name,
		use_sudo=True, backup='.bak', flags='')
	# Symlink to enable site
	print('Creating symlink to project virtual host')
	sudo('ln -s /etc/nginx/sites-available/%s /etc/nginx/sites-enabled/%s' %
		 (env.git_project.lower(), env.git_project.lower()))
	# Add custom php.ini
	print('Restart nginx & php-fpm')
	sudo('/etc/init.d/nginx restart')
	sudo('/etc/init.d/php5-fpm restart')
	# Create/mount global file storage
	document_root = env.config.get('document_root')
	mount_s3fs = env.config.get('mount_s3fs')
	# Mount S3FS
	if (mount_s3fs):
	 	# Test a bunch of things here
	 	if not exists(document_root):
	 		sudo('mkdir -p -m 777 %s' % document_root)
	 	else:
	 		with settings(warn_only=True):
				sudo('fusermount -u %s' % document_root)
		print("Mounting S3FS ...")
		print('Create s3fs passwd file')
		sudo('echo %s:%s > /etc/passwd-s3fs' %
			 (env.aws_access_key, env.aws_secret_key))
		sudo('chown root:root /etc/passwd-s3fs')
		sudo('chmod 400 /etc/passwd-s3fs')
		print('Update fstab to automount')
		if not exists('/etc/fstab.orig'):
			sudo('cp /etc/fstab /etc/fstab.orig')
		if exists('/etc/fstab.orig'):
			sudo('rm /etc/fstab')
			sudo('cp /etc/fstab.orig /etc/fstab')
		sudo('echo "\n" >> /etc/fstab')
		sudo('echo "s3fs#%s	%s	fuse	allow_other	0	0" >> /etc/fstab' %
			 (env.aws_bucket, document_root))
		sudo('mount -a')
	# Not mounting S3FS
	else:
		print("NOT mounting S3FS")
		sudo('rm -fR %s' % document_root)
		sudo('mkdir -p -m 777 %s' % document_root)
		# Create the remainder of the document subdirectories
		document_dirs = ['database/',
						 'documents/archive/',
						 'documents/file/',
						 'documents/inbox/',
						 'documents/temp/',
						 'documents/upload/',
						 'resque/failures/',
						]
		for document_dir in document_dirs:
			if not exists("%s%s" % (document_root, document_dir)):
				#print "%s%s" % (document_root, document_dir)
				sudo("mkdir -m 777 -p %s%s" % (document_root, document_dir))
				if not (mount_s3fs):
					sudo("chmod +t %s%s" % (document_root, document_dir))
	# Set timezone
	sudo('echo "%s" > /etc/timezone' % env.timezone)
	sudo('dpkg-reconfigure -f noninteractive tzdata')
	print('==================================================')
	print('... done Setup/Install Project on Web+App Server')
	print('==================================================')

