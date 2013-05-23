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


## Prerequisites

- `pyes`


## Script Assumptions
- The key names are the first row of data.
- The index name is the filename minus extension.


## Use

### Adding data
- When adding data to ElasticSearch, you can optionally clear the existing
  ElasticSearch index before data is added by including the `-del` argument.

Process tab-delimited data and push the contents into the `song` index of the
ElasticSearch database located at server `-s` address 10.129.1.201:9200:

```
#!shell
python ssa.py -f '\\skynyrd\Export\Dev\data\Song.txt' -s '10.129.1.210:9200'
```

Process all files in a directory `-d` with the extensions `-ext` .txt and .tdf,
and push the data into the ElasticSearch database located at server `-s`
address 10.129.1.201:9200:

```
#!shell
python ssa.py -d '\\skynyrd\Export\Dev\data\Song.txt' -ext '.txt' '.tdf' -s '10.129.1.210:9200'
```

### Other commands

Get information on ALL indices `-i` on the ElasticSearch database located at
server `-s` 10.129.1.201:9200:

```
#!shell
python ssa.py -i -s '10.129.1.210:9200'
```

Further help available via the script:

```
#!shell
python ssa.py --help
```
