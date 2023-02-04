import requests
import json
import csv
import common

serverUrl = 'https://van-th-orch-prod.radiant.net/portal/'
session = requests.Session()
session.headers.update({'Content-Type': 'application/json','Authorization': 'Token ' + common.token})

requestData1 = {"jsonrpc":"2.0","method":"enterprise/getEnterpriseEdges","params":{"id": 1,"enterpriseId": 1,"with": ["site"]},"id":1}
response = session.post(serverUrl,data=json.dumps(requestData1))
requestResult1 = response.json()['result']

output_file = open(f'Edge_GeoData.csv', mode='w', newline='\n')
field_names = ['Edge','State','Street Address','City','Province','Postal Code','Longitude','Latitude']
csv_writer = csv.DictWriter(output_file, field_names, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
csv_writer.writeheader()

for edge in requestResult1:
    csv_writer.writerow({
        'Edge': edge['name'],
        'State': edge['edgeState'],
        'Street Address': edge['site']['streetAddress'],
        'City': edge['site']['city'],
        'Province': edge['site']['state'],
        'Postal Code': edge['site']['postalCode'],
        'Longitude': edge['site']['lon'],
        'Latitude': edge['site']['lat']

    })