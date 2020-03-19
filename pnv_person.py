# -*- coding: utf-8 -*-
import re
import sys

class PnvPerson(dict):
    def __missing__(self, key):
        return ""

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
        else:
            self.naam[categorie] = value

    def get(self,categorie):
        if categorie in self.combinations:
            return self.combine(categorie) 
        if categorie not in self.categories:
            try:
                return self.naam[categorie]
            except KeyError:
                pass
        return "unknown name part: {}".format(categorie)

    def __get(self, categorie):
        try:
            return self.naam[categorie]
        except KeyError:
            return ""

    def combine(self,categorie):
        if(categorie == "literalName"):
            result = ""
            for cat in self.categories:
                if cat in self.naam:
                    result = result + " {}".format(self.naam[cat])
            return self.clean(result)
        elif(categorie == "surname"):
            return self.clean(f"{self.naam['surnamePrefix']} {self.naam['baseSurname']}")
        elif(categorie == "firstName"):
            return self.clean(f"{self.__get('givenName')} {self.__get('patronym')} {self.__get('givenNameSuffix')}")
        elif(categorie == "infix"):
            return self.clean(f"{self.__get('InfixTitle')} {self.__get('surnamePrefix')}")
        elif(categorie == "suffix"):
            return self.clean(f"{self.__get('trailingPatronym')} {self.__get('honorificSuffix')} {self.__get('disambiguatingDescription')}")

    def clean(self,text):
        pattern = re.compile("  +")
        pattern_2 = re.compile("' ")
        result = re.sub(pattern," ",text)
        result = re.sub(pattern_2,"'",result)
        return result.strip()

    def to_h(self):
        return self.naam

    def to_s(self):
        return self.get('literalName')

