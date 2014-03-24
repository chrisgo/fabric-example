from __future__ import with_statement
from fabric.api import *
from fabric.contrib.console import confirm
from fabric.contrib.files import *
import paramiko
import os
import json
import datetime
import inspect
import time

"""
Util
"""

def start():
	module_name = ''
	function_name = ''
	stack = inspect.stack()
	parentframe = stack[1][0]
	module = inspect.getmodule(parentframe)
	if module:
		module_pieces = (module.__name__).split('.')
		module_name = module_pieces[-1].capitalize()
	function_name = stack[1][3]
	title = "Starting %s.%s()" % (module_name, function_name)
	dashes = '-' * (49-len(title))
	print("%s %s" % (title, dashes))

def done(error = ''):
	module_name = ''
	function_name = ''
	stack = inspect.stack()
	parentframe = stack[1][0]
	module = inspect.getmodule(parentframe)
	if module:
		module_pieces = (module.__name__).split('.')
		module_name = module_pieces[-1].capitalize()
	function_name = stack[1][3]
	title = "%s.%s()" % (module_name, function_name)
	if (error == ''):
		print("... done %s" % title)
	else:
		print("... NOT done %s - %s" % (title, error))

def template(filename):
	module_name = ''
	stack = inspect.stack()
	parentframe = stack[1][0]
	module = inspect.getmodule(parentframe)
	if module:
		module_pieces = (module.__name__).split('.')
		module_name = module_pieces[-1]
		return "fabfile/lib/templates/%s/%s" % (module_name, filename)
	else:
		return "fabfile/lib/templates/%s" % (filename)

def environment():
	environment = env.config.get('environment')
	return environment

def is_production():
	environment = env.config.get('environment')
	if (environment=='PRODUCTION'):
		return True
	else:
		return False

def timestamp(filename = ""):
	date_string = time.strftime("%Y-%m-%d.%H:%M:%S") # "%d/%m/%Y"
	if (filename != ""):
		return "filename.%s" % date_string
	else:
		return "%s" % date_string

def enabled(module):
	return env.config.get('enables').get(module, False)

