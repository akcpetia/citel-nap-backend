import requests
import json
import csv
from requests.adapters import HTTPAdapter, Retry
import common

#Setup API Request Session from TH VCO

retries = Retry(total=5, backoff_factor=1, status_forcelist=[ 502, 503, 504 ])
serverUrl = 'https://van-th-orch-prod.radiant.net/portal/'
session = requests.Session()
session.headers.update({'Content-Type': 'application/json','Authorization': 'Token ' + common.token})
session.mount('https://', HTTPAdapter(max_retries=retries))

interval = {
        "start": 1671944400000, # Sunday, December 25, 2022 12:00:00 AM GMT-05:00
        "end": 1672549200000 # Sunday, January 1, 2023 12:00:00 AM GMT-05:00
    }

#Get Edges and Links List

requestData = {
    "jsonrpc": "2.0",
    "method": "enterprise/getEnterpriseEdgeList",
    "params": {
        "with": [
            "recentLinks",
            "site",
            "ha",
            "vnfs",
            "isSoftwareVersionSupportedByVco"
        ],
        "enterpriseId": 1
    },
    "id": 1
}

response = session.post(serverUrl,data=json.dumps(requestData))
edges = response.json()['result']

#create CSV file

output_file = open(f'Link_Quality_Report_test.csv', mode='w', newline='\n')
field_names = ['Edge','Link','Mode','IP Address','Quality Score']
csv_writer = csv.DictWriter(output_file, field_names, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
csv_writer.writeheader()

for count,edge in enumerate(edges):
    print("Edge "+edge['name']+" (#"+str(count+1)+"/"+str(len(edges))+"):")
    requestData = {
        "id": 9,
        "jsonrpc": "2.0",
        "method": "linkQualityEvent/getLinkQualityEvents",
        "params": {
            "interval": interval,
            "edgeId": edge['id'],
            "enterpriseId": 1,
            "maxSamples": 80
        }
    }

    response = session.post(serverUrl,data=json.dumps(requestData))
    try:
        linkQualityMetrics = list(response.json()['result'].items())
    except:
        print("No recent links for this Edge.\n")
        continue

    for linkMetric in linkQualityMetrics:

        if linkMetric[0] == "overallLinkQuality":
            linkName = "Overall Link Quality"
            linkMode = ""
            ipAddress = ""
        else:
            link = [e for e in edge['recentLinks'] if e['internalId'] == linkMetric[0]][0]
            linkName = link['displayName']
            linkMode = link['linkMode']
            ipAddress = link['ipAddress']

        csv_writer.writerow({
            'Edge': edge['name'],
            'Link': linkName,
            'Mode': linkMode,
            'IP Address': ipAddress,
            'Quality Score': linkMetric[1]['totalScore']
        })

        print("Processing done for link "+linkName+".")

    print('Done.\n') 

