# Development

def config():
    return {
        'provider':         'digitalocean',
        'document_root':    '/tmp/s3fs/',
        'www_root':         '/var/www/%s/web/',		# /var/www/%s/web/
        'branch':           'master',               # branch
        'mount_s3fs':		False,
        'enable_ssl':		False,
        'server_names': {
            'www':          ['dev-www.domain.com'],
        },
        'roledefs': {
            'www': 	        ['dev-www1.domain.com'],
        }
    }
