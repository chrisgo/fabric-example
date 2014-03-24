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
PHP
"""

def install():
	util.start()
	sudo('apt-get install -yq php5-fpm')
	sudo('apt-get install -yq php5-mysql')
	sudo('apt-get install -yq php5-gd')
	sudo('apt-get install -yq php5-curl')
	# May not be needed anymore
	#http://stackoverflow.com/questions/14405053/is-php-5-4-safe-without-suhosin
	#sudo('apt-get install -y php5-suhosin')
	sudo('apt-get install -yq php-apc')
	sudo('apt-get install -yq php-pear')
	sudo('apt-get install -yq mcrypt')
	sudo('apt-get install -yq php5-mcrypt')
	util.done()

def configure():
	util.start()
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
	put(util.template('php.conf'), '/etc/nginx/conf.d/php.conf', use_sudo=True)
	# Add custom php.ini settings
	print('Adding custom php.ini settings')
	if exists('/etc/nginx/conf.d/php.conf'):
		if exists('/etc/php5/fpm/conf.d/php-custom.ini'):
			sudo('rm /etc/php5/fpm/conf.d/php-custom.ini')
	put(util.template('php-custom.ini'), '/etc/php5/fpm/conf.d/php-custom.ini', use_sudo=True)
	# Reload php-fpm
	sudo('/etc/init.d/php5-fpm restart')
	util.done()


 	