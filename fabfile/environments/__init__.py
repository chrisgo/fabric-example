from __future__ import with_statement
from fabric.api import *
from fabric.contrib.console import confirm
from fabric.contrib.files import *

"""
This file contains project-specific general settings
Environment-specific settings go into the environments folder
"""

# Fabric Variables (Project)

env.base_user		= "chris"
env.base_password   = "password"
env.git_project     = "project_name"
env.app_root        = 'src/php/web/'
env.aws_access_key  = ''
env.aws_secret_key  = ''
env.aws_bucket      = ''
env.databases		= ['database_name']
env.newrelic_key    = ''

# Fabric Variables (Standard-ish)

env.server_role     = ''
env.providers       = ['vagrant', 'digitalocean', 'linode', 'ec2']
env.server_roles    = ['www', 'database', 'resque', 'balancer']
env.user            = env.base_user
env.password        = env.base_password
env.git_server      = 'github.com'
env.project_dir     = '~/Projects/'
env.timezone        = 'UTC'
env.redis_host		= ''
env.redis_port		= ''
env.redis_password	= ''

