from django.core.management.base import BaseCommand, CommandError
from networkanalyzer.network_apis import velocloud
import ipaddress, json
from django.conf import settings
from networkanalyzer.management.commands._private import load_velocloud_API_tokens
from networkanalyzer.models import Network, Site, Link, Edge, Ha, ModelJSONEncoder
class Command(BaseCommand):
    help = 'Saves the network report to a database'

    #def add_arguments(self, parser):
    #    parser.add_argument('lans', nargs='+', type=str)

    def handle(self, *args, **options):
        credentials = load_velocloud_API_tokens()
        for network in credentials:
            vcanalyzer = velocloud.VelocloudAPICaller(network)
            json_file_path = settings.BASE_DIR/"networkanalyzer"/"network_apis"/"sample_Velocloud_API_calls"/f"enterprises_{network['serverUrl']}.json"
            #enterprises = vcanalyzer.explore_enterprises()
            #with open(json_file_path, "w") as opf:
            #    json.dump(enterprises, opf, indent=4)
            with json_file_path.open('r') as opf:
                enterprises = json.load(opf)
            for enterprise in enterprises.values():
                edges = vcanalyzer.get_enterprise_edges(enterprise['id'])
                for edge in edges["result"]:
                    if len(edge["recentLinks"]) > 0:
                        assert 0, json.dumps(edge, indent=4)
                # The 'id' fields are being deleted, because id is assigned in a non-unique way by the Velocloud API

                for edge in edges['result']:
                    edge['site'].pop('id', None) #deleted the id fields of the site, if it exists
                    edge['site'] = Site.objects.create(**edge['site'])
                    linkobjs = []
                    for link in edge['recentLinks']:
                        link.pop('id', None) #deletes the id field if None
                        extant_links = Link.objects.filter(logicalId=link["logicalId"], internalId=link["internalId"])
                        if extant_links.exists():
                            print("el", extant_links)
                            extant_link = extant_links.get()
                            assert extant_link.internalId == link["internalId"], (extant_link.logicalId, link)
                            linkobjs.append(extant_link)
                        else:
                            lc = Link.objects.create(**link)
                            linkobjs.append(lc)
                    del edge['recentLinks']
                    edge.pop('id', None) #deletes the edge id field if present
                    ef = Edge.objects.filter(deviceId=edge['deviceId'], logicalId=edge['logicalId'], selfMacAddress=edge['selfMacAddress'])
                    if ef.exists():
                        ef = ef.first()
                        assert ef.serialNumber == edge['serialNumber'], (ef.logicalId, edge)
                    ec = Edge.objects.create(**edge)
                    ec.recentLinks.set(linkobjs)
                    ec.save()
