from __future__ import with_statement
from fabric.api import *
from fabric.contrib.console import confirm
from fabric.contrib.files import *
import paramiko
import os
import json
import datetime

"""
Set up DigitalOcean to a normalized state to run base server setup

To reset a DigitalOcean droplet:

1) Login to http://digitalocean.com 
2) Decide on name like dev-www.domain.com, staging-www.domain.com, etc.
3) Create a new Droplet using image: Debian 6.0 x64 
4) Login to GoDaddy and create DNS entry to match name and IP address
5) DigitalOcean will email you the root password
6) SSH into new server (using IP) and change root password to 

   env.password in environments/__init__.py

"""

def normalize():
	"""
	Normalize the DigitalOcean system/provider
	"""
	print('==================================================')
	print('DigitalOcean')
	print('==================================================')
	print('Setting env.user to root (for now)')
	env.user = 'root'
	# Set the debian apt-get non-interactive shell
	run('export DEBIAN_FRONTEND=noninteractive')
	# Do update and upgrade for latest security patches
	run('apt-get update')
	run('apt-get upgrade --show-upgraded --yes')
	# Create standard user 
	print('Setting up non-root standard user (%s) ...' % env.base_user)
	if not exists('/home/%s' % env.base_user):
		run('useradd -m %s' % env.base_user)
		run('echo "%s:%s"|chpasswd' % (env.base_user, env.base_password))
	else:
		print("User found: %s" % env.base_user)
	# Install and configure sudo
	print('Setting up sudo ...')
	run('apt-get install sudo')
	if not exists('/etc/sudoers.orig'):
		run('cp /etc/sudoers /etc/sudoers.orig')
		#run('chmod 0640 /etc/sudoers.orig')
	run('echo "%s	ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers' % env.base_user)
	# Setup static IP
	print('Setting up static IP ...')
	# Get the IP address
	# http://www.if-not-true-then-false.com/2010/linux-get-ip-address/
	ip = run('/sbin/ifconfig eth0 | grep "inet addr" | awk -F: \'{print $2}\' | awk \'{print $1}\'')
	# Use static IP to guess the gateway (xxx.xxx.xxx.1)
	gateway = '%s.%s.%s.1' % (ip.split('.')[0], ip.split('.')[1], ip.split('.')[2])
	# http://library.linode.com/networking/configuring-static-ip-interfaces
	# Set the hostname
	#run('echo "%s" > /etc/hostname' % env.host_string.split('.')[0])
	#run('hostname -F /etc/hostname')
	# /etc/hosts file
	#if not exists('/etc/hosts.orig'):
	#	sudo('cp /etc/hosts /etc/hosts.orig')
	#cmd = 'echo -e "%s \t %s \t %s" >> /etc/hosts' % (ip, env.host_string, env.host_string.split('.')[0])
	#run(cmd)
	# Disable root ssh access (do this at the end)
	print('Disable ssh for root user ...')
	# This basically kicks you out as root and need to login as somebody else
	#sed('/etc/ssh/sshd_config', 'PermitRootLogin yes', 'PermitRootLogin no', use_sudo=True, backup='.bak', flags='')
	#run('/etc/init.d/ssh restart')
	print('Setting env.user back to %s' % env.base_user)
	env.user = env.base_user
	print('==================================================')
	print('... done DigitalOcean')
	print('==================================================')
