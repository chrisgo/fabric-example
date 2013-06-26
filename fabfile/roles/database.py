from __future__ import with_statement
from fabric.api import *
from fabric.contrib.console import confirm
from fabric.contrib.files import *
from fabric.utils import warn
import paramiko
import os
import json
import datetime
from fabtools import require
import fabtools

"""
Database Server Build and Setup
"""

def server_setup():
	"""
	Setup Database Server with basic software for "database" role
	"""
	print('==================================================')
	print('Building Database Server')
	print('==================================================')
	# Run apt update
	sudo('apt-get update')
	# Install standard packages
	with settings(hide('warnings', 'stderr'), warn_only=True):
		result = sudo('dpkg-query --show mysql-server')
		if ("No packages" in result):
			print("Installing MySQL ...")
			sudo('echo "mysql-server-5.5 mysql-server/root_password password ' \
                 '%s" | debconf-set-selections' % env.password)
			sudo('echo "mysql-server-5.5 mysql-server/root_password_again password ' \
                 '%s" | debconf-set-selections' % env.password)
			sudo('apt-get install -y mysql-server')
	# Open up mysql 
	sed('/etc/mysql/my.cnf', 
		'bind-address		= 127.0.0.1', 
		'bind-address		= 0.0.0.0', 
		use_sudo=True, backup='.bak', flags='')
	# Update root password (do we need to do this??)
	#query = "update user set password=PASSWORD('%s') where user='root';" % (env.password)
	#run('mysql --batch --raw --skip-column-names --user=root --execute="%s"' % query)
	#print("Updated database root user password")
	sudo('/etc/init.d/mysql restart')
	# Install Percona XtraBackup (Hot backup software)
	put('fabfile/lib/database/etc-apt-percona.list', 
		'/etc/apt/sources.list.d/percona.list', 
		use_sudo=True)
	sudo('apt-key adv --keyserver keys.gnupg.net --recv-keys 1C4CBDCDCD2EFD2A')
	sudo('apt-get update')
	sudo('apt-get install -y xtrabackup')
	# Install automysqlbackup
	sudo('apt-get install -y automysqlbackup')
	# Load timezone info
	run('mysql_tzinfo_to_sql /usr/share/zoneinfo | mysql --user=%s --password=%s mysql' %
		('root', env.password))
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
				sudo('umount %s' % document_root)
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
		with settings(warn_only=True):
			sudo('umount %s' % document_root)
		sudo('mount -a')
	# Not mounting S3FS
	else:
		print("NOT mounting S3FS")
	print('==================================================')
	print('... done Building Database Server')
	print('==================================================')


def project_setup():
	"""
	Installs and setup Database server with project specifics
	"""
	print('==================================================')
	print('Setup/Install Project on Database Server')
	print('==================================================')
	# Create Database(s) 
	for database in env.databases:
		#print("Checking database: %s" % database)
		if not fabtools.mysql.database_exists(database, mysql_user='root', mysql_password=env.password):
			# Create database
			query = "CREATE DATABASE %s CHARACTER SET utf8 COLLATE utf8_general_ci;" % database
			run('mysql --batch --raw --skip-column-names --user=%s --password=%s --execute="%s"' %
				('root', env.password, query))
			print("Database schema %s created" % database)
			# Also create the user for the "user"@"%" for the database 
			# The line above only create "user"@"localhost"
			query = "GRANT ALL PRIVILEGES ON %s.* TO '%s'@'localhost' " \
			        "IDENTIFIED BY '%s' WITH GRANT OPTION;" % (database, env.user, env.password)
			run('mysql --batch --raw --skip-column-names --user=%s --password=%s --execute="%s"' %
				('root', env.password, query))
			query = "GRANT ALL PRIVILEGES ON %s.* TO '%s'@'%s' " \
			        "IDENTIFIED BY '%s' WITH GRANT OPTION;" % (database, env.user, "%", env.password)
			run('mysql --batch --raw --skip-column-names --user=%s --password=%s --execute="%s"' %
				('root', env.password, query))
			print("User %s granted access" % env.user)
	#sudo('/etc/init.d/mysql restart')
	# TODO: Figure out how to get data into the DEV database
	#
	# (1) Go to replicated database
	#     - mysqldump to local file on server 
	#     - mysqldump into dev database
	#     - http://www.iangeorge.net/articles/2010/jul/22/getting-live-data-mysqldump-and-fabric/
	# (2) Use boto, grab latest dump from nightly backup
	#     - Use boto to copy from /mnt/s3fs/database/latest
	#     - Unzip file and mysqldump into dev database
	# (3) SCP from another server that has S3FS mounted
	# 
	# run('mysqldump --user %s --password=%s %s | gzip > /tmp/%s.sql.gz' % (
    #            settings_dev.DATABASES['default']['USER'], 
    #            settings_dev.DATABASES['default']['PASSWORD'], 
    #            settings_dev.DATABASES['default']['NAME'],
    #            settings_dev.DATABASES['default']['NAME'] 
    #            ))
    #    put('/tmp/%s.sql.gz' % env.database, '/tmp/%s.sql.gz' % env.database)
    #   run('gunzip < /tmp/%s.sql.gz | mysql -u %s -p%s -D %s' % (
    #            env.database, 
    #           env.db_user, 
    #            env.db_password, 
    #            env.database
    #            ), capture=False)
	#for database in env.databases:
	#    print("Loading %s ... this may take a while ..." % database)
	#    run("mysql -u root --password=%s %s < ~/%s.sql" % 
	#        (env.password, database, database))

	print('==================================================')
	print('... done Setup/Install Project on Database Server')
	print('==================================================')
	
	