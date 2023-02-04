import json, requests, datetime
from requests.adapters import HTTPAdapter, Retry
retries = Retry(total=5, backoff_factor=1, status_forcelist=[ 502, 503, 504 ])

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

    def call(self, endpoint, params):
        request_data = {
            "jsonrpc": "2.0",
            "method": endpoint,
            "params": params,
            "id": 1
        }
        server_url = f'https://{self.network["serverUrl"]}/portal/'
        response = self.session.post(server_url, data=json.dumps(request_data))
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


    def get_enterprise_events_list(self, interval:list[datetime.datetime], enterpriseId: int, event:str):
        """Event can be, for instance, LINK_ALIVE, LINK_DEAD, EDGE_DOWN, EDGE_UP"""
        request_data = {
            "id": 10,
            "jsonrpc": "2.0",
            "method": "event/getEnterpriseEventsList",
            "params": {
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
        }
        server_url = f'https://{self.network["serverUrl"]}/portal/'
        response = self.session.post(server_url, data=json.dumps(request_data))
        assert response.status_code == 200
        return response.json()


    def get_enterprise_events(self, enterpriseId: int):
        """Event can be, for instance, LINK_ALIVE, LINK_DEAD, EDGE_DOWN, EDGE_UP"""
        request_data = {
            "id": 10,
            "jsonrpc": "2.0",
            "method": "event/getEnterpriseEvents",
            "params": {
                "enterpriseId": enterpriseId,
                "_count": True
            }
        }
        server_url = f'https://{self.network["serverUrl"]}/portal/'
        response = self.session.post(server_url, data=json.dumps(request_data))
        assert response.status_code == 200
        return response.json()


    def get_edge_events(self, enterpriseId: int, edge_id: int):
        """Event can be, for instance, LINK_ALIVE, LINK_DEAD, EDGE_DOWN, EDGE_UP"""
        request_data = {
            "id": 10,
            "jsonrpc": "2.0",
            "method": "event/getEnterpriseEvents",
            "params": {
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
        }
        server_url = f'https://{self.network["serverUrl"]}/portal/'
        response = self.session.post(server_url, data=json.dumps(request_data))
        assert response.status_code == 200
        return response.json()
