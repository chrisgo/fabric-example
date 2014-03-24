from __future__ import with_statement
from fabric.api import *
from fabric.contrib.console import confirm
from fabric.contrib.files import *

"""
This file contains project-specific general settings 
Environment-specific settings go into the environments folder
"""

# Fabric Variables (Project)

env.base_user       = "chris"
env.base_password   = "password"
env.git_project     = "Project"
env.app_root        = 'src/php/web/'
env.databases       = ['project']
env.newrelic_key    = ''
env.papertrail_key	= ''
env.aws_buckets     = [{
                        'name': "s3fs.domain.com", 
                        'mount': "s3fs", 
                        'access_key': "", 
                        'secret_key': ""
                       }]
env.app_dirs		= ['s3fs/files/', 
					   's3fs/documents/', 
					   's3fs/database',
					  ]

# Fabric Variables (Standard-ish)
env.server_role     = ''
env.providers       = ['vagrant', 'digitalocean', 'linode', 'ec2']
env.server_roles    = ['www', 'database', 'resque', 'balancer']
env.user            = env.base_user
env.password        = env.base_password
env.git_server      = 'git.domain.com'
env.project_dir     = '~/Projects/'
env.timezone        = 'UTC'
env.redis_host		= ''
env.redis_port		= ''
env.redis_password	= ''

