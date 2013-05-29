from setuptools import setup

setup(name='search-sync-agent',
	version='0.1.0',
	description='Synchronizes 4d database content from Conductor with a ElasticSearch',
	author='PlayNetwork, Inc.',
	author_email='industrial@playnetwork.com',
	url='https://bitbucket.org/playnetwork/search-sync-agent',
	packages=['ssa'],
	package_dir={'ssa': 'ssa'},
	install_requires=[
	"pyes == 0.20.0",
	"requests == 1.2.3"
	]
)