# Developer: Chris

def config():
    return {
        'provider':         'vagrant',
        'mount_root':       '/tmp/s3fs/',	      # /mnt/s3fs/
        'www_root':         '/var/www/%s/web/',   # /var/www/%s/web/
        'branch':           'master',             # branch
        'environment':      'DEVELOPMENT',
        'roledefs':	{
            'www':	           ['chris-dev-www.domain.com'],
            'database':        ['chris-dev-db.domain.com'],
            #'database_master': [''],
            #'database_slave':  [''],
            #'database_backup': [''],
            'resque':          ['chris-dev-resque.domain.com'],
            #'cron':           [''],
            #'worker':         [''],
        },
        'enables': {
            'ssl':          False,
            's3fs':         False,
            'newrelic':     False,
            'papertrail':   False,
        },
    }



