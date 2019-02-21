# -*- coding: utf-8 -*-
import argparse
from datetime import datetime
from datetime import date
import html
import json
import locale
locale.setlocale(locale.LC_ALL, 'nl-NL') 
import re
import sys
import unicodedata
import urllib.parse

class PnvPerson:

    categories = [
        "prefix",
        "givenName",
        "patronym",
        "givenNameSuffix",
        "infixTitle",
        "surnamePrefix",
        "baseSurname",
        "trailingPatronym",
        "honorificSuffix",
        "disambiguatingDescription"
    ]

    combinations = [
        "surname",
        "literalName",
        "firstName",
        "infix",
        "suffix"
    ]

    def __init__(self):
        self.naam = {}
        for cat in self.categories:
            self.naam[cat] = ''

    def add(self,categorie,value):
        if categorie in self.naam:
            self.naam[categorie] += " {}".format(value)
#            stderr("added {} more than once ({})\n".format(categorie,self.naam[categorie]))
        else:
            stderr("unknown categorie: {}".format(categorie))
            self.naam[categorie] = value

    def get(self,categorie):
        if categorie in self.combinations:
            return self.combine(categorie) 
        if categorie in self.categories:
            return self.clean(self.naam[categorie])
        return "unknown name part: {}".format(categorie)

    def combine(self,categorie):
#        print(categorie)
        if(categorie == "literalName"):
#            print("yes!")
          #  print(self.naam)
            result = ""
            for cat in self.categories:
#                stderr(" {}: ".format(cat))
                if cat in self.naam:
                    #print("{}".format(cat,self.naam[cat]))
                    result = result + " {}".format(self.naam[cat])
                #else:
                    ##print()
            return self.clean(result)
        elif(categorie == "surname"):
            return self.clean("{} {}".format(self.naam['surnamePrefix'],self.naam['baseSurname']))
        elif(categorie == "firstName"):
            return self.clean("{} {} {}".format(self.naam['givenName'],self.naam['patronym'],self.naam['givenNameSuffix']))
        elif(categorie == "infix"):
            return self.clean("{} {}".format(self.naam['infixTitle'],self.naam['surnamePrefix']))
        elif(categorie == "suffix"):
            return self.clean("{} {} {}".format(self.naam['trailingPatronym'],self.naam['honorificSuffix'],self.naam['disambiguatingDescription']))

    def clean(self,text):
        #print(text)
        pattern = re.compile("  +")
        pattern_2 = re.compile("' ")
        result = re.sub(pattern," ",text)
        result = re.sub(pattern_2,"'",result)
        #print(result.strip())
        return result.strip()
        #text.replace(/  +/," ").gsub(/' /,"'").strip()

    def to_h(self):
        return self.naam

    def to_s(self):
        pass

# end class



def find_property(value):
    result = properties[value.lower()]
    if result:
        return result
    return value


def do_components(elems,indent):
    name = PnvPerson()
    for elem in elems:
        type = find_property(elem['type'])
        value = elem['value']
        name.add(type,value)
#        uitvoer.write("{}: {}\n".format(type,value))
#    stderr("<pnv:literalName>{}</pnv:literalName>\n".format(name.get('literalName')))
#    stderr("name: {}".format(name))
    return name


def do_names(list):
#    stderr("length list: {}".format(len(list)))
    all_names = []
    for item in list:
#        print(item)
        res = do_components(item['components'],1)
#       stderr("res: {}".format(res))
        all_names.append(res)
    return all_names


def do_relations(uitvoer,item,ind):
    for key,elem in item.items():
#        stderr(key)
        for el in elem:
#            stderr(el['id'])
#            stderr(el['type'])
#            stderr(el['displayName'])
            uitvoer.write('{0}<ww:{1} rdf:resource="https://resource.huygens.knaw.nl/ww/{2}/{3}"/>\n'.format(
                indent(ind), key, el['type'], el['id']))
            if el['type'] in relatedObjects:
                new_obj = [el['displayName'].replace(" & "," &amp; "),el['id']]
                if not new_obj in relatedObjects[el['type']]:
                    relatedObjects[el['type']].append(new_obj)
            else:
                stderr("{} ontbreekt in relatedObjects".format(el['type']))
                stderr("id         : {}".format(el['id']))
                stderr("displayName: {}".format(el['displayName']))
    pass

def stderr(text):
    sys.stderr.write("{}\n".format(text))

def indent(num=4):
    return num * " "


def scrape_line(uitvoer,item,ind=4):
    for key,elem in item.items():
#        uitvoer.write("{}\n".format(key))
#        elem = item[key]
        if key[0]=="^":
            key = key[1:]
        if key[0]=="@":
            key = key[1:]
        prefix = "schema"
        if key in wwPrefix:
            prefix = "ww"
        if key in dctermsPrefix:
            prefix = "dcterms"

        if key.startswith('temp'):
            pass
        elif key in ignore:
            pass
        elif key=="type" and elem in objects and ind==4:
            pass
        elif isinstance(elem,list):
            #stderr("a list!")
            uitvoer.write("{0}<{2}:{1}>\n".format(indent(ind),key,prefix))
            uitvoer.write("{}<rdf:Seq>\n".format(indent(ind+2)))
            for e in elem:
                if isinstance(e,dict):
#                    stderr("dict in list!\n")
                    uitvoer.write("{0}<{2}:{1} rdf:parseType=\"Resource\">\n".format(indent(ind+4),key[0:-1],prefix))
                    scrape_line(uitvoer,e,ind+6)
                    uitvoer.write("{0}</{2}:{1}>\n".format(indent(ind+4),key[0:-1],prefix))
                else:
                    scrape_line(uitvoer,e,ind+4)
            uitvoer.write("{}</rdf:Seq>\n".format(indent(ind+2)))
            uitvoer.write("{0}</{2}:{1}>\n".format(indent(ind),key,prefix))
        elif isinstance(elem,dict):
            if key=="modified" or key=="created":
#                stderr("modified")
#                stderr(elem['timeStamp'])
#                stderr(int(elem['timeStamp']))
#                stderr(datetime.fromtimestamp(1545730073))
#                stderr(datetime.timestamp(datetime.fromisoformat("2014-09-25T11:03:03")))
#                stderr(datetime.fromtimestamp(1411642983))
                datum = datetime.fromtimestamp(int(elem['timeStamp']/1000)).strftime("%Y-%m-%dT%H:%M:%S")
#                stderr(elem['userId'])
#                uitvoer.write("{0}<{2}:{1}>{3}</{0}<{2}:{1}>\n".format(indent(ind),key,prefix,elem['timeStamp']))
                uitvoer.write("{0}<dcterms:{2}>{1}</dcterms:{2}>\n".format(indent(ind),datum,key))
                uitvoer.write("{0}<ww:{2}By>{1}</ww:{2}By>\n".format(indent(ind),elem['userId'],key))
            else:
            #stderr("{}: a dict!".format(key))
                prefix = "ww"
                if key=="relations":
                    do_relations(uitvoer,elem,ind)
                else:
                    uitvoer.write("{0}<{2}:{1} rdf:parseType=\"Resource\">\n".format(indent(ind),key,prefix))
                    scrape_line(uitvoer,elem,ind+4)
                    uitvoer.write("{0}</{2}:{1}>\n".format(indent(ind),key,prefix))
        else:
            if not key=="@type":
                if isinstance(elem,str):
#                    elem = elem.replace("\n","\\n")
                    elem = html.escape(elem)
                note = ""
                if key=="date":
                    note =  ' rdf:datatype="xsd:gYear"'
                elif key=="notes":
                    note =  ' rdf:datatype="xsd:string"'
                    prefix = "skos"
                    key = "note"
                uitvoer.write("{0}<{4}:{1}{3}>{2}</{4}:{1}>\n".format(indent(ind),key,elem,note,prefix))
                if key=="displayName" and add_title:
                    uitvoer.write("{0}<schema:title>{1}</schema:title>\n".format(indent(ind),elem))


def arguments():
    ap = argparse.ArgumentParser()
    ap.add_argument('-i', '--inputfile',
                    help="inputfile",
                    default="./ww_query_result_first.json"
                    )
                
    ap.add_argument("-o", "--outputfile", help="outputfile",
                        default="./ww_query_result_first.xml")
    ap.add_argument("-t", "--addtitle", help="voeg <schema:title> toe (indien True); default: False",
                        default=False)
    args = vars(ap.parse_args())
    return args


if __name__ == "__main__":

    args = arguments()
    inputfile = args['inputfile']
    outputfile = args['outputfile']
    add_title = args['addtitle']

    aant_writers = 0
    aant_meerdere_namen = 0
    aant_meerdere_links = 0
    ignore = ['rdfAlternatives','variationRefs','relationCount','_id','rev','deleted','links']

    wwPrefix = ['modifiedBy', 'createdBy', 'documentType', 'isWorkCommentedOnIn', 'isStoredAt', 'isPublishedBy',
            'isCreatedBy', 'hasGenre', 'hasPublishLocation', 'hasWorkLanguage', 'displayName', 'pid']
    schemaPrefix = ['date']
    dctermsPrefix = ['modified','created','title']
    skosPrefix = ['notes']

    relatedObjects = { }
    objects =  [ "wwcollective", "wwperson", "wwkeyword", "wwlocation", "wwlanguage", "wwdocument" ]
    for obj in objects:
        relatedObjects[obj] = []

    res = locals()["stderr"]
    #method_to_call = getattr(local(), 'stderr')

    stderr("start")
    
    properties = { "forename" : "givenName", "name_link" : "surnamePrefix", "surname" : "baseSurname", "add_name" : "trailingPatronym", "role_name" : "prefix", "gen_name" : "givenNameSuffix" }
    
    uitvoer = open(outputfile,"w", encoding="utf-8")

    header = '''<?xml version="1.0"?>
<rdf:RDF
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:xsd="http://www.w3.org/2001/XMLSchema#"
    xmlns:schema="http://schema.org/"
    xmlns:ww="https://resource.huygens.knaw.nl/ww/"
    xmlns:dcterms="http://purl.org/dc/terms/modified"
    xmlns:pnv="http://www.purl.org/pnv/"
    xmlns:skos="http://www.w3.org/2004/02/skos/core#">
'''

    uitvoer.write(header)


    inputtext = json.load(open(inputfile, encoding='utf-8', errors="surrogateescape"))
    
    tel = 0
    for item in inputtext:
        #stderr(tel)
        topline = """
  <ww:wwdocument rdf:about="https://resource.huygens.knaw.nl/ww/{}/{}">
"""
        uitvoer.write(topline.format(item['@type'],item['_id']))
#        print(json.dumps(item,indent=4))
        scrape_line(uitvoer,item)
        uitvoer.write("  </ww:wwdocument>\n")
        tel += 1


# get the writers
    look_for_ids = []
    found_writers = {}
    labels = ['^pid', 'types', 'gender', 'birthDate', 'deathDate', 'notes', 'bibliography',
            'children', 'health', 'livedIn', 'nationality', 'personalSituation', 'links']
    for obj in relatedObjects["wwperson"]:
        look_for_ids.append(obj[1])
    inputtext = json.load(open("all_writers.json", encoding='utf-8', errors="surrogateescape"))
    for item in inputtext:
        if item["_id"] in look_for_ids:
            res = do_names(item["names"])
            found_writers[item["_id"]] = {}
            found_writers[item["_id"]]['name'] = res[0]
            found_writers[item["_id"]]['names'] = res
            if len(res) > 1:
#                stderr("meer dan 1 naam: {}".format(res))
                aant_meerdere_namen += 1
            # links ook tellen
            for label in labels:
                try:
                    if label=="types":
                        found_writers[item["_id"]]['type'] = ' '.join(item[label])
                    elif label=="notes":
                        found_writers[item["_id"]]['note'] = item[label].replace(" & "," &amp; ").replace("<","&lt;").strip()
                    elif label=="^pid":
                        found_writers[item["_id"]]['pid'] = item[label]
                        new_label = "pid"
                    elif label=="bibliography":
                        found_writers[item["_id"]][label] = item[label].replace(" & "," &amp; ")
                    elif label=="links":
                        all_links = []
                        for link in item[label]:
                            if not link['url']=="":
                                if link['label']=="":
                                    link['label'] = link['url']
                                all_links.append(link)
                        found_writers[item["_id"]][label] = all_links
                    else:
                        found_writers[item["_id"]][label] = item[label]
                except KeyError:
                    pass


    ind = 2
#    stderr(relatedObjects)
    for key in relatedObjects.keys():
        if not key=="wwperson":
            uitvoer.write("\n")
#        stderr("{}: {}".format(key,relatedObjects[key]))
            for obj in relatedObjects[key]:
#            stderr(obj)
                if add_title:
                    schema_title = "{0}  <schema:title>{1}</schema:title>\n".format(indent(ind),obj[0])
                else:
                    schema_title = ""
                uitvoer.write('''{0}<ww:{1} rdf:about="https://resource.huygens.knaw.nl/ww/{1}/{2}">
{0}  <ww:displayName>{3}</ww:displayName>
{4}  </ww:{1}>
'''.format(indent(ind),key,obj[1],obj[0],schema_title))

# wwpersons
    uitvoer.write("\n")
    labels = ['pid', 'type', 'gender', 'birthDate', 'deathDate', 'bibliography',
            'children', 'health', 'livedIn', 'nationality', 'personalSituation']
    for obj in relatedObjects["wwperson"]:
#        stderr(obj)
#        if add_title:
#            schema_title = "{0}  <schema:title>{1}</schema:title>\n".format(indent(ind),obj[0])
#        else:
#            schema_title = ""
#        uitvoer.write('''{0}<ww:{1} rdf:about="https://resource.huygens.knaw.nl/ww/{1}/{2}">
#{0}  <ww:displayName>{3}</ww:displayName>
#{4}  </ww:{1}>
#'''.format(indent(ind),"wwperson",obj[1],obj[0],schema_title)
        uitvoer.write('  <ww:wwperson rdf:about="https://resource.huygens.knaw.nl/ww/wwperson/{}">\n'.format(obj[1]))
        uitvoer.write('    <ww:displayName>{}</ww:displayName>\n'.format(obj[0]))
        if add_title:
            uitvoer.write("    <schema:title>{}</schema:title>\n".format(obj[0]))

        writers = found_writers[obj[1]]['names']
        for writer in writers:
            uitvoer.write('    <ww:nameComponents rdf:parseType="Resource">\n')
            if add_title:
                uitvoer.write('      <schema:title>{}</schema:title>\n'.format(writer.get("literalName")))
            if not writer.get("prefix")=="":
                uitvoer.write("      <pnv:prefix>{}</pnv:prefix>\n".format(writer.get("prefix")))
            if not writer.get("firstName")=="":
                uitvoer.write("      <pnv:firstName>{}</pnv:firstName>\n".format(writer.get("firstName")))
            if not writer.get("infix")=="":
                uitvoer.write("      <pnv:infix>{}</pnv:infix>\n".format(writer.get("infix")))
            if not writer.get("baseSurname")=="":
                uitvoer.write("      <pnv:baseSurname>{}</pnv:baseSurname>\n".format(writer.get("baseSurname")))
            if not writer.get("suffix")=="":
                uitvoer.write("      <pnv:suffix>{}</pnv:suffix>\n".format(writer.get("suffix")))
            uitvoer.write("    </ww:nameComponents>\n")

        for label in labels:
            try:
                if not found_writers[obj[1]][label]=="":
                    uitvoer.write('    <ww:{0}>{1}</ww:{0}>\n'.format(label,found_writers[obj[1]][label]))
            except:
                pass
                #uitvoer.write('    <ww:{}/>\n'.format(label))
        try:
            if not found_writers[obj[1]]['note']=="":
                uitvoer.write('    <skos:note rdf:datatype="xsd:string">{1}</skos:note>\n'.format(label,found_writers[obj[1]]['note']))
        except:
            pass
#            uitvoer.write('    <skos:note/>\n'.format(label))
        try:
            if len(found_writers[obj[1]]['links'])>1:
#                stderr("meer dan 1 link: {}".format(found_writers[obj[1]]['links']))
                aant_meerdere_links += 1
            for link in found_writers[obj[1]]['links']:
                uitvoer.write('      <ww:link>\n')
                #  niet zo tevreden met urllib: misschien alleen & vervangen door
                # uitvoer.write('        <rdf:Description rdf:about="{}">\n'.format(urllib.parse.quote(link['url'])))
                uitvoer.write('        <rdf:Description rdf:about="{}">\n'.format(link['url'].replace("&","%26").replace(" ","%20")))
                uitvoer.write('          <ww:label>{}</ww:label>\n'.format(link['label']))
                uitvoer.write('        </rdf:Description>\n'.format(link['url']))
                uitvoer.write('      </ww:link>\n')
#                break
        except KeyError as err:
            stderr("error: {}".format(err))
        except:
            stderr("Unexpected error: {}".format(sys.exc_info()[0]))
            raise
#            uitvoer.write('    <ww.links/>\n'.format(label))
#            uitvoer.write('    </ww.links>\n'.format(label))

        uitvoer.write('  </ww:wwperson>\n')

    uitvoer.write("\n</rdf:RDF>\n")

    stderr("aantal writers: {}".format(len(found_writers)))
    stderr("aantal meerdere namen: {}".format(aant_meerdere_namen))
    stderr("aantal meerdere links: {}".format(aant_meerdere_links))
    stderr("einde")
