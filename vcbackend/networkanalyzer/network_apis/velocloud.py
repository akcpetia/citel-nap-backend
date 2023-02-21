import json, requests, datetime, typing
from requests.adapters import HTTPAdapter, Retry
retries = Retry(total=5, backoff_factor=1, status_forcelist=[ 502, 503, 504 ])

def last_X_seconds(X):
    dtnow = datetime.datetime.now()
    interval = datetime.timedelta(seconds=X)
    dtthen = dtnow - interval
    return {"start": int(dtthen.timestamp()*1000), "end": int(dtnow.timestamp()*1000)}
class VelocloudAPICaller:
    """Handles the API calls for a specific Velocloud network"""
    default_fields_to_request = [
        "recentLinks",
        "state",
        "site",
        "ha",
        "vnfs",
        "isSoftwareVersionSupportedByVco"
    ]
    def __init__(self, network):

        self.network = network #Saves the network data for later use
        #Creates a Request session with authorization headers and a HTTP adapter for the specified Velocloud network
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json', 'Authorization': 'Token ' + network['token']})
        self.session.mount('https://', HTTPAdapter(max_retries=retries))

    def get_enterprise_addresses(self, enterpriseId=1):
        return self.call("enterprise/getEnterpriseAddresses", {"enterpriseId": enterpriseId})

    def call(self, endpoint, params, id: int=1, filters=None):
        request_data = {
            "jsonrpc": "2.0",
            "method": endpoint,
            "params": params,
            "id": id
        }
        if filters:
            request_data['filters'] = filters
        server_url = f'https://{self.network["serverUrl"]}/portal/'
        response = self.session.post(server_url, data=json.dumps(request_data))
        assert response.status_code == 200
        return response.json()

    def call_v2(self, endpoint, params):
        # Makes a call to ApiV2
        server_url = f'https://{self.network["serverUrl"]}/sdwan{endpoint}'
        response = self.session.get(server_url)
        assert response.status_code == 200
        return response.json()

    def explore_enterprises(self, to_id=1000, missing_enterprises_tolerance=20):
        """Explores the enterprises by ID, trying from range 1 to {to_id}, but stopping when {missing_enterprises_tolerance} have not been found"""
        enterprises = {}
        last_successful_id = 0
        for enterprise_id in range(1, to_id + 1):
            enterprise_info = self.call("/enterprise/getEnterprise", {"enterpriseId": enterprise_id})
            if "error" in enterprise_info:
                # normally I have found error responses like:
                # {'jsonrpc': '2.0', 'error': {'code': -32603, 'message': 'unable to find enterprise for operator enterprise context'}, 'id': '/enterprise/getEnterprise'}
                if (enterprise_id - last_successful_id) >= missing_enterprises_tolerance:
                    break
            else:
                last_successful_id = enterprise_info["result"]["id"]
                enterprises[last_successful_id] = enterprise_info["result"]
        return enterprises

    def get_enterprise_edges(self, enterpriseId):

        request_params = {
            "with": self.default_fields_to_request,
            "enterpriseId": enterpriseId,
        }
        return self.call("enterprise/getEnterpriseEdges", request_params)

    def get_enterprise_edges_v2(self, enterprise):
        return self.call_v2(f"/enterprises/{enterprise['logicalId']}/edges", {})

    def get_edge(self, enterpriseId, edgeId):
        request_params = {
            "enterpriseId": enterpriseId,
            "edgeId": edgeId,
        }
        return self.call("enterprise/getEnterpriseEdges", request_params)

    def get_enterprise_edges_list(self, enterpriseId):
        request_params = {
            "with": self.default_fields_to_request,
            "enterpriseId": enterpriseId,
        }
        return self.call("enterprise/getEnterpriseEdgesList", request_params)

    def get_enterprise_edges_by_state(self, enterpriseId:int, state:str):
        request_params = {
            "with": self.default_fields_to_request,
            "filters": {
                "and": [
                    {
                        "field": "edgeState",
                        "operator": "is",
                        "value": state
                    }
                ]
            },
            "enterpriseId": enterpriseId,
        }
        return self.call("enterprise/getEnterpriseEdges", request_params)


    def get_enterprise_events_list(self, interval:typing.List[datetime.datetime], enterpriseId: int, event:str):
        """Event can be, for instance, LINK_ALIVE, LINK_DEAD, EDGE_DOWN, EDGE_UP"""
        request_params = {
                "enterpriseId": enterpriseId,
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
                "_count": True
            }
        call1 = self.call("event/getEnterpriseEventsList", request_params, id=1)
        call2 = self.call("event/getEnterpriseEventsList", request_params, id=10)
        return self.call("event/getEnterpriseEventsList", request_params)


    def get_enterprise_events(self, enterpriseId: int, interval: dict):
        """Event can be, for instance, LINK_ALIVE, LINK_DEAD, EDGE_DOWN, EDGE_UP"""
        request_params = {
            "enterpriseId": enterpriseId,
            "interval": interval,
            "_count": True
        }
        return self.call("event/getEnterpriseEvents", params=request_params, id=10)


    def get_edge_events(self, enterpriseId: int, edge_id: int):
        """Event can be, for instance, LINK_ALIVE, LINK_DEAD, EDGE_DOWN, EDGE_UP"""
        request_params = {
            "enterpriseId": enterpriseId,
            "filters": {
                "and": [
                    {
                        "field": "edgeId",
                        "operator": "is",
                        "value": edge_id
                    }
                ]
            },
            "_count": True
        }
        return self.call("event/getEnterpriseEvents", request_params, id=10)


    def get_edge_link_metrics(self, enterpriseId: int, edge_id: int, interval: dict):
        request_params = {
            "enterpriseId": enterpriseId,
            "edgeId": edge_id,
            "interval": interval,
            "_count": True
        }
        return self.call("metrics/getEdgeLinkMetrics", request_params, id=10)

    def get_edge_status_metrics(self, enterpriseId: int, edge_id: int):
        request_params = {
            "enterpriseId": enterpriseId,
            "edgeId": edge_id,
            "_count": True
        }
        return self.call("metrics/getEdgeStatusMetrics", request_params, id=10)


    def get_edge_app_link_metrics(self, enterpriseId: int, edge_id: int, interval: dict):
        request_params = {
            "enterpriseId": enterpriseId,
            "id": edge_id,
            "interval": interval,
            "_count": True
        }
        return self.call("metrics/getEdgeAppLinkMetrics", request_params, id=10)

    def get_edge_app_metrics(self, enterpriseId: int, edge_id: int, interval: dict):
        request_params = {
            "enterpriseId": enterpriseId,
            "id": edge_id,
            "interval": interval,
            "_count": True
        }
        return self.call("metrics/getEdgeAppMetrics", request_params, id=10)
