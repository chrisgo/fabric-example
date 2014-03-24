from __future__ import with_statement
from fabric.api import *
from fabric.contrib.console import confirm
from fabric.contrib.files import *

__all__ = ['digitalocean','ec2','linode','vagrant']

