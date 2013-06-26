from __future__ import with_statement
from fabric.api import *
from fabric.contrib.console import confirm
from fabric.contrib.files import *
import paramiko
import os
import json
import datetime

"""
Set up Amazon EC2 to a normalized state to run base server setup

EC2 requires you to login using a private key (.pem) file that you
create on the Amazon EC2 web console and then download to your local
system and use as a private key when connecting 
"""

def normalize():
	"""
	Normalize the Amazon EC2 system/provider
	"""
	print('==================================================')
	print('Amazon EC2')
	print('==================================================')



	print('==================================================')
	print('... done Amazon EC2')
	print('==================================================')
	# Then run base server setup
	#execute('servers.base_server')
