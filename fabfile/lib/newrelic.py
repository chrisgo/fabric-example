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
NewRelic

Only do this for PRODUCTION servers
"""

def install():
	util.start()
	if (not(env.newrelic_key)):
		util.done('Missing Key')
		return
	if (not(util.enabled('newrelic'))):
		util.done('Not enabled in environment settings')
		return
	sudo('wget -O /etc/apt/sources.list.d/newrelic.list http://download.newrelic.com/debian/newrelic.list')
	sudo('apt-key adv --keyserver hkp://subkeys.pgp.net --recv-keys 548C16BF')
	sudo('apt-get update')
	sudo('apt-get install -yq newrelic-sysmond')
	util.done()

def configure():
	util.start()
	if (not(env.newrelic_key)):
		util.done('Missing Key')
		return
	if (not(util.enabled('newrelic'))):
		util.done('Not enabled in environment settings')
		return
	sudo('nrsysmond-config --set license_key=%s' % env.newrelic_key)
	sudo('/etc/init.d/newrelic-sysmond start')
	util.done()

def install_php_agent():
	util.start()
	if (not(env.newrelic_key)):
		util.done('Missing Key')
		return
	if (not(util.enabled('newrelic'))):
		util.done('Not enabled in environment settings')
		return
	sudo('wget -O - http://download.newrelic.com/548C16BF.gpg | apt-key add -')
	sudo('echo "deb http://apt.newrelic.com/debian/ newrelic non-free" > /etc/apt/sources.list.d/newrelic.list')
	sudo('apt-get update')
	sudo('apt-get install -yq newrelic-php5')
	sudo('newrelic-install')
	sudo('/etc/init.d/newrelic-daemon restart')
	sudo('/etc/init.d/php5-fpm restart')
	sudo('/etc/init.d/nginx restart')
	util.done()

def install_mysql_agent():
	util.start()
	if (not(env.newrelic_key)):
		util.done('Missing Key')
		return
	if (not(util.enabled('newrelic'))):
		util.done('Not enabled in environment settings')
		return
	# Do it
	util.done()



