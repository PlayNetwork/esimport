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


## Data Support Files
If bulk-importing all data in a directory, you will need to use the
`index_name.ext` naming convention.
    
For example:

- `Song.txt`: data file (tab-delimited)
- `Song.map`: map file (JSON)
- `Song.keys`: field name translations file (tab-delimited)

### Map File
Mapping is the process of defining the characteristics of a document so
ElasticSearch can treat the data appropriately.  Characteristics such as field
type, whether a field is searchable, and whether to include a timestamp may all
be defined in a map.

An ElasticSearch index may contain documents of different **mapping types**.  At
present, search-sync-agent assumes that all documents' type name is the index
name and adds them as that type.

ElasticSearch *can* make basic inferences about a document type based on the
documents that are added, so explicit mapping is not required.  However,
providing a map for each type in an index is **highly recommended** when using
search-sync-agent because the data is obtained from text files.  If a map is not
provided, every field will be stored as a string.

Maps should be provided in JSON format, as seen below and on the ElasticSearch website.

#### Sample mapping for a document type "song"
```
{
  "song" : {
    "properties" : {
      "genre" : {
        "type" : "string"
      },
      "albumToken" : {
        "type" : "integer"
      },
      "titleDisplay" : {
        "type" : "string"
      },
      "ISRC" : {
        "type" : "string"
      },
      "recordCompany" : {
        "type" : "string"
      },
      "artistAlpha" : {
        "type" : "string"
      },
      "artistPrint" : {
        "type" : "string"
      },
      "songToken" : {
        "type" : "integer"
      },
      "durationInSeconds" : {
        "type" : "integer"
      },
      "title" : {
        "type" : "string"
      }
    }
  }
}
```

More details on mapping may be found in [ElasticSearch's mapping reference][ES-mapping-doc].


### Field Translations File
If you do not want to use the original field names from Conductor, you will need
to provide a field translations file.  The first row of this file should consist
of the original field names, separated by tabs; the second, the new names, again
separated by tabs.

#### Sample song field translations file
```
Alb_Category	Album_ID	ISRC	Record_Co	SongArtPrint	Song_ID_pk	Song_Secs	Song_Title
genre	albumToken	ISRC	recordCompany	artistPrint	songToken	durationInSeconds	title
```


## Resources
- Python libraries
  - `Requests`: [documentation][requests-lib] | [quickstart][requests-docs]
  - `PyES`: [Github][pyes-lib] | [documentation][pyes-docs]
- 4D
  - `EXPORT DATA`: [command reference][4D-EXPORT-DATA-docs]
- ElasticSearch
  - [Windows installers][ES-windows-installers]: What's special about this is
    that it already has ES packaged up to run as a service.  The official ES
    website provides instructions on how to run ES as a service, but it requires
    a separate download and extra setup time.  This is a nice timesaver.
  - Mapping: [reference][ES-mapping-doc]


[pyes-lib]: https://github.com/aparo/pyes
[pyes-docs]: http://pyes.readthedocs.org/en/latest/index.html
[requests-lib]: http://docs.python-requests.org/en/latest/index.html
[requests-docs]: http://docs.python-requests.org/en/latest/user/quickstart/
[4D-EXPORT-DATA-docs]: http://doc.4d.com/4D-Language-Reference-11.6/Import-and-Export/EXPORT-DATA.301-206065.en.html
[ES-mapping-doc]: http://www.elasticsearch.org/guide/reference/mapping/
[ES-windows-installers]: https://github.com/rgl/elasticsearch-setup