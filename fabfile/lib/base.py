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
Base Packages
"""

def add_keys():
	util.start()
	# Create the private/public key for the user on this server
	if not exists('/home/%s/.ssh/id_rsa.pub' % env.user):
		print("... creating new SSH key")
		run('mkdir ~/.ssh')
		# Try to get rid of the prompts
		#prompts = []
		#prompts += expect('What is your name?','Jasper')
		#with expecting(prompts):
		#	expect_run('ssh-keygen -t rsa', pty=False)
		# http://unix.stackexchange.com/questions/69314/automated-ssh-keygen-without-passphrase-how
		# ssh-kegen -b 2048 -t rsa -f /tmp/sshkey -q -N ""
		# 
		#run('ssh-keygen -t rsa', pty=False)
		run('ssh-kegen -t rsa -f /tmp/sshkey -q -N ""', pty=False)
		util.done()
	else:
		util.done('Existing key found')

def install():
	util.start()
	print('Adding dotdeb repostories ...')
	print('Dotdeb ...')
	sudo('echo "deb http://packages.dotdeb.org wheezy all" >> /etc/apt/sources.list.d/wheezy-dotdeb.list')
	sudo('echo "deb-src http://packages.dotdeb.org wheezy all" >> /etc/apt/sources.list.d/wheezy-dotdeb.list')
	sudo('wget http://www.dotdeb.org/dotdeb.gpg')
	sudo('cat dotdeb.gpg | sudo apt-key add -')
	sudo('rm dotdeb.gpg')
	# Run an update
	sudo('apt-get update')
	#sudo('DEBIAN_FRONTEND=noninteractive apt-get -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" dist-upgrade')
	sudo('apt-get install -yq ntp')
	sudo('apt-get install -yq mysql-client')
	sudo('apt-get install -yq git-core')
	sudo('apt-get install -yq vim')
	util.done()

def configure():
	util.start()
	# Set the timezone
 	print('Setting Timezone')
 	# Set timezone
	sudo('echo "%s" > /etc/timezone' % env.timezone)
	sudo('dpkg-reconfigure -f noninteractive tzdata')
 	# Make bash the default shell
 	print('Settings /bin/bash as default shell')
 	sudo('chsh -s /bin/bash %s' % env.user)
 	# Make vim the default editor
 	# http://shallowsky.com/blog/linux/ubuntu-default-browser.html
 	#sudo rm /etc/alternatives/gnome-www-browser
	# sudo ln -s /usr/local/firefox11/firefox /etc/alternatives/gnome-www-browser
	# sudo rm /etc/alternatives/x-www-browser
	# sudo ln -s /usr/local/firefox11/firefox /etc/alternatives/x-www-browser
	#sudo('update-alternatives --config editor')
 	util.done()
 	
