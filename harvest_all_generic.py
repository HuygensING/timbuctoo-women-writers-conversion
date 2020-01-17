# -*- coding: utf-8 -*-
import argparse
from datetime import datetime
from datetime import date
import html
import json
from pnv_person import PnvPerson
import re
import requests
import sys
import unicodedata
from urllib.parse import quote, unquote


start_time = datetime.now()
properties = { "forename" : "givenName", "name_link" : "surnamePrefix", "surname" : "baseSurname", "add_name" : "trailingPatronym", "role_name" : "prefix", "gen_name" : "givenNameSuffix" }


def find_property(value):
    result = properties[value.lower()]
    if result:
        return result
    return value


def do_components(elems, indent, uitvoer):
    name = PnvPerson()
    for elem in elems:
        type = find_property(elem['type'])
        value = elem['value']
        name.add(type,value)
        uitvoer.write("      <pnv:{0}>{1}</pnv:{0}>\n".format(type, escape(value)))
    uitvoer.write("      <schema:name>{}</schema:name>\n".format(escape(name.get('literalName'))))


def do_names(names_list, uitvoer, prefix):
    for name in names_list:
        uitvoer.write(f'    <{prefix}:nameComponents rdf:parseType="Resource">\n')
        do_components(name['components'], 1, uitvoer)
        uitvoer.write(f'    </{prefix}:nameComponents>\n')

def do_links(link_list, uitvoer, prefix):
    link_str = '''    <{prefix}:link>
      <rdf:Description rdf:about="{url}">
        <schema:label>{label}</schema:label>
        <schema:url rdf:resource="{url}"/>
      </rdf:Description>
    </{prefix}:link>
'''
    for link in link_list:
        url = link['url']
        label = link['label']
        if re.search(': http', url):
            res = re.split(': ', url)
            label = '{} ({})'.format(label, res[0])
            url = res[1]
        url = unquote(url)
        url = quote(url, safe='/:?=+,')
        uitvoer.write(link_str.format(url=url, label=escape(label), prefix=prefix))


def do_header(uitvoer, prefix):
    header = f'''<?xml version="1.0"?>
<rdf:RDF
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:xsd="http://www.w3.org/2001/XMLSchema#"
    xmlns:schema="http://schema.org/"
    xmlns:{prefix}="https://resource.huygens.knaw.nl/{prefix}/"
    xmlns:dcterms="http://purl.org/dc/terms/modified"
    xmlns:pnv="http://www.purl.org/pnv/"
    xmlns:skos="http://www.w3.org/2004/02/skos/core#">
'''
    uitvoer.write(header)


def do_footer(uitvoer):
    uitvoer.write("\n</rdf:RDF>\n")


def do_start_record(uitvoer, domain, id, prefix):
    uitvoer.write(f'\n  <{prefix}:{domain} rdf:about="https://resource.huygens.knaw.nl/{prefix}/{domain}/{id}">\n')


def indent(num=4):
    return num * " "


def escape(txt):
    txt = txt.replace("\n","\\n")
    txt = html.escape(txt)
    return txt

def scrape_line(uitvoer, item, prefix, ind=4, parent=""):
    schema_title = ""
    for key,elem in item.items():
        if key=='@relations':
            # we do these elsewhere
            return
        if key=='@type':
            key = 'rec_type'
        if key[0]=="^" or key[0]=="@":
            key = key[1:]
        if isinstance(elem,list):
            if key=='names':
                do_names(elem, uitvoer, prefix)
            elif key=='links':
                do_links(elem, uitvoer, prefix)
            else:
                for e in elem:
                    if isinstance(e,dict):
                        uitvoer.write("{}<schema:{} rdf:parseType=\"Resource\">\n".format(indent(ind+2), key))
                        scrape_line(uitvoer, e, prefix, ind=ind+4, parent=key[:-1])
                        uitvoer.write("{}</schema:{}>\n".format(indent(ind+2), key))
                    elif isinstance(e,str):
                        e = escape(e)
                        uitvoer.write("{0}<schema:{1}>{2}</schema:{1}>\n".format(indent(ind+2), key,e))
                    else:
                        scrape_line(uitvoer, e, prefix, ind=ind+4, parent=key)
        elif isinstance(elem,dict):
            uitvoer.write("{}<schema:{} rdf:parseType=\"Resource\">\n".format(indent(ind), key))
            scrape_line(uitvoer, elem, prefix, ind=ind+4, parent=key)
            uitvoer.write("{}</schema:{}>\n".format(indent(ind), key))
        else:
            if not key=="@type":
                if parent=="variationRef" and key=="type":
                    schema_title = elem
                if parent=="modified" or parent=="created":
                    schema_title = f'{schema_title} {elem}'
                if isinstance(elem, str):
                    elem = escape(elem)
                note = ""
                if key=="date":
                    note =  " rdf:datatype=\"http://www.w3.org/2001/XMLSchema#date\""
                elif key=="notes":
                    note =  " rdf:parseType=\"Literal\""
                elif key=="displayName":
                    uitvoer.write("{0}<schema:name>{1}</schema:name>\n".format(indent(ind),elem))
                if key=="timeStamp":
                    schema_title = datetime.utcfromtimestamp(elem/1000).strftime("%Y-%m-%d, %H:%M:%S")
                uitvoer.write("{0}<{4}:{1}{3}>{2}</{4}:{1}>\n".format(indent(ind),key,elem,note,prefix))
    if schema_title!='':
        uitvoer.write("{0}<schema:title>{1}</schema:title>\n".format(indent(ind), schema_title.strip()))


def find_schema_title(uitvoer, record, titles):
    for title in titles:
        res = record[title]
        if res:
            uitvoer.write(f"    <schema:title>{res}</schema:title>\n")
            break
    if not res:
        uitvoer.write(f"    <schema:title>{record['_id']}</schema:title>\n")

def do_body(uitvoer, record, relations, prefix, titles):
    find_schema_title(uitvoer, record, titles)
    scrape_line(uitvoer, record, prefix)
    rels_in_record = record.get('@relations',{})
    for relation in rels_in_record:
        if relation in relations:
            for rel in rels_in_record[relation]:
                uitvoer.write('    <{3}:{0} rdf:resource="https://resource.huygens.knaw.nl/{3}/{1}s/{2}"/>\n'.format(relation, rel['type'], rel['id'], prefix))


def do_end_record(uitvoer, prefix):
    uitvoer.write(f'  </{prefix}:{domain}>\n')


def download_data(url, domains, datum, test, relation_tag='Relations'):
    for domain in domains.keys():
        json_uitvoer = open(f'{domain}_{datum}.json', "w", encoding='utf-8')
        json_uitvoer.write('[')
        domain_rels = relations.get(domain, {})
        start = 0
        rows = 100 # a larger amount frequently causes a time-out. With this amount downloading the data takes about 15 minutes.
        with_relations = "{}".format(domains[domain]).lower()
        res = {}
        teller = 0
        while True:
#            stderr(f"{url}{domain}?{relation_tag}={with_relations}&start={start}&rows={rows}")
            res = requests.get(f"{url}{domain}?{relation_tag}={with_relations}&start={start}&rows={rows}").json()
            teller += len(res)
            res_2 = res
            if with_relations=='true':
                res_2 = []
                for record in res:
#                    stderr(record['_id'])
                    result = requests.get(f"{url}{domain}/{record['_id']}")
#                    stderr(result.json())
                    rels = result.json().get('@relations')
#                    stderr(rels)
                    if rels:
                        record['@relations'] = rels
#                    else:
#                        record['@relations'] = {}
                    res_2.append(record)
            stderr("\n{0}: {1}".format(domain, teller))
            json_dump = json.dumps(res_2, sort_keys=False, indent=2)[1:-2]
            json_uitvoer.write(json_dump)
            if len(res)<rows or test:
                json_uitvoer.write('\n]')
                break
            start += rows
            json_uitvoer.write(',\n')
        json_uitvoer.close()


def stderr(text, newline=True):
    new_line = ''
    if newline:
        new_line = '\n'
    sys.stderr.write("{}{}".format(text,new_line))


def start():
    start_time = datetime.now()
    stderr("started at: {}".format(start_time.strftime("%H:%M:%S")))
    return start_time.strftime("%Y%m%d")


def stop():
    stop_time = datetime.now()
    stderr("stopped at: {}\nafter: {:1.0f} seconds".format(datetime.today().strftime("%H:%M:%S"),
                                                      ((stop_time - start_time).total_seconds())))
    sys.exit(0)


def arguments():
    ap = argparse.ArgumentParser()
    ap.add_argument('-d', '--download',
                    help="download data from website (True), or read files (False; default)",
                    default='false')
    ap.add_argument('-c', '--config',
                    help="configuration file")
    ap.add_argument('-f', '--files',
                    help="specify the used files")
    ap.add_argument('-t', '--test',
            help="set test: if true (default), maximum download of 100 records",
                    default='true')
    args = vars(ap.parse_args())
    return args

 

if __name__ == "__main__":

    startdate = start()
    args = arguments()
    do_download_data = args['download'].lower()=='true'
    with open(args['config'], encoding='utf-8') as invoer:
        config = json.load(invoer)
    datum = args.get('files')
    if datum==None:
        datum = config.get('file_ext',startdate)
    test = args['test'].lower()=='true'
    metadata = {}
    with open(config['relations'], encoding='utf-8') as invoer:
        relations = json.load(invoer)

    domains =  config['domains']
    prefix = config['prefix']
    titles = config.get('titles',{})

    if do_download_data:
        url = config['url']
        if not url.endswith('/'):
            url = f'{url}/'
        download_data(url, domains, datum, test)

    for domain in domains.keys():
        domain_data = {}
        stderr(f'{domain}_{datum}.json')
        with open(f'{domain}_{datum}.json', encoding='utf-8') as invoer:
            domain_data = json.load(invoer)
        domain_rels = relations.get(domain, {})
        xml_uitvoer = "{}_{}.xml".format(domain, datum)
        uitvoer = open(xml_uitvoer, "w", encoding="utf-8")
        do_header(uitvoer, prefix)
        teller = len(domain_data)
        stderr("\n{0}: {1}".format(domain, teller))
        for record in domain_data:
            do_start_record(uitvoer, domain, record['_id'], prefix)
            do_body(uitvoer, record, domain_rels, prefix, titles.get(domain, {}))
            do_end_record(uitvoer, prefix)
        do_footer(uitvoer)

    stop()

