# generic conversion script
## 'old timbuctoo' to 'new timbuctoo'

The script harvest_all_generic.py' needs a config-file and a relations file.

The relations file:

contains for each domain the relations it has and to which other domain.

The configfile contains the name of the relations file.

Other entries in the config file:
- domains: indicates weather or not a domain has relations
- titles: indicates the fields in the domain which might contain a title; if all fail (or None), the `_id` is used.
- url: to download the data from the old timbuctoo
- relations: where to find the relations file
- file_ext: is added to the domain name to create a file name
- relations_tag: when relations in the imput are marked differently
- prefix: the prefix of the dataset

usage:
`python harvest_all_generic.py [-h] [-d DOWNLOAD] [-c CONFIG] [-t TEST]`

- `download`: True | False ; False is default which means: use previously downloaded files
- `config`: the name of the config file
- `test`: True | False ; True is default: download only the first 100 records of each domain (to save time and do a quick test)

