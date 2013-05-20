# Search Synchronization Agent

Tool exists to synchronize 4d database content from Conductor with a search engine (ElasticSearch) for Global Conductor and Innovation projects to leverage for discovery of media.

## Running Locally

Create a folder for your Virtual environments on your machine (see example below):

```
#!shell
mkdir -p ~/Virtualenvs
cd ~/Virtualenvs
```

Create and activate a virtual environment for this project:

```
#!shell
virtualenv search-sync-agent
source search-sync-agent/bin/activate
```

Now clone this repo into your projects folder:

```
#!shell
mkdir -p ~/Projects
cd ~/Projects
git clone git@bitbucket.org:playnetwork/search-sync-agent.git
cd search-sync-agent
```

