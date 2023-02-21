import requests
import json
import common

serverUrl = 'https://van-th-orch-prod.radiant.net/portal/'
session = requests.Session()
session.headers.update({'Content-Type': 'application/json','Authorization': 'Token ' + common.token})

requestData1 = {"jsonrpc":"2.0","method":"enterprise/getEnterpriseEdges","params":{"id": 1,"enterpriseId": 1,"with": ["site"]},"id":1}
response = session.post(serverUrl,data=json.dumps(requestData1))
requestResult1 = response.json()['result']

with open('TH_Link_Report.csv','w') as file:
    counter = 0
    file.write("Edge Name,Model Number,Serial Number, Status, Activation Date, Link Name, Link Mode, Link State, Last Active, IP Address, DL (Mbps), UL (Mbps), DL (MB), UL (MB)\n")
    for edge in requestResult1:
        #file.write(str(edge['id'])+","+edge['name']+","+ str(edge['modelNumber'])+","+ str(edge['serialNumber'])+","+edge['edgeState'] +","+edge['activationTime'].replace('T',' ').replace('Z','') +'\n')
        edgeId = edge['id']
        requestData2 = {"jsonrpc":"2.0","method":"metrics/getEdgeLinkMetrics","params":{"enterpriseId": 1,"edgeId": edgeId,"interval": {"start": 1662004800000,"end": 1664596800000}},"id":1}
        response = session.post(serverUrl,data=json.dumps(requestData2))
        # print(response.json())
        requestResult2 = response.json()['result']
        for link in requestResult2:
            file.write(edge['name']+","+ str(edge['modelNumber'])+","+ str(edge['serialNumber'])+","+edge['edgeState'] +","+edge['activationTime'].replace('T',' ').replace('Z','') +","+link["link"]["displayName"]+","+link["link"]["linkMode"]+","+link['state']+","+link['link']['lastActive'].replace('T',' ').replace('Z','')+","+link['link']['ipAddress']+","+str(link["bpsOfBestPathRx"]/10**6)+","+str(link["bpsOfBestPathTx"]/10**6)+","+str(link['bytesRx']/10**6)+","+str(link['bytesTx']/10**6)+'\n')
            counter += 1
            print(str(counter) + " links processed.")
    print("Processing completed.")