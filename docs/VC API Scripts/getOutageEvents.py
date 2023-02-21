import requests
import json
import datetime
import pytz
import csv
from requests.adapters import HTTPAdapter, Retry
import common

#Setup API Request Session from TH VCO

retries = Retry(total=5, backoff_factor=1, status_forcelist=[ 502, 503, 504 ])
serverUrl = 'https://van-th-orch-prod.radiant.net/portal/'
#token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlblV1aWQiOiJkZjZiZDk2NC1hMzkxLTQ1ODgtYWE4Ni1kYWE2ZWJjZDU4MTYiLCJleHAiOjE2OTU0ODA2NzEwMDAsInV1aWQiOiJjM2E1ZWQ2ZC0wZmRjLTExZWEtYmM4OS0wMDUwNTZiMWU0YWYiLCJpYXQiOjE2NjM5NDQ2NzV9.sT8yO4BlAvQqMa-56vZCXoZmMkjTm3u7dom-m9AkYbM'
session = requests.Session()
session.headers.update({'Content-Type': 'application/json','Authorization': 'Token ' + common.token})
session.mount('https://', HTTPAdapter(max_retries=retries))

interval = {
        "start":  int(datetime.datetime(2023,1,2,0,0,0).timestamp()*1000),
        "end":  int(datetime.datetime(2023,1,9,0,0,0).timestamp()*1000) 
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
results = response.json()['result']
edges = []
links = []
for result in results:
    links += result['recentLinks']
    del result['recentLinks']
    edges.append(result)

print("Edges Count: "+str(len(edges)))
print("Links Count: "+str(len(links)))

print(json.dumps(links[0],sort_keys=True, indent=4))

#Get target events count

requestData = {
    "id": 10,
    "jsonrpc": "2.0",
    "method": "event/getEnterpriseEventsList",
    "params": {
        "enterpriseId": 1,
        "interval": interval,
        "filters": {
            "and": [
                {
                    "field": "event",
                    "operator": "is",
                    "value": "LINK_DEAD"
                }
            ]
        },
        "_count": True
    }
}

response = session.post(serverUrl,data=json.dumps(requestData))
results = response.json()['result']
linkDeadEventsCount = results['count']
print("Link Dead Events Count: "+str(linkDeadEventsCount))

requestData = {
    "id": 10,
    "jsonrpc": "2.0",
    "method": "event/getEnterpriseEventsList",
    "params": {
        "enterpriseId": 1,
        "interval": interval,
        "filters": {
            "and": [
                {
                    "field": "event",
                    "operator": "is",
                    "value": "LINK_ALIVE"
                }
            ]
        },
        "_count": True
    }
}

response = session.post(serverUrl,data=json.dumps(requestData))
results = response.json()['result']
linkAliveEventsCount = results['count']
print("Link Alive Events Count: "+str(linkAliveEventsCount))

requestData = {
    "id": 10,
    "jsonrpc": "2.0",
    "method": "event/getEnterpriseEventsList",
    "params": {
        "enterpriseId": 1,
        "interval": interval,
        "filters": {
            "and": [
                {
                    "field": "event",
                    "operator": "is",
                    "value": "EDGE_DOWN"
                }
            ]
        },
        "_count": True
    }
}

response = session.post(serverUrl,data=json.dumps(requestData))
results = response.json()['result']
EdgeDownEventsCount = results['count']
print("Edge Down Events Count: "+str(EdgeDownEventsCount))

requestData = {
    "id": 10,
    "jsonrpc": "2.0",
    "method": "event/getEnterpriseEventsList",
    "params": {
        "enterpriseId": 1,
        "interval": interval,
        "filters": {
            "and": [
                {
                    "field": "event",
                    "operator": "is",
                    "value": "EDGE_UP"
                }
            ]
        },
        "_count": True
    }
}

response = session.post(serverUrl,data=json.dumps(requestData))
results = response.json()['result']
EdgeUpEventsCount = results['count']
print("Edge Up Events Count: "+str(EdgeUpEventsCount))

outageEvents = []

for event in ["EDGE_UP","EDGE_DOWN","LINK_DEAD","LINK_ALIVE"]:
    print("Processing "+event+" events.")
    requestData = {
        "id": 23,
        "jsonrpc": "2.0",
        "method": "event/getEnterpriseEventsList",
        "params": {
            "sortBy": [
                {
                    "attribute": "eventTime",
                    "type": "DESC"
                }
            ],
            "enterpriseId": 1,
            "interval": interval,
            "filters": {
                "and": [
                    {
                        "field": "event",
                        "operator": "is",
                        "value": event
                    }
                ]
            }
        }
    }
    print(".")
    response = session.post(serverUrl,data=json.dumps(requestData))
    result = response.json()['result']
    events = result['data']
    outageEvents += events

    while result['metaData']['more'] == True:
        requestData = {
            "id": 23,
            "jsonrpc": "2.0",
            "method": "event/getEnterpriseEventsList",
            "params": {
                "sortBy": [
                    {
                        "attribute": "eventTime",
                        "type": "DESC"
                    }
                ],
                "enterpriseId": 1,
                "interval": interval,
                "filters": {
                    "and": [
                        {
                            "field": "event",
                            "operator": "is",
                            "value": event
                        }
                    ]
                },
                "nextPageLink": result['metaData']['nextPageLink']
            }
        }
        response = session.post(serverUrl,data=json.dumps(requestData))
        result = response.json()['result']
        events = result['data']
        outageEvents += events
        print(".")

#Remove duplicate entries

outageEvents = [dict(t) for t in {tuple(d.items()) for d in outageEvents}]  

outageEvents.sort(key = lambda x:x['eventTime'])

print("Total Collected Events: "+str(len(outageEvents)))

for event in outageEvents:
    if event['event'] == 'LINK_DEAD':
        print(json.dumps(event,sort_keys=True, indent=4))
        break
    
output_file = open(f'Edges_Outage_Report.csv', mode='w', newline='\n')
field_names = ['Edge','Outage Time','Recovery Time','Outage Duration']
csv_writer = csv.DictWriter(output_file, field_names, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
csv_writer.writeheader()

outageCounter = 0
for count,event in enumerate(outageEvents):
    if event['event'] == 'EDGE_DOWN':
        endOfEvent = False
        #print(json.dumps(event,sort_keys=True, indent=4))
        edge = event['edgeName']
        downTime = datetime.datetime.strptime(event['eventTime'],'%Y-%m-%dT%H:%M:%S.000Z')
        seeker = count
        while seeker < len(outageEvents):
            if outageEvents[seeker]['edgeName'] == edge and outageEvents[seeker]['event'] == 'EDGE_UP':
                endOfEvent = True
                upTime = datetime.datetime.strptime(outageEvents[seeker]['eventTime'],'%Y-%m-%dT%H:%M:%S.000Z')
                break
            else:
                seeker += 1
        if endOfEvent == True:
            outageCounter += 1
            delta = upTime - downTime

            csv_writer.writerow({
                'Edge': edge,
                'Outage Time': downTime.strftime("%m/%d/%Y %H:%M:%S"),
                'Recovery Time': upTime.strftime("%m/%d/%Y %H:%M:%S"),
                'Outage Duration': delta.total_seconds()
        })

            #print("Outage #"+str(outageCounter)+":\nEdge: "+str(edge)+"\nDown Time: "+downTime.strftime("%m/%d/%Y %H:%M:%S")+"\nUp Time: "+upTime.strftime("%m/%d/%Y %H:%M:%S")+"\nDuration: "+str(delta.total_seconds()/60)+" minutes\n")
        else:
            pass

print("Edges Outages Report ready.")

output_file = open(f'Links_Outage_Report.csv', mode='w', newline='\n')
field_names = ['Edge','Link','Interface','Outage Time','Recovery Time','Outage Duration']
csv_writer = csv.DictWriter(output_file, field_names, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
csv_writer.writeheader()

outageCounter = 0
for count,event in enumerate(outageEvents):
    if event['event'] == 'LINK_DEAD':
        endOfEvent = False
        #print(json.dumps(event,sort_keys=True, indent=4))
        edge = event['edgeName']
        linkInternalId = event['detail'].split('\"')[7]
        linkLogicalId = event['detail'].split('\"')[3]
        try:
            link = [e for e in links if e['internalId'] == linkInternalId][0]
            linkName = link['displayName']
            interface = link['interface']
        except:
            print(edge)
            edgeId = [e for e in edges if e['name']==edge][0]['id']
            edgeLinks = [l for l in links if l['edgeId'] == edgeId]
            print(json.dumps(edgeLinks,sort_keys=True, indent=4))
            print("logical ID: "+linkLogicalId)
            print("Internal ID: "+linkInternalId)
            linkName = '#N/A'
            interface = '#N/A'
        
        downTime = datetime.datetime.strptime(event['eventTime'],'%Y-%m-%dT%H:%M:%S.000Z')
        seeker = count
        while seeker < len(outageEvents):
            if outageEvents[seeker]['edgeName'] == edge and outageEvents[seeker]['event'] == 'LINK_ALIVE' and outageEvents[seeker]['detail'] == event['detail']:
                endOfEvent = True
                upTime = datetime.datetime.strptime(outageEvents[seeker]['eventTime'],'%Y-%m-%dT%H:%M:%S.000Z')
                break
            else:
                seeker += 1
        if endOfEvent == True:
            outageCounter += 1
            delta = upTime - downTime

            csv_writer.writerow({
                'Edge': edge,
                'Link': linkName,
                'Interface': interface,
                'Outage Time': downTime.strftime("%m/%d/%Y %H:%M:%S"),
                'Recovery Time': upTime.strftime("%m/%d/%Y %H:%M:%S"),
                'Outage Duration': delta.total_seconds()
        })

            #print("Outage #"+str(outageCounter)+":\nEdge: "+str(edge)+"\nDown Time: "+downTime.strftime("%m/%d/%Y %H:%M:%S")+"\nUp Time: "+upTime.strftime("%m/%d/%Y %H:%M:%S")+"\nDuration: "+str(delta.total_seconds()/60)+" minutes\n")
        else:
            pass

print("Link Outages Report ready.")
