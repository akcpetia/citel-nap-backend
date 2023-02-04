import requests
import json
import math
import csv
import common


#Setup API Request Session from TH VCO

serverUrl = 'https://van-th-orch-prod.radiant.net/portal/'
session = requests.Session()
session.headers.update({'Content-Type': 'application/json','Authorization': 'Token ' + common.token})
interval = {
        "start": 1669870800000,
        "end": 1672549200000
    }
#Get Alerts Count and need number of API calls for the requested period

requestData = {
  "id": 1,
  "jsonrpc": "2.0",
  "method": "enterprise/getEnterpriseAlertsList",
  "params": {
    "filters": {
      "and": [
        {
          "field": "enterpriseAlertConfigurationId",
          "operator": "isNotNull"
        }
      ]
    },
    "with": [
      "notifications"
    ],
    "enterpriseId": 1,
    "interval": interval,
    "_count": True
  }
}
response = session.post(serverUrl,data=json.dumps(requestData))
alertsCount = response.json()['result']['count']
numberRequests = math.ceil(alertsCount/512)

#Make initial alerts request

requestData = {
    "id": 2,
    "jsonrpc": "2.0",
    "method": "enterprise/getEnterpriseAlertsList",
    "params": {
        "filters": {
            "and": [
                {
                    "field": "enterpriseAlertConfigurationId",
                    "operator": "isNotNull"
                }
            ]
        },
        "with": [
            "notifications"
        ],
        "sortBy": [
            {
                "attribute": "triggerTime",
                "type": "DESC"
            }
        ],
        "enterpriseId": 1,
        "interval": interval,
        "limit": 512,
    }
}
response = session.post(serverUrl,data=json.dumps(requestData))
alerts = response.json()['result']['data']
nextPageLink = response.json()['result']['metaData']['nextPageLink']

#create CSV file

output_file = open(f'Alerts_Report_test.csv', mode='w', newline='\n')
field_names = ['ID','Trigger Time','Notification Time','Category','Type','Description','Status']
csv_writer = csv.DictWriter(output_file, field_names, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
csv_writer.writeheader()
for count,alert in enumerate(alerts):
    type = alert['type'].replace('_',' ').lower().title()
    if type.split()[0] == 'Edge':
        description = "Edge "+str(alert['edgeName'])+" "+type.split()[1]
    elif type.split()[0] == 'Link':
        description = alert['linkName']+" "+type+" on Edge "+str(alert['edgeName'])
    try:
        notificationTime = alert['notifications'][0]['notificationTime'].replace('T',' ').replace('Z','')
    except:
        notificationTime = "Pending"
    
    csv_writer.writerow({
        'ID':                   alert['id'],
        'Trigger Time':         alert['triggerTime'].replace('T',' ').replace('Z',''),
        'Notification Time':    notificationTime,
        'Category':             'Customer',
        'Type':                 type,
        'Description':          description,
        'Status':               alert['state'].lower().title() 
        })

numberRequests -= 1
counter = 1
# Loop through the rest of the events
lastPage = False
while lastPage == False:
    print("API Call #"+str(counter))
    requestData = {
        "id": 2,
        "jsonrpc": "2.0",
        "method": "enterprise/getEnterpriseAlertsList",
        "params": {
            "filters": {
                "and": [
                    {
                        "field": "enterpriseAlertConfigurationId",
                        "operator": "isNotNull"
                    }
                ]
            },
            "with": [
                "notifications"
            ],
            "sortBy": [
                {
                    "attribute": "triggerTime",
                    "type": "DESC"
                }
            ],
            "enterpriseId": 1,
            "interval": interval,
            "nextPageLink": nextPageLink,
            "limit": 512,
        }
    }

    response = session.post(serverUrl,data=json.dumps(requestData))
    alerts = response.json()['result']['data']
    try:
        nextPageLink = response.json()['result']['metaData']['nextPageLink']
    except:
        print("This is the last page.")
        lastPage = True

    for count,alert in enumerate(alerts):
        type = alert['type'].replace('_',' ').lower().title()
        if type.split()[0] == 'Edge':
            description = "Edge "+str(alert['edgeName'])+" "+type.split()[1]
        elif type.split()[0] == 'Link':
            description = alert['linkName']+" "+type+" on Edge "+str(alert['edgeName'])
        try:
            notificationTime = alert['notifications'][0]['notificationTime'].replace('T',' ').replace('Z','')
        except:
            notificationTime = "Pending"
        
        csv_writer.writerow({
            'ID':                   alert['id'],
            'Trigger Time':         alert['triggerTime'].replace('T',' ').replace('Z',''),
            'Notification Time':    notificationTime,
            'Category':             'Customer',
            'Type':                 type,
            'Description':          description,
            'Status':               alert['state'].lower().title() 
            })

    counter += 1