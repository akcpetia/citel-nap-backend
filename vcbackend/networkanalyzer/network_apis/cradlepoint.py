import json, requests, datetime
from requests.adapters import HTTPAdapter, Retry

class CradlepointAPICaller:
    """Handles the API calls for a specific Velocloud network"""
    def __init__(self, network):

        self.network = network #Saves the network data for later use
        #Creates a Request session with authorization headers and a HTTP adapter for the specified Velocloud network
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json', 'Authorization': 'Token ' + network['token']})
        self.session.mount('https://', HTTPAdapter(max_retries=retries))
