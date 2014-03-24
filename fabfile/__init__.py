from __future__ import with_statement
from fabric.api import *
from fabric.contrib.console import confirm
from fabric.contrib.files import *
import importlib
import paramiko
import os
import json
import datetime
import inspect
from environments import *
from project import *
from providers import *
from roles import *

"""
Usage:

fab <environment> <branch> release   # Release code
fab <environment> <role> <task>      # Builds servers

Examples:

fab dev master release               # standard release to dev
fav developer:chris master release   # standard release to chris (developer)

fab dev www server_normalize         # step 1 (normalize providers + basic)
fab dev www server_setup             # step 2 (server role specific)
fab dev www project_setup            # step 3 (project specific)
"""

# ========================================
#               Environments
# ========================================

@task 
def production():
    """
    ......... <environment> set up production environment
    """
    print("\n\n")
    print("************************************************")
    print("***** PRODUCTION (environments.production) *****")
    print("************************************************")
    import environments.production
    env.config = environments.production.config()
    roledefs = env.config.get("roledefs")
    for roledef in roledefs:
        print(roledef + " => " + ', '.join(roledefs[roledef]))
    print("\n")
    check = prompt("Updating PRODUCTION, please type project name:", "")
    if (check.upper() != env.git_project.upper()):
        print("\n")
        print("*******************************")
        print("***** FABRIC TASK ABORTED *****")
        print("*******************************\n\n")
        abort("")

@task
def staging():
    """
    ......... <environment> set up staging environment
    """
    print("***** STAGING (environments.staging) *****")
    import environments.staging
    env.config = environments.staging.config()

@task
def dev():
    """
    ......... <environment> set up dev environment
    """
    print("***** DEV (environments.dev) *****")
    import environments.dev
    env.config = environments.dev.config()

@task
def developer(user='chris'):
    """
    ......... <environment> set up developer environment
    """
    environment_name = "environments.developer_%s" % user
    print("***** DEVELOPER (%s) *****" % environment_name)
    _environment_object = __import__(environment_name, globals(), locals(), ['object'], -1)
    _config_method = getattr(_environment_object, 'config')
    env.config = _config_method()

# ========================================
#               Branches 
# ========================================

@task
def master():
    """
    ......... <branch> work on master branch
    """
    env.branch = 'master'
    env.roledefs = env.config.get('roledefs')
    env.hosts = env.roledefs['www']

@task
def branch(branch_name):
    """
    ......... <branch> work on any specified branch
    """
    env.branch = branch_name
    env.roledefs = env.config.get('roledefs')
    env.hosts = env.roledefs['www']

# ========================================
#                  Roles 
# ========================================

@task
def www():
    """
    ......... <role> www (web+app) role
    """   
    env.roledefs = env.config.get('roledefs')
    env.server_role = 'www'
    env.hosts = env.roledefs['www']
    env.branch = env.config.get('branch', 'master')

@task
def database():
    """
    ......... <role> database role
    """
    env.roledefs = env.config.get('roledefs')
    env.server_role = 'database'
    env.hosts = env.roledefs['database']

@task
def resque():
    """
    ......... <role> resque role
    """
    env.roledefs = env.config.get('roledefs')
    env.server_role = 'resque'
    env.hosts = env.roledefs['resque']


@task
def balancer():
    """
    ......... <role> balancer role
    """
    env.roledefs = env.config.get('roledefs')
    env.server_role = 'balancer'
    env.hosts = env.roledefs['balancer']

# ========================================
#                  Main
# ========================================

@task
def server_all():
    """
    ..... (1-2-3) Runs normalize, server_setup and project_setup
    """
    print('\n\n\n')
    print('==================================================')
    print('Running Full Server Setup')
    print('==================================================')
    print('\n\n\n')
    server_normalize()
    server_setup()
    project_setup()


@task
def server_normalize():
    """
    ..... (1) Initialize and normalize systems/providers
    """
    require('config', provided_by=[production, staging, dev, developer])
    require('hosts', provided_by=[www, database, resque, balancer])
    print("Normalize server ...")
    provider = env.config.get('provider')
    print("Loading normalize() from providers.%s" % provider)
    if not(provider in env.providers):
        abort("Provider: %s not found" % provider)
    else:
        # dynamically load function 
        getattr(getattr(providers, provider), "normalize")()
    # Then run base server setup
    roles.server_normalize()

@task
def server_setup():
    """
    ..... (2) Setup basic server software by role
    """
    require('config', provided_by=[production, staging, dev, developer])
    require('hosts', provided_by=[www, database, resque, balancer])
    print("Server Setup ...")
    # Call www.server_build()
    if not(env.server_role in env.server_roles):
        abort("Server Role: %s not found" % env.server_role)
    else:
        print("Loading server_setup() from servers.%s ..." % env.server_role)
        getattr(getattr(roles, env.server_role), "server_setup")()

@task
def project_setup():
    """
    ..... (3) Setup project-specific installs by role
    """
    require('config', provided_by=[production, staging, dev, developer])
    require('hosts', provided_by=[www, database, resque, balancer])
    print("Project Setup ...")
    # Call www.server_build()
    if not(env.server_role in env.server_roles):
        abort("Server Role: %s not found" % env.server_role)
    else:
        print("Loading project_setup() from servers.%s ..." % env.server_role)
        getattr(getattr(roles, env.server_role), "project_setup")()

@task
def release():
    """
    Release code to an environment
    """
    require('config', provided_by=[production, staging, dev, developer])
    require('hosts', provided_by=[www, database, resque, balancer])
    require('branch', provided_by=[master, branch])
    # Get www_root
    www_root = env.config.get('www_root')
    if ('%s' in www_root):
        www_root = www_root % env.git_project.lower()
    # Deploy build
    print("Deploy Build ...")
    with cd("%s%s" % (env.project_dir.lower(), env.git_project.lower())):
        run('git checkout %s' % env.branch)
        run('git reset --hard HEAD')
        run('git clean -f -d')
        run('git pull')
        # Rsync code
        print('Performing rsync to %s' % www_root)
        source = '%s%s/%s' % (env.project_dir.lower(), env.git_project.lower(), env.app_root)
        target = www_root
        run("rsync -oavz --delete \
                         --exclude 'application/log*' \
                         --exclude 'application/cache*' \
                         %s %s" % 
                         (source, target))
    # Update build date
    build_date = datetime.datetime.now().strftime("%m/%d/%y %I:%M %p %Z")
    print("Updating build date to %s" % build_date)
    sed('%s/web/application/config/app.php' % os.path.dirname(www_root.rstrip('/')), 
        '\{\{BUILD.DATE\}\}',
        build_date)

