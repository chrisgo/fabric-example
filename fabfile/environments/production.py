# Production

def config():
	return {
		'provider':			'digitalocean',
		'mount_root':  	    '/mnt/',			# /mnt/
		'www_root':       	'/var/www/%s/web/',	# /var/www/%s/web/
		'branch':           'master',           # branch
        'environment':      'PRODUCTION',
        'server_names': {
			'www': 				['www.domain.com', 'domain.com'],
			'resque':			['resque.domain.com'],
		},
		'roledefs':	{
			'www': 	 			['www1.domain.com', 'www2.domain.com', 'www3.domain.com'],
			'database': 		['db1.domain.com', 'db2.domain.com'],
            #'database_master': [''],
            #'database_slave':  [''],
            #'database_backup': [''],
			'resque':   		['resque1.domain.com', 'resque2.domain.com'],
            #'cron':            [''],
            #'worker':          [''],
		},
		'enables': {
            'ssl':          True,
            's3fs':         True,
            'newrelic':     True,
            'papertrail':   True,
        },
	}
