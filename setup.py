from setuptools import setup

setup(name="esimport",
	version="0.1.1",
	description="Facilitates the indexing of content from a CSV into ElasticSearch",
	author="PlayNetwork, Inc.",
	author_email="industrial@playnetwork.com",
	url="https://github.com/playnetwork/esimport.git",
	packages=["ssa"],
	package_dir={"esimport" : "esimport"},
	install_requires=[
		"rawes == 0.5.2"
	]
)