# Production

def config():
	return {
		'provider':			'digitalocean',
		'document_root':  	'/mnt/s3fs/',			# /mnt/s3fs/
		'www_root':       	'/var/www/%s/web/',		# /var/www/%s/web/
		'branch':           'master',               # branch
		'mount_s3fs':		True,
		'enable_ssl':		True,
		'server_names': {
			'www': 			['www.domain.com', 'domain.com'],
			'resque':		['resque.domain.com'],
		},
		'roledefs':	{
			'www': 	 		['www1.domain.com', ], # 'www2.domain.com'],
			'database': 	['db1.domain.com', 'db2.domain.com'],
			'resque':   	['resque1.domain.com'],
		},
	}
