from distutils.core import setup

setup(name="esimport",
	version="0.1.5",
	description="Facilitates the indexing of content from a CSV into ElasticSearch",
	author="PlayNetwork, Inc.",
	author_email="industrial@playnetwork.com",
	url="https://github.com/playnetwork/esimport",
	packages=["esimport"],
	package_dir={"esimport" : "esimport"},
	license='MIT license, see LICENSE.txt',
	long_description=open('README').read(),
	include_package_data=True,
	install_requires=[
		"rawes"
	]
)