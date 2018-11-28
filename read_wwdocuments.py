# -*- coding: utf-8 -*-
import argparse
import html
import json
import re
import sys
import unicodedata

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

    def add(self,categorie,value):
        if categorie in self.naam:
            self.naam[categorie] += " {}".format(value)
#            stderr("added {} more than once ({})\n".format(categorie,self.naam[categorie]))
        else:
            self.naam[categorie] = value

    def get(self,categorie):
        if categorie in self.combinations:
            return self.combine(categorie) 
        if categorie not in self.categories:
            return self.naam[categorie]
        return "unknown name part: {}".format(categorie)

    def combine(self,categorie):
#        print(categorie)
        if(categorie == "literalName"):
#            print("yes!")
          #  print(self.naam)
            result = ""
            for cat in self.categories:
                sys.stdout.write(" {}: ".format(cat))
                if cat in self.naam:
                    #print("{}".format(cat,self.naam[cat]))
                    result = result + " {}".format(self.naam[cat])
                #else:
                    ##print()
            return self.clean(result)
        elif(categorie == "surname"):
            return self.clean("{} {}",self.naam['surnamePrefix'],self.naam['baseSurname'])
        elif(categorie == "first"):
            return self.clean("{} {} {}",self.naam['givenName'],self.naam['patronym'],self.naam['givenNameSuffix'])
        elif(categorie == "infix"):
            return self.clean("{} {}",self.naam['InfixTitle'],self.naam['surnamePrefix'])
        elif(categorie == "suffix"):
            return self.clean("{} {} {}",self.naam['tralingPatronym'],self.naam['honorificSuffix'],self.naam['disambiguatingDescription'])

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
        uitvoer.write("{}: {}\n".format(type,value))
    uitvoer.write("<pnv:literalName>{}</pnv:literalName>\n".format(name.get('literalName')))


def do_names(list):
#    stderr("length list: {}".format(len(list)))
    for item in list:
#        print(item)
        do_components(item['components'],1)


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

        if isinstance(elem,list):
            #stderr("a list!")
            uitvoer.write("{}<schema:{}>\n".format(indent(ind),key))
            uitvoer.write("{}<rdf:Seq>\n".format(indent(ind+2)))
            for e in elem:
                if isinstance(e,dict):
#                    stderr("dict in list!\n")
                    uitvoer.write("{}<schema:{} rdf:parseType=\"Resource\">\n".format(indent(ind+4),key[0:-1]))
                    scrape_line(uitvoer,e,ind+6)
                    uitvoer.write("{}</schema:{}>\n".format(indent(ind+4),key[0:-1]))
                else:
                    scrape_line(uitvoer,e,ind+4)
            uitvoer.write("{}</rdf:Seq>\n".format(indent(ind+2)))
            uitvoer.write("{}</schema:{}>\n".format(indent(ind),key))
        elif isinstance(elem,dict):
            #stderr("{}: a dict!".format(key))
            uitvoer.write("{}<schema:{} rdf:parseType=\"Resource\">\n".format(indent(ind),key))
            scrape_line(uitvoer,elem,ind+4)
            uitvoer.write("{}</schema:{}>\n".format(indent(ind),key))
        else:
            if not key=="@type":
                if isinstance(elem,str):
                    elem = elem.replace("\n","\\n")
                    elem = html.escape(elem)
                note = ""
                if key=="date":
                    note =  " rdf:datatype=\"http://www.w3.org/2001/XMLSchema#date\""
                elif key=="notes":
                    note =  " rdf:parseType=\"Literal\""
                uitvoer.write("{0}<schema:{1}{3}>{2}</schema:{1}>\n".format(indent(ind),key,elem,note))


def arguments():
    ap = argparse.ArgumentParser()
    ap.add_argument('-i', '--inputfile',
                    help="inputfile",
                    default="./wwdocuments.json"
                    )
                
    ap.add_argument("-o", "--outputfile", help="outputfile",
                        default="./wwdocuments.xml")
    args = vars(ap.parse_args())
    return args


if __name__ == "__main__":

    args = arguments()
    inputfile = args['inputfile']
    outputfile = args['outputfile']

    res = locals()["stderr"]
    #method_to_call = getattr(local(), 'stderr')

    stderr("start")
    
    properties = { "forename" : "givenName", "name_link" : "surnamePrefix", "surname" : "baseSurname", "add_name" : "trailingPatronym", "role_name" : "prefix", "gen_name" : "givenNameSuffix" }
    
    uitvoer = open(outputfile,"w", encoding="utf-8")

    header = '''<?xml version="1.0"?>
<rdf:RDF
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:schema="http://schema.org/"
    xmlns:pnv="http://www.purl.org/pnv/"
    xmlns:ww="https://resource.huygens.knaw.nl/women_writers/ww"
    xmlns:person="https://resource.huygens.knaw.nl/women_writers/document">
'''

    uitvoer.write(header)


    inputtext = json.load(open(inputfile, encoding='utf-8', errors="surrogateescape"))
    
    tel = 0
    for item in inputtext:
        #stderr(tel)
        topline = """    <rdf:Description rdf:about="https://resource.huygens.knaw.nl/ww/{}/{}">
    <rdf:type rdf:resource="https://resource.huygens.knaw.nl/ww/{}" />
"""
        uitvoer.write(topline.format(item['@type'],item['_id'],item['@type']))
#        print(json.dumps(item,indent=4))
        scrape_line(uitvoer,item)
        uitvoer.write("    </rdf:Description>\n\n")
        tel += 1

    uitvoer.write("</rdf:RDF>\n")

    stderr("einde")
