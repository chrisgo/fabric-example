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
from fabfile.lib import *

"""
Worker Server Build and Setup
"""

def server_setup():
	"""
	Setup Worker Server with basic software for "worker" role
	"""
	print('==================================================')
	print('Building Worker Server')
	print('==================================================')
	sudo('export DEBIAN_FRONTEND=noninteractive')
	# Run apt update
	sudo('apt-get update')
	print('==================================================')
	print('... done Building Worker Server')
	print('==================================================')


def project_setup():
	"""
	"""
	print('==================================================')
	print('Setup/Install Project on Worker Server')
	print('==================================================')
	sudo('export DEBIAN_FRONTEND=noninteractive')
	# Get some variables from the environment
	print('==================================================')
	print('... done Setup/Install Project on Worker Server')
	print('==================================================')
