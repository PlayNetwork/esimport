from distutils.core import setup

setup(name='search-sync-agent',
	version='0.1.0',
	description='Synchronizes 4d database content from Conductor with a ElasticSearch',
	author='PlayNetwork, Inc.',
	author_email='industrial@playnetwork.com',
	url='https://bitbucket.org/playnetwork/search-sync-agent',
	packages=['search-sync-agent'],
	package_dir={'search-sync-agent': 'src/search-sync-agent'}
	)
