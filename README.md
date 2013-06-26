Fabric Example
====

Example of how you can organize a set of fabric scripts.  Mostly this is just how I organized my fabric build and release process and sharing to possibly help other folks get started.

* Fabric: http://fabfile.org
* Fabtools: https://github.com/ronnix/fabtools
* S3FS: https://code.google.com/p/s3fs/
* Boto: https://github.com/boto/boto (didn't get to AWS yet)

Mostly I deal with a standard LEMP stack (Linux, Nginx, MySQL and PHP-fpm) on Debian so please adapt for your own use.  The original goal was to deal with Vagrant and Linode or Amazon AWS but I ended up just implementing Vagrant and DigitalOcean as "deployment targets".

---

These scripts should be run in the directory where the fabfile directory lives.  *If you do an ls, you should see the directory called "fabfile"*

### Goals

1. Build servers quickly based on:

    * Environments => developer, dev, qa, stage, production
    * Roles        => www, database, resque, balance

1. Normalize all the different cloud providers

    * Providers    => digitalocean, ec2, linode, vagrant

1. Be able to customize each project while sharing core fabric files

    * Core: __init__.py, roles/, lib/ and providers/ folders
    * Per project: environments/ folder

### Usage

    fab <environment> <branch> release   # Release code
    fab <environment> <role> <task>      # Builds servers

    Examples:

    fab dev master release               # standard release to dev
    fav developer:chris master release   # standard release to chris (developer)

    fab dev www server_normalize         # step 1 (normalize providers + basic)
    fab dev www server_setup             # step 2 (server role specific)
    fab dev www project_setup            # step 3 (project specific)

### New Projects

1. Check environments/__init__.py to make sure all project-specific settings are correct
1. Check environments/*.py to make sure all the servers are correct

### New Hosts (Servers)

For new servers (new file environments), we need to do some setup:

1. Create the appropriate settings for the system, usually this is for a new developer
   or a new server starting from scratch

    * Make sure to note down the provider (Vagrant, Linode, etc.)
    * Make sure this <environment> is unique across everything ever created for this project
    * The fabric system will pick up the settings for that environment

1. Run through steps 1-3

    1. fab <environment> <role> server_normalize
        * Normalizes each provider (Vagrant, Linode, etc)
        * Installs basic setup for ALL servers
    1. fab <environment> <role> server_setup
        * Installs more software by server role
    1. fab <environment> <role> project_setup
        * Installs project-specific software by server role
        * Also initializes the project on the server by server role

For normal releases to an environment (for example: dev), run

    fab dev master release

and for PRODUCTION, run it with a group argument

    fab production master release

### TODO

* Move build date tokenization out of init
* Break release() to 2 parts: Core __init__.py and execute project-specific stuff in environments/__init__.py


