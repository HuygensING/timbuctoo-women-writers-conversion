# Women writers conversion

`usage: harvest_all.py [-h] [-d DOWNLOAD] [-f FILES] [-t TEST]`

`-d True` means: download the data from the current site and save it as files.

`-f' actually does not ask for filenames, but for a suffix to be used. Example:
`harvest_all.py -d True -f today`
will save files with extension `_today`.

For each file type a file will be filled:
- ww_languages_today.json
- ww_kewords_today.json
- ww_locations_today.json
- ww_collectives_today.json
- ww_persons_today.json
- ww_documents_today.json

If you omit de `-d` parameter the script will look for files with the `-f` extension. If `-f` is not given, it will use todays date, for exmple: `_20191206` (yyyymmdd).

In the second part the script converts the json files to rdf-xml files. These files can than be uploaded to timbuctoo.

Downloading the files takes about 15 minutes; converting takes about 10 seconds.

Uploading of the first four files mentioned about is fast, they are small. Persons and documents take more time, several minutes.

## read_metadata

With the read_metadata script the relations are extracted from the metadata.

You get the metadata from: `http://myrepository.org/v2.1/system/vres/MyDataset/metadata`; save as json.

The output of the script is also json.
