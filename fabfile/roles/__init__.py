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

__all__ = []

@task
def server_normalize():	
	"""
	*** SUB-TASK *** Builds a server after normalization of systems/providers

	Set up the correct apt repositories so we can get the 
	# correct packages (Nginx 1.x, PHP-FPM)
	"""
	print('==================================================')
	print('Server Normalize (Common)')
	print('==================================================')
	# Set the debian apt-get non-interactive shell
	sudo('export DEBIAN_FRONTEND=noninteractive')
	print('Creating SSH Key')
	# Create the private/public key for the user on this server
	if not exists('/home/%s/.ssh/id_rsa.pub' % env.user):
		print("... creating new SSH key")
		run('mkdir ~/.ssh')
		# Try to get rid of the prompts
		#prompts = []
		#prompts += expect('What is your name?','Jasper')
		#with expecting(prompts):
		#	expect_run('ssh-keygen -t rsa', pty=False)
		run('ssh-keygen -t rsa', pty=False)
	else:
		print("... using existing SSH key")
	# Add the dotdeb repos
	print('Adding dotdeb Repostories')
	sudo('echo "deb http://packages.dotdeb.org squeeze all" > /etc/apt/sources.list.d/squeeze-dotdeb.list')
	sudo('wget http://www.dotdeb.org/dotdeb.gpg')
	sudo('cat dotdeb.gpg | sudo apt-key add -')
	sudo('rm dotdeb.gpg')
	# Run an update
	sudo('apt-get update')
	print('... done adding dotdeb repos')
	# Install standard packages
	print('Installing Basic Packages')
	sudo('apt-get install -y ntp')
	sudo('apt-get install -y mysql-client')
	sudo('apt-get install -y git-core')
	sudo('apt-get install -y vim')
	print('... done installing basic packages')
	# Install S3FS software
	# NOTE: This needs to be 1.61 even if the latest is 1.69 until the permission
	#       stuff gets fixed 
	print('Installing S3FS')
	s3fs_version = "1.61"
	sudo('apt-get install -y libfuse2')
	sudo('apt-get install -y fuse-utils')
	sudo('apt-get install -y make g++ pkg-config gcc build-essential')
	sudo('apt-get install -y libfuse-dev libxml2 libxml2-dev curl libcurl3 libcurl3-dev')
	with cd('~'):
		sudo('wget http://s3fs.googlecode.com/files/s3fs-%s.tar.gz' % s3fs_version)
		sudo('tar xzvf s3fs-%s.tar.gz' % s3fs_version)
	with cd('~/s3fs-%s' % s3fs_version):
 		sudo('./configure --prefix=/usr')
 		sudo('make')
 	with cd('~/s3fs-%s' % s3fs_version):
 		sudo('make install')
 	print('... done installing S3FS')	
    # New relic
 	print('Installing NewRelic Server Monitor')
 	if (env.newrelic_key):
 		sudo('wget -O /etc/apt/sources.list.d/newrelic.list http://download.newrelic.com/debian/newrelic.list')
		sudo('apt-key adv --keyserver hkp://subkeys.pgp.net --recv-keys 548C16BF')
		sudo('apt-get update')
		sudo('apt-get install newrelic-sysmond')
		sudo('nrsysmond-config --set license_key=%s' % env.newrelic_key)
		sudo('/etc/init.d/newrelic-sysmond start')
		print('... done installing NewRelic')
 	# Set the timezone
 	print('Settings Timezone')
 	print('...')
 	# Make bash the default shell
 	print('Settings /bin/bash as default shell')
 	sudo('chsh -s /bin/bash %s' % env.user)
	print('==================================================')
	print('... done Server Normalize (Common)')
	print('==================================================')