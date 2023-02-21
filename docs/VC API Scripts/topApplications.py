import requests
import json
import csv
import common

#Setup session for API requests from TDL VCO

serverUrl = 'https://van-th-orch-prod.radiant.net/portal/'
session = requests.Session()
session.headers.update({'Content-Type': 'application/json','Authorization': 'Token ' + common.token})

#Get identifiable applications

requestData = {
    "jsonrpc": "2.0",
    "method": "configuration/getIdentifiableApplications",
    "params": {
        "enterpriseId": 1,
    },
    "id": 1
}
response = session.post(serverUrl,data=json.dumps(requestData))
appClasses = response.json()['result']['applicationClasses']
apps = response.json()['result']['applications']

#Get Edges

requestData = {"jsonrpc":"2.0","method":"enterprise/getEnterpriseEdges","params":{"id": 1,"enterpriseId":1,"with": ["site"]},"id":1}
response = session.post(serverUrl,data=json.dumps(requestData))
edges = response.json()['result']

for count, edge in enumerate(edges):
    print("Processing for edge "+edge['name']+" (#"+str(count+1)+"/"+str(len(edges))+")")
#Get application metrics
    requestData = {
        "jsonrpc": "2.0",
        "method": "metrics/getEdgeAppMetrics",
        "params": {
            "metrics": [
                "totalBytes",
                "bytesRx",
                "bytesTx",
                "totalPackets",
                "packetsRx",
                "packetsTx"
            ],
            "with": [
                "category"
            ],
            "edgeId": edge['id'],
            "interval": {
                "start": 1670816537578
            },
            "enterpriseId": 1,
            "limit": -1
        },
        "id": 13
    }
    response = session.post(serverUrl,data=json.dumps(requestData))
    appMetrics = response.json()['result']
    #print(json.dumps(appMetrics, indent=4))

    output_file = open(f'Edges_Top_Apps/{edge["name"]}.csv', mode='w', newline='\n')
    field_names = ['Application','Category','Total Bytes','Bytes Received','Bytes Sent']
    csv_writer = csv.DictWriter(output_file, field_names, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
    csv_writer.writeheader()

    for app in appMetrics:
        
        if app['category'] == 0:
            appName = "Unknown virtual protocol"
        else:
            appName = [appData for appData in apps if appData['id'] == app['application']][0]['displayName']
        appCategory = appClasses[app['category']]
        totalBytes = app['totalBytes']
        bytesRx = app['bytesRx']
        bytesTx = app['bytesTx']

        csv_writer.writerow({
            'Application': appName,
            'Category': appCategory,
            'Total Bytes': totalBytes,
            'Bytes Received': bytesTx,
            'Bytes Sent': bytesRx
        })
