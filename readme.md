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
All dependencies are noted in setup.py and can be installed via the following command after git clone:

```
#!shell
python setup.py develop
```

## Script Assumptions
- The key names are the first row of data in the TDF file.
- The index name is the filename minus extension.
- By default, the mapping filename is the index name plus the **.map** extension
  (may be overridden by the user with the `-map_ext` argument)

## Use
If login credentials are required for any operation, add the arguments
`-user 'username'` and `-pass 'password'`.

### Adding data
- When adding data to ElasticSearch, you can optionally clear the existing
  ElasticSearch index before data is added by including the `-del` argument.

Process tab-delimited data and push the contents into the `song` index of the
ElasticSearch database located at server `-s` address **10.129.1.201:9200**:

```
#!shell
python -m ssa -f '\\skynyrd\Export\Dev\data\Song.txt' -s '10.129.1.210:9200'
```

Process each file in a directory `-d` with the extension `-tdf_ext` **.txt**
or **.tdf**, use the file with the extension `-map_ext` **.map** as the map
for that index, use the file with the extension `-fn_ext` **.keys** to rename
the fields, and push the data into the ElasticSearch database located at
server `-s` address **10.129.1.201:9200**:

```
#!shell
python -m ssa -d '\\skynyrd\Export\Dev\data\' -tdf_ext '.txt' '.tdf' -map_ext '.map' -fn_ext '.keys' -s '10.129.1.210:9200'
```

### Other commands

Get information on ALL indices `-indices` on the ElasticSearch database located at
server `-s` **10.129.1.201:9200**:

```
#!shell
python -m ssa -indices -s '10.129.1.210:9200'
```

Further help available via the script:

```
#!shell
python -m ssa --help
```


## Resources
- Python libraries
  - `Requests`: [documentation][requests-lib] | [quickstart][requests-docs]
  - `PyES`: [Github][pyes-lib] | [documentation][pyes-docs]
- 4D
  - `EXPORT DATA`: [command reference][4D-EXPORT-DATA-docs]


[pyes-lib]: https://github.com/aparo/pyes
[pyes-docs]: http://pyes.readthedocs.org/en/latest/index.html
[requests-lib]: http://docs.python-requests.org/en/latest/index.html
[requests-docs]: http://docs.python-requests.org/en/latest/user/quickstart/
[4D-EXPORT-DATA-docs]: http://doc.4d.com/4D-Language-Reference-11.6/Import-and-Export/EXPORT-DATA.301-206065.en.html
