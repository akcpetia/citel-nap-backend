from django.core.management.base import BaseCommand, CommandError
from networkanalyzer.network_apis import velocloud
from networkanalyzer.management.commands._private import load_velocloud_API_tokens
import ipaddress, json
from django.conf import settings
from networkanalyzer.models import Network, Site, Link, Edge, Ha, ModelJSONEncoder
class Command(BaseCommand):
    help = 'Saves the network report to a database'

    def add_arguments(self, parser):
        parser.add_argument('--enterprise_ids', default=[1,2,3,4], type=int, nargs="+")
        parser.add_argument('--lans', default=["100.127.64.1/29", "100.99.98.1/29"], type=int, nargs="+")

    def handle(self, *args, **options):
        credentials = load_velocloud_API_tokens()

        all_hosts = set()
        for lan in options['lans']:
            ipn = ipaddress.IPv4Network(lan, False)
            all_hosts.update(str(ipx) for ipx in ipn)
        for network in credentials:
            vcanalyzer = velocloud.VelocloudAPICaller(network)
            json_file_path = settings.BASE_DIR/"networkanalyzer"/"network_apis"/"sample_Velocloud_API_calls"/f"enterprises_{network['serverUrl']}.json"
            #enterprises = vcanalyzer.explore_enterprises()
            #with open(json_file_path, "w") as opf:
            #    json.dump(enterprises, opf, indent=4)
            with json_file_path.open('r') as opf:
                enterprises = json.load(opf)
            for (id_str, enterprise) in enterprises.items():
                #nwy = vcanalyzer.call("/enterprise/getEnterpriseNetworkSegments", {"enterpriseId": enterprise['id']})
                # nwy = vcanalyzer.call("/network/getNetworkGatewayPools", {"networkId": 0})
                #nwy = vcanalyzer.call("/enterprise/getEnterpriseNetworkAllocations", {"enterpriseId": enterprise['id']})
                nwy = vcanalyzer.call("/enterprise/getEnterpriseRouteTable", {"enterpriseId": enterprise['id']})
                if len(nwy["results"]["recentLinks"]) > 0:
                    assert 0, json.dumps(nwy, indent=4)
