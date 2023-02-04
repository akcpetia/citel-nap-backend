from django.core.management.base import BaseCommand, CommandError
from networkanalyzer.network_apis import velocloud
from _private import load_velocloud_API_tokens
import ipaddress, json
from django.conf import settings
class Command(BaseCommand):
    help = 'Saves the network report to a database'

    def handle(self, *args, **options):
        credentials = load_velocloud_API_tokens()

        erts = []
        all_hosts = set()
        for lan in options['lans']:
            ipn = ipaddress.IPv4Network(lan, False)
            all_hosts.update(str(ipx) for ipx in ipn)
        for network in credentials:
            vcanalyzer = velocloud.VelocloudAPICaller(network)
            # Work in progress, thus the comments with the distinct
            # API endpoint paths are preserved
            #nwy = vcanalyzer.call("/network/getNetworkGatewayPools", {"networkId": 0})
            #nwy = vcanalyzer.call("/enterprise/getEnterpriseGatewayHandoff", {"enterpriseId": 1})
            nwy = vcanalyzer.call("/enterprise/getEnterpriseNetworkSegments", {"enterpriseId": 1})
            #gac = vcanalyzer.call("/enterprise/getEnterpriseNetworkAllocations", {"enterpriseId": 1})
            #ert = vcanalyzer.call("/enterprise/getEnterpriseRouteTable", {"enterpriseId": 1})
            erts.append(nwy)
        with open("nwp.json", "w") as opf:
            json.dump(erts, opf)
        assert 0, all_hosts
        for network in credentials:
            vcanalyzer = velocloud.VelocloudAPICaller(network)
            gac = vcanalyzer.call("/enterprise/getEnterpriseNetworkAllocations", {"enterpriseId": 1})
        for network in credentials:
            vcanalyzer = velocloud.VelocloudAPICaller(network)
            gac = vcanalyzer.call("/enterprise/getEnterpriseNetworkAllocations", {"enterpriseId": 1})
            assert 0, gac
            gad = vcanalyzer.get_enterprise_addresses()
            for result in gad['result']:
                if isinstance(result['address'], str) and result['address'] in all_hosts:
                    assert 0
        edges = vcanalyzer.get_enterprise_edges(1)
