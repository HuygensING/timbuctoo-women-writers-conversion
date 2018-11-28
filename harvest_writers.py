import json
#import urllib.request
import requests
import sys

def stderr(text):
    sys.stderr.write("{}\n".format(text))


if __name__ == "__main__":

    stderr("start")

    url = "https://repository.huygens.knaw.nl/solr/wwdocuments/select"
    headers = {'Content-type': 'application/x-www-form-urlencoded'}
    query = 'q=*:*&fq=%7B!parent%20which%3Dtype_s%3Adocument%7Dperson_relatedLocations_ss%3A(%22Netherlands%22)&fq=%7B!parent%20which%3Dtype_s%3Adocument%7Dperson_language_ss%3A(%22Dutch%22)&fq=type_s%3Adocument&rows=100000&wt=json'
    query = {
            "fl":"id",
            "q":"*:*",
            "fq":["{!parent which=type_s:document}person_relatedLocations_ss:(\"Netherlands\")",
        "{!parent which=type_s:document}person_language_ss:(\"Dutch\")",
        "type_s:document"],
            "rows":100000,
            "wt":"json"
            }
    res = requests.post(url,headers=headers, data=query)
#    stderr(res.url)
#    stderr(res.json())
#    stderr("{}".format(res)
    stderr("{} responses\n".format(len(res.json()['response']['docs'])))
#    print(json.dumps(res.json()['response']['docs'],indent=4))
    stderr("end")

    id_list = res.json()['response']['docs']
    for id in id_list:
        url = "https://repository.huygens.knaw.nl/v2.1/domain/wwdocuments/{}".format(id['id'])
#        stderr(url)
        answer = requests.get(url)
        res = answer.json()
#        stderr(answer.url)
        print(json.dumps(res,indent=4))
#        break



# http://docs.python-requests.org/en/master/user/quickstart/#custom-headers
