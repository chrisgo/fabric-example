# Developer: Chris

def config():
    return {
        'provider':         'vagrant',
        'document_root':    '/tmp/s3fs/',	    # /mnt/s3fs/
        'www_root':         '/var/www/%s/web/',     # /var/www/%s/web/
        'branch':           'master',               # branch
        'mount_s3fs':		False,
        'enable_ssl':		False,
        'roledefs':	{
            'www':	  ['chris-dev-www.domain.com'],
            'resque': ['chris-dev-resque.domain.com'],
        },
    }
