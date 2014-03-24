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
Git
"""

def install():
	util.start()
	#sudo('apt-get install -y ufw')
	util.done()

def configure():
	util.start()
	util.done()

def rsync(project_name, project_dir, app_root, www_root, username):
	util.start()
	# Check to make sure directory exists
	if not exists(www_root):
		print('Creating project folder for web server: %s' % www_root)
		sudo('mkdir -p %s' % www_root)
		sudo('chown -R %s:%s %s' % (username, username, www_root))
		sudo('chmod -R 775 %s' % www_root)
	# Rsync the entire directory over
	print('Performing rsync to %s' % www_root)
	source = '%s%s/%s' % (project_dir.lower(), project_name.lower(), app_root)
	target = www_root
	run("rsync -oavz --exclude 'application/log*' \
				     --exclude 'application/cache*' \
				     %s %s" %
				     (source, target))
	run('mkdir -p %sapplication/cache' % www_root)
	run('mkdir -p %sapplication/logs' % www_root)
	run('chmod -R 777 %sapplication/cache' % www_root)
	run('chmod -R 777 %sapplication/logs' % www_root)
	util.done()


def checkout(project_name, project_dir, branch = ''):
	util.start()
	# Check out source code for the first time (always use master)
	print('Checking out code for the first time')
	if not exists("%s" % project_dir.lower()):
		run('mkdir -p %s' % project_dir.lower())
	if not exists("%s/%s" % (project_dir.lower(), project_name.lower())):
		with cd(project_dir.lower()):
			if (branch != "" and branch != None):
				run('git clone -b %s ssh://git@git-server/%s.git %s' %
					(branch, git_project.lower(), git_project.lower()))
			else:
				run('git clone ssh://git@git-server/%s.git %s' %
				(git_project.lower(), git_project.lower()))
	util.done()


def register(git_hostname, username):
	util.start()
	# Copy the deploy private key to the server
	print("Copying deployment private key to server")
	put(util.template('id_rsa_deploy'), 
		'/home/%s/.ssh/id_rsa_deploy' % username, 
		use_sudo=False, mode=0600)
	# Copy ssh config file to server
	put(util.template('ssh_config'), 
		'/home/%s/.ssh/config' % username, 
		use_sudo=False)
	# Replace tokens in config file
	sed('/home/%s/.ssh/config' % username,
		'\{\{git-server\}\}',
		'%s' % git_hostname,
		use_sudo=False, flags='')
	sed('/home/%s/.ssh/config' % username,
		'\{\{home\}\}',
		'%s' % username,
		use_sudo=False, flags='')
	util.done()
 	