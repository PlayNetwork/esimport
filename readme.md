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
  ElasticSearch index before data is added by including the `-rmi` argument.
- Likewise, everything of a certain type under the index can be removed by
  including the `-rmi` argument.

Process tab-delimited data and push the contents into the 'conductor' index
`-i` of the ElasticSearch database located at server `-s` address
**10.129.1.201:9200**:

```
#!shell
python -m ssa file -f '\\skynyrd\Export\Dev\data\Song.txt' -i 'conductor' -s '10.129.1.210:9200'
```

Process each file in a directory `-d` with the extension `-tdf_ext` **.txt**
or **.tdf**, use the file with the extension `-map_ext` **.map** as the map
for that index, use the file with the extension `-fn_ext` **.keys** to rename
the fields, and push the data into the 'conductor' index `-i` of the
ElasticSearch database located at server `-s` address **10.129.1.201:9200**:

```
#!shell
python -m ssa dirs -d '\\skynyrd\Export\Dev\data\' -tdf_ext '.txt' '.tdf' -map_ext '.map' -fn_ext '.keys' -i 'conductor' -s '10.129.1.210:9200'
```

### Other commands

Get information on ALL indices on the ElasticSearch database located at
server `-s` **10.129.1.201:9200**:

```
#!shell
python -m ssa indices -s '10.129.1.210:9200'
```

Further help available via the script:

```
#!shell
python -m ssa --help
```


## Removing Old Data

To remove old data (for example, an outdated 'song' index), use:

```
#!shell
curl -XDELETE 'http://localhost:9200/song'
```

If you want to remove a particular type in an index - for example, all documents
of type 'timezones' in the 'conductor' index - use:

```
#!shell
curl -XDELETE 'http://localhost:9200/conductor/timezones'
```


## Data Support Files

### Bulk Imports
If you wish to use index names other than the default (file name minus
extension) while bulk-importing.  To do this, add the `-tp` argument followed
by the path to a TDF file.  The first row of this file should consist of the
original data set names *in lowercase* and separated by tabs; the second,
the new names, again separated by tabs.

If bulk-importing all data in a directory, you will also need to use the
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


## Conductor Data Export

To run the data export, you will first need to create some export project template files.

1. Log into Conductor as a Design user.  (See Jesse or Allison.)
2. Change to Design mode.  (Hold down Alt+Shift and right-click anywhere in the
   4D window.  From the popup menu, select "Go to Design mode".)
3. From the File menu, select Export > Data to File...
4. Choose a table from the "Export from Table" dropdown and double-click on each
   of your fields of interest listed to add them to your export project template.
5. On the File tab, ensure the format selected is "Text" and "Windows File", and
   select "Export Selection" (NOT "Export all Records", so the template doesn't
   have to be changed when we start exporting updates instead of all records).
6. On the Header tab, check the "Column header" box.
7. On the Delimiters tab, select "Tab" from the "end of Field" dropdown.
8. Use the "Save Settings" button to export the template as a .4SI file.
  - **Important**: You MUST name the template file to match the name of the Conductor table!
    For example, `Record_Co.4SI`.
  - **Important**: You MUST save the template files in the
    `\\Skynyrd\Export\[Dev|Staging|Conductor]\projects\` folder!

The data export method may be called by:

- a recurring task (recurrence TBD, if any) set up within Conductor's internal
  Task Manager
- a SOAP call to `ws_ExportData` (input: path to the desired data export
  location, or an empty string if the default location is acceptable)


### WDSL Locations

- Dev: [http://soap_dev:8080/4dwsdl/](http://soap_dev:8080/4DWSDL/)
- Staging: [http://supremes:8080/4DWSDL/](http://supremes:8080/4DWSDL/) (data
  export method NOT yet available)
- Production: [http://young:8080/4DWSDL/](http://young:8080/4DWSDL/) (data
  export method NOT yet available; will be deployed with Conductor 8.10 release)


### Data Export Method: `store_task_ExportDataSearchSync`

May be called as a task by Conductor or by `ws_ExportData` via web service call.
Unless otherwise specified, data will be exported to the
`\\Skynyrd\Export\[Dev|Staging|Conductor]\data\` folder.

```
  ` ----------------------------------------------------
  ` User name (OS): awintrip
  ` Date and time: 5/7/13, 16:31:26
  ` ----------------------------------------------------
  ` Method: store_task_ExportDataSearchSync
  ` Description
  ` 
  ` Project filename format (do not include brackets):
  `     [TableName].4SI
  `
  ` Data output filename format (do not include brackets):
  `     [TableName].txt
  `
  ` 1.  Get the (environment-dependent) paths of the folders that
  `     will house the export instructions and export data.
  ` 2.  Verify the folders exist; if not, create 'em.
  ` 3.  Get the list of files in the export instructions folder.
  ` 4.  Filter out any file that doesn't end in .4SI.
  ` 5.  Loop through files and run each data export.
  `
  `
  ` Parameters
  ` $1: string.  Where we want to place the data export file(s).
  ` $0: boolean.  The return value.  Represents "task is done".  Since
  `     this is a scheduled task, $0 always needs to return False so
  `     Task Manager marks it as "need to run this task again later".
  `
  ` Possible TODO later items:
  ` ==========================
  ` - Write an error output file instead of no output file if the
  `   supplied table name (derived from project filename) was
  `   invalid.  Don't want to have to check 4D for errors.
  `
  ` - Add timestamp and write a new file for each run instead of
  `   replacing the original.
  `
  `
  ` Copyright 2013 Play Network  Inc.
  ` ----------------------------------------------------

C_TEXT($tExportBasepath;$tProjectFolderPath;$tDataFolderPath)
C_BOOLEAN($bUseDefaultExportPath)
$bUseDefaultExportPath:=False

If (Count parameters=0)
	$bUseDefaultExportPath:=True
Else 
	If ($1#"")
		$bUseDefaultExportPath:=True
	End if 
End if 

$tExportBasepath:=pref_GetPreferenceValue ("Data Export Project Template Files")

If (Test path name($tExportBasepath)#Is a directory )
	CREATE FOLDER($tExportBasepath)
End if 

  ` now add in env-specific folder...
$tExportBasepath:=$tExportBasepath+pref_GetPreferenceValue ("Environment")+"\\"
If (Test path name($tExportBasepath)#Is a directory )
	CREATE FOLDER($tExportBasepath)
End if 

$tProjectFolderPath:=$tExportBasepath+"projects\\"
If (Test path name($tProjectFolderPath)#Is a directory )
	CREATE FOLDER($tProjectFolderPath)
End if 

If ($bUseDefaultExportPath)
	$tDataFolderPath:=$tExportBasepath+"data\\"
Else 
	$tDataFolderPath:=$1
End if 

If (Test path name($tDataFolderPath)#Is a directory )
	CREATE FOLDER($tDataFolderPath)
End if 

  ` get the list of files in the specified folder
ARRAY TEXT($atDocNames;0)
DOCUMENT LIST($tProjectFolderPath;$atDocNames)

C_TEXT($tProjExtensionExpected)
$tProjExtensionExpected:=".4SI"

<>gMsg:="Exporting data..."
alert_DisplayProgressMsg (<>gMsg)

  ` Loop through files and run each data export
C_LONGINT($i)
For ($i;1;Size of array($atDocNames))
	C_TEXT($tFilename)
	$tFilename:=$atDocNames{$i}
	
	  ` get the last n chars of the filename, where n is the length of the
	  ` expected extension; +1 because 4D starts index at 1
	$tProjExtensionActual:=Substring($tFilename;Length($tFilename)-Length($tProjExtensionExpected)+1)
	
	  ` only attempt to process it if the extension is what we expect
	If ($tProjExtensionActual=$tProjExtensionExpected)
		C_TEXT($tTableName)  ` remove extension from filename to get table name
		$tTableName:=Substring($tFilename;1;Length($tFilename)-Length($tProjExtensionExpected))
		
		C_POINTER($pTable)
		
		  ` because sh_GetTablePtrFromTableName doesn't have any error handling,
		  ` and it's silly to let this task break over a typo
		ON ERR CALL("err_GeneralErrorHandler")
		$pTable:=sh_GetTablePtrFromTableName ($tTableName)
		ON ERR CALL("")
		
		  ` if we have a valid pointer to a table (i.e. pointer is not null/"nil"), run the export
		If (Not(Nil($pTable)))
			<>gMsg:="Exporting data from the "+$tTableName+" table for report "+$tFilename+"..."
			
			  ` ensure we're in read-only state within this process; that
			  ` MIGHT squeeze a bit more performance out of this.
			C_BOOLEAN($bIsAlreadyReadOnly)
			$bIsAlreadyReadOnly:=Read only state($pTable->)
			If (Not($bIsAlreadyReadOnly))
				READ ONLY($pTable->)
			End if 
			
			ALL RECORDS($pTable->)
			
			C_TEXT($tProjectFullPath)
			$tProjectFullPath:=$tProjectFolderPath+$tFilename
			
			C_BLOB($exportParams)  ` Beware of The BLOB, it creeps, and leaps...
			DOCUMENT TO BLOB($tProjectFullPath;$exportParams)
			
			C_TEXT($tDataFilename;$tDataFileFullPath)
			$tDataFilename:=$tTableName+".txt"
			$tDataFileFullPath:=$tDataFolderPath+$tDataFilename
			
			EXPORT DATA($tDataFileFullPath;$exportParams)
			
			  ` if the table wasn't in read-only state within this process
			  ` when we started, set it back to read/write
			If (Not($bIsAlreadyReadOnly))
				READ WRITE($pTable->)
			End if 
			
		Else 
			  ` TODO: Might want to add some code here later to write an error
			  ` doc; don't want to have to check 4D for errors.  Not required
			  ` right now though.
			  ` akw 05/13/2013
		End if 
	End if 
End for 

<>gMsg:=""

$0:=False  `this is a scheduled task, so $0=done.  It should always return done:=false
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