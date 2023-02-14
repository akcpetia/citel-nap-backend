from django.core.management.base import BaseCommand, CommandError
from networkanalyzer.network_apis import velocloud
from _private import load_velocloud_API_tokens
import ipaddress, json
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
            nwy = vcanalyzer.call("/enterprise/getEnterpriseNetworkSegments", {"enterpriseId": 1})
            erts.append(nwy)
        with open("getEnterpriseNetworkSegments.json", "w") as opf:
            json.dump(erts, opf)
        for network in credentials:
            vcanalyzer = velocloud.VelocloudAPICaller(network)
            gac = vcanalyzer.call("/enterprise/getEnterpriseNetworkAllocations", {"enterpriseId": 1})
            gad = vcanalyzer.get_enterprise_addresses()
            for result in gad['result']:
                if isinstance(result['address'], str) and result['address'] in all_hosts:
                    assert 0
