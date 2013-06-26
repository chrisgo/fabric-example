from __future__ import with_statement
from fabric.api import *
from fabric.contrib.console import confirm
from fabric.contrib.files import *
import paramiko
import os
import json
import datetime

"""
Set up Vagrant to a normalized state to run base server setup

Vagrant creates a default user vagrant/vagrant that has sudo powers.
We use this to create the base user and right now, we don't touch
the su user at all

To reset a vagrant box:

cd ~/Servers/Project (directory with Vagrantfile)
vagrant destroy
vagrant up

"""

def normalize():
	"""
	Normalize the Vagrant system/provider
	"""
	print('==================================================')
	print('Vagrant')
	print('==================================================')
	with settings(user = 'vagrant', password = 'vagrant'):
		# Set the debian apt-get non-interactive shell
		run('export DEBIAN_FRONTEND=noninteractive')
		# Set the root password to a known password (???)
		# Do update and upgrade for latest security patches
		sudo('apt-get update')
		sudo('apt-get upgrade --show-upgraded --yes')
		# Install and configure sudo
		print('Setting up sudo ...')
		sudo('cp /etc/sudoers /etc/sudoers.tmp')
		sudo('chmod 0640 /etc/sudoers.tmp')
		sudo('echo "%s	ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers.tmp' % env.base_user)
		sudo('chmod 0440 /etc/sudoers.tmp')
		sudo('mv /etc/sudoers.tmp /etc/sudoers')
		# Create standard user (chris)
		print('Setting up non-root standard user (%s) ...' % env.base_user)
		if not exists('/home/%s' % env.base_user):
			sudo('useradd -m %s' % env.base_user)
			sudo('echo "%s:%s"|chpasswd' % (env.base_user, env.base_password))
		else:
			print("User found: %s" % env.base_user)
		# Setup static IP
		print('Setting up static IP ...')
		# Not sure if this is needed
		print('Disable ssh for root user ...')
		# This basically kicks you out as root and need to login as somebody else
		#sed('/etc/ssh/sshd_config', 'PermitRootLogin yes', 'PermitRootLogin no', use_sudo=True, backup='.bak', flags='')
		#sudo('/etc/init.d/ssh restart')
	print('==================================================')
	print('... done Vagrant')
	print('==================================================')
	


