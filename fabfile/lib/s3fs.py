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
S3FS
"""

def install():
	util.start()
	if (not(util.enabled('s3fs'))):
		util.done('Not enabled in environment settings')
		return
	s3fs_version = "1.61"
	sudo('apt-get install -yq libfuse2')
	sudo('apt-get install -yq fuse-utils')
	sudo('apt-get install -yq make g++ pkg-config gcc build-essential')
	sudo('apt-get install -yq libfuse-dev libxml2 libxml2-dev curl libcurl3 libcurl3-dev')
	with cd('~'):
		sudo('wget http://s3fs.googlecode.com/files/s3fs-%s.tar.gz' % s3fs_version)
		sudo('tar xzvf s3fs-%s.tar.gz' % s3fs_version)
	with cd('~/s3fs-%s' % s3fs_version):
 		sudo('./configure --prefix=/usr')
 		sudo('make')
 	with cd('~/s3fs-%s' % s3fs_version):
 		sudo('make install')
 	util.done()

def configure():
	util.start()
	util.done()

def mount(mount_root, aws_buckets):
	util.start()
	if (not(util.enabled('s3fs'))):
		util.done('Not enabled in environment settings')
		return
	# Create the password file
	print("Mounting S3FS ...")
	if exists('/etc/passwd-s3fs'):
		print("Delete existing passwd file ...")
		sudo('rm -fR /etc/passwd-s3fs')	
	print('Create s3fs passwd file')
	sudo('touch /etc/passwd-s3fs')
	for aws_bucket in aws_buckets:
		sudo('echo %s:%s:%s >> /etc/passwd-s3fs' %
		     (aws_bucket['name'], aws_bucket['access_key'], aws_bucket['secret_key']))
	sudo('chown root:root /etc/passwd-s3fs')
	sudo('chmod 400 /etc/passwd-s3fs')
	# Update fstab
	print('Update fstab to automount')
	# If this is the first ever touch, the .orig file should not exist
	if not exists('/etc/fstab.orig'):
		sudo('cp /etc/fstab /etc/fstab.orig')
	# Backup the current fstab with timestamp as well
	sudo('cp /etc/fstab /etc/%s' % util.timestamp('fstab'))
	# If the fstab.orig file exists, this means that this is NOT
	# the first time fabric has come around so we want to copy 
	# the original 
	if exists('/etc/fstab.orig'):
		sudo('rm /etc/fstab')
		sudo('cp /etc/fstab.orig /etc/fstab')
	for aws_bucket in aws_buckets:
		mount_point = "%s%s" % (mount_root, aws_bucket['mount'])
		print("Mounting bucket: %s => %s" % (aws_bucket['name'], mount_point))
		sudo('echo "\n" >> /etc/fstab')
		# s3fs#s3fs.domain.com	/mnt/s3fs/	fuse	allow_other	0	0
		sudo('echo "s3fs#%s	%s	fuse	allow_other	0	0" >> /etc/fstab' %
		     (aws_bucket['name'], mount_point))
	sudo('mount -a')
	util.done()
