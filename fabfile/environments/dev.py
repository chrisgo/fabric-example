# Development

def config():
    return {
        'provider':         'digitalocean',
        'mount_root':       '/tmp/s3fs/',
        'www_root':         '/var/www/%s/web/',		# /var/www/%s/web/
        'branch':           'master',               # branch
        'environment':      'DEVELOPMENT',
        'server_names': {
            'www':              ['dev-www.domain.com'],
        },
        'roledefs': {
            'www':              ['dev-www1.domain.com'],
            'database':         ['dev-db1.domain.com'],
            #'database_master': [''],
            #'database_slave':  [''],
            #'database_backup': [''],
            'resque':           ['dev-resque1.domain.com'],
            #'cron':            [''],
            #'worker':          [''],
        },
        'enables': {
            'ssl':          False,
            's3fs':         False,
            'newrelic':     False,
            'papertrail':   False,
        },
    }