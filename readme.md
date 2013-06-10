# ElasticSearch Importy (esimport)

Tool exists to index content from a CSV in ElasticSearch.

## Prerequisites

All dependencies are noted in setup.py and can be installed via the following command after git clone:

```Bash
python setup.py develop
```

## Use
To index the contents of a CSV file (where the first row contains field names) into an ElasticSearch server, you must supply the -s, -f, -i and -t arguments. If the specified index or type does not exist within the specified ElasticSearch server, it will be created when the module executes. The following example will index data from data.file into ElasticSearch at http://myserver:9200/myindex/mytype:

```Bash
python -m esimport -s myserver:9200 -f /path/to/import/data.file -i myindex -t mytype
```

* -s _server_ (may either be a hostname:port or fully qualified, i.e. https://servername:port)
* -f _filepath_ (location of tab-delimited file to import data from)
* -i _index_name_ (name of the target index within ElasticSearch)
* -t _type_name_ (name of the target document type within ElasticSearch)

Further help available via the script:

```Bash
python -m esimport --help
```

### Additional Options

#### Clear Existing Data First

When indexing data in ElasticSearch, you may optionally clear the existing ElasticSearch type before data is added by including the -rm argument.

```Bash
python -m esimport -s myserver:9200 -f /path/to/import/data.file -i myindex -t mytype -rm
```

* -rm (removes all documents of given type within the specified index on ElasticSearch)

#### Mapping

Mapping is the definitiion of the field names and value types of a document indexed within ElasticSearch.  Characteristics such as field type, whether a field is searchable, and whether to include a timestamp may all be defined in a map.

*Please note:* If the specified mapping does not match the field names in the tab-delimited file, you should supply a field translation file (described below).

A mapping file can be specified by adding the -m parameter to the command:

```Bash
python -m esimport -s myserver:9200 -f /path/to/import/data.file -i myindex -t mytype -m /path/to/mapping.json
```

* -m _mapping_filepath_ (location of JSON formatted mapping file for specified type)

Maps should be provided in JSON format, as seen below and on the ElasticSearch website.

##### Sample mapping for a document type "tracks"

```JSON
{
	"tracks" : {
		"properties" : {
			"genre" : {
				"type" : "string"
		  	},
			"album" : {
				"type" : "string"
			},
			"ISRC" : {
				"type" : "string"
			},
			"recordCompany" : {
				"type" : "string"
			},
			"artist" : {
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

#### Field Translations

If the original field names from the CSV file need to be altered or filtered during the import, you may provide a field translations file.  The first row of this file should consist of the original field names, separated by the specified delimiter; the second, the new names, again separated by the specified delimeter.

*Please note:* Any original field names omitted from the first row, will be omitted from the indexed data as well. This is a handy way to filter the columns at time of indexing if that is necessary.

```Bash
python -m esimport -s myserver:9200 -f /path/to/import/data.file -i myindex -t mytype -rm -m /path/to/mapping.json -n /path/to/field/name/translations.file
```

* -n _field_translation_filepath_ (location of CSV field translation file for specified type)

##### Sample Field Name Translations File

```
Album_Category,Album_ID,ISRC,Record_Co,Song_Artist,Song_ID,Song_Secs,Song_Title
genre,albumID,ISRC,recordCompany,artist,songID,duration,title
```

#### Basic Auth

If login credentials are required, add the arguments -user and -pass

```Bash
python -m esimport -s https://myserver.com -f /path/to/import/data.file -i myindex -t mytype -user exampleuser -pass examplepassword
```

## Developing Locally

Create a folder for your Virtual environments on your machine (see example below):

```Bash
mkdir -p ~/Virtualenvs
cd ~/Virtualenvs
```

Create and activate a virtual environment for this project:

```Bash
virtualenv esimport
source esimport/bin/activate
```

Now clone this repo into your projects folder:

```Bash
mkdir -p ~/Projects
cd ~/Projects
git clone git@bitbucket.org:playnetwork/esimport.git
cd esimport
```

## Dependencies

* Python libraries
	* `rawes`: [Github][rawes-lib] | [documentation][rawes-docs]
* ElasticSearch

[rawes-lib]: https://github.com/humangeo/rawes
[rawes-docs]: https://github.com/humangeo/rawes#rawes
[ES-mapping-doc]: http://www.elasticsearch.org/guide/reference/mapping/