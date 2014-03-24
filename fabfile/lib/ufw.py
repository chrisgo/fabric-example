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
UFW
"""

def install():
	util.start()
	sudo('apt-get install -yq ufw')
	util.done()

def configure():
	util.start()
	# http://guides.webbynode.com/articles/security/ubuntu-ufw.html
	# http://niteowebfabfile.readthedocs.org/en/latest/_modules/niteoweb/fabfile/server.html
	print("Enabling UFW (firewall)")
	# Change some things per here to eliminate errors
	# http://blog.kylemanna.com/linux/2013/04/26/ufw-vps/
	sed('/etc/default/ufw',
		'IPV6=yes',
		'IPV6=no',
		use_sudo=True, backup='.bak', flags='')
	sed('/etc/default/ufw',
		'IPT_MODULES=',
		'#IPT_MODULES=',
		use_sudo=True, backup='.bak', flags='')
	# Reset
	sudo('ufw --force reset')
	# Apply rules
	sudo('ufw default deny')
	sudo('ufw allow 22')	# ssh
	sudo('ufw allow 80')	# web/http
	sudo('ufw allow 443')   # web/https
	sudo('ufw allow 3306')  # mysql
	sudo('ufw allow 5678')  # resque-web
	sudo('ufw allow 6379')  # redis
	# re-enable firewall and print rules
	sudo('ufw --force enable')
	sudo('ufw status verbose')
	util.done()


 	