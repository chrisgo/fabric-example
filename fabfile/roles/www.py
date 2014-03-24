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
from fabfile.lib import *

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
	sudo('export DEBIAN_FRONTEND=noninteractive')
	# Run apt update
	sudo('apt-get update')
	# Nginx & PHP
	nginx.install()
	php.install()
	nginx.configure()
	php.configure()
	# NewRelic
	newrelic.install_php_agent()
	# Papertrail
	#papertrail.install()
	#papertrail.configure()
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
	sudo('export DEBIAN_FRONTEND=noninteractive')
	# Get some variables from the environment
	print("Setting up environment ...")
	provider 		= env.config.get('provider')
	mount_root 		= env.config.get('mount_root', "/tmp/")
	www_root		= env.config.get('www_root', "")
	aws_buckets 	= env.aws_buckets if ('aws_buckets' in env) else ""
	app_dirs		= env.app_dirs if ('app_dirs' in env) else ""
	if ('%s' in www_root):
		www_root = www_root % env.git_project.lower()
	# Checkout project from git
	if (provider != 'vagrant'):
		print("Checking out project from git")
		git.register(env.git_server, env.user)
		git.checkout(env.git_project, env.project_dir)
		git.rsync(env.git_project, env.project_dir, env.app_root, www_root, env.user)
	else:
		print("Vagrant project directory already created")
		print("during VM boot in Vagrantfile")
		print("Guest: /var/www/<project>/web")
		print("Host:  ~/Projects/<project>/src/php/kohana")
	# Add host to nginx
	nginx.add_host(env.git_project, 
				   www_root, 
				   env.host_string, 
				   env.config.get('environment', ""), 
				   env.config.get('server_names', ""))
	# Symlink to enable site
	print('Creating symlink to project virtual host')
	sudo('ln -s /etc/nginx/sites-available/%s /etc/nginx/sites-enabled/%s' %
		 (env.git_project.lower(), env.git_project.lower()))
	# Add custom php.ini
	print('Restart nginx & php-fpm')
	sudo('/etc/init.d/nginx restart')
	sudo('/etc/init.d/php5-fpm restart')
	# Mount project folders (whatever is defined)
	print("Mounting project directories ...")
	# Create the directories for the S3 mount points
	if (aws_buckets):
		directories = []
		for aws_bucket in aws_buckets:
			directories.append("%s%s" % (mount_root, aws_bucket['mount']))
		filesystem.mkdirs(directories)
	# Mount S3
	if (util.enabled('s3fs')):
		s3fs.mount(mount_root, aws_buckets)
	else:
		print("NOT mounting S3FS")
	# Create directories for the project/application
	print("Creating project directories")
	if (app_dirs):
		directories = []
		for app_dir in app_dirs:
			directories.append("%s%s" % (mount_root, app_dir))
		filesystem.mkdirs(directories)
	# ==================================================
	# Install other software here
	# ==================================================
	print("Installing project-specific software ...")
	print(" Barcode/Datamatrix")
	sudo('apt-get install -yq libdmtx-utils')
	print(" PDFtk")
	sudo('apt-get install -yq pdftk')
	print(" PEAR MailQueue")
	# Mail_Queue
	with settings(warn_only=True):
		#sudo('pear uninstall Mail_Queue')
		sudo('pear install --alldeps Mail_Queue')
		sed('/usr/share/php/Mail/Queue.php',
    		'function isError($value)',
    		'function isError($value, $dummy = "")',
    		use_sudo=True, flags='')
		#sudo('pear uninstall MDB2-2.5.0b5')
		sudo('pear install --alldeps MDB2-2.5.0b5')
		#sudo('pear uninstall MDB2_Driver_mysql-1.5.0b4')
		sudo('pear install --alldeps MDB2_Driver_mysql-1.5.0b4')
	# Trigger legacy
	project_legacy()
	print('==================================================')
	print('... done Setup/Install Project on Web+App Server')
	print('==================================================')

def project_legacy():
	provider = env.config.get('provider', "")
	www_root = env.config.get('www_root', "")
	source = '%s%s/%s' % (env.project_dir, env.git_project.lower(), env.app_root)
	target = www_root
	# Do some token replacements if needed
	if ('%s' in www_root):
		www_root = www_root % env.git_project.lower()
	# ==================== START LEGACY ====================
	# Also rsync the 3 legacy folders (asc, business & lib)
	# TODO: Remove this once the legacy stuff is deprecated
	if (provider != 'vagrant'):
		source_base_dir = os.path.dirname(source.rstrip('/'))
		target_base_dir = os.path.dirname(www_root.rstrip('/'))
		sudo('chown -R %s:%s %s' % (env.user, env.user, target_base_dir))
		# (1) asc folder
		run("rsync -oavz %s/asc %s" % (source_base_dir, target_base_dir))
		# (2) business folder
		run("rsync -oavz %s/business %s" % (source_base_dir, target_base_dir))
		# (3) lib folder
		run("rsync -oavz %s/lib %s" % (source_base_dir, target_base_dir))
