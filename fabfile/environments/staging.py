# Staging 

def config():
	return {
		'provider':			'digitalocean',
		'document_root':  	'/tmp/s3fs/',			# /mnt/s3fs/
		'www_root':       	'/var/www/%s/web/',		# /var/www/%s/web/
        'branch':           'master',               # branch
		'mount_s3fs':		False,
		'enable_ssl':		False,
		'roledefs':	{
			'www': 	 	['staging-www.domain.com'],
		}
}