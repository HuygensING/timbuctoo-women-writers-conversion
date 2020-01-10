# -*- coding: utf-8 -*-
import argparse
from datetime import datetime
from datetime import date
import html
import json
import locale
locale.setlocale(locale.LC_ALL, 'nl_NL') 
import re
import sys
import unicodedata
import urllib.parse


def arguments():
    ap = argparse.ArgumentParser()
    ap.add_argument('-i', '--inputfile',
                    help="inputfile",
                    default="./ww_metadata.json"
                    )
                
    ap.add_argument("-o", "--outputfile", help="outputfile",
                        default="./ww_query_result_first.xml")
    ap.add_argument("-t", "--addtitle", help="voeg <schema:title> toe (indien True); default: False",
                        default=False)
    args = vars(ap.parse_args())
    return args


def stderr(text):
    sys.stderr.write("{}\n".format(text))

def start():
    stderr("started at: {}".format(datetime.today().strftime("%H:%M:%S")))

def stop():
    stderr("stopped at: {}".format(datetime.today().strftime("%H:%M:%S")))
 

if __name__ == "__main__":
    start()
    args = arguments()
    inputfile = args['inputfile']
    outputfile = args['outputfile']
    metadata = json.load(open(inputfile, encoding='utf-8', errors="surrogateescape"))
#    stderr(json.dumps(metadata, sort_keys=False, indent=2))
    result = {}
    for key in metadata.keys():
        stderr(key)
        result[key] = {}
        for item in metadata[key]:
            if item['type']=='relation' and item['name'] == item['relation']['outName']:
#                stderr(" {}: {}".format(item['relation']['outName'], item['relation']['targetCollection']))
                result[key][item['relation']['outName']] = item['relation']['targetCollection']
    for key in result.keys():
        stderr(key)
        for item in result[key].keys():
            stderr(" {}: {}".format(item, result[key][item]))
    with open(outputfile, "w", encoding='utf-8') as uitvoer:
        uitvoer.write(json.dumps(result, sort_keys=False, indent=2))
    stop()

