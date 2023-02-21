import requests
import json
import csv
import common

#Setup session for API requests from TDL VCO

serverUrl = 'https://van-th-orch-prod.radiant.net/portal/'
session = requests.Session()
session.headers.update({'Content-Type': 'application/json','Authorization': 'Token ' + common.token})

#Get Edges List (contains link data)

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
edgesList = response.json()['result']['applicationClasses']
apps = response.json()['result']['applications']