from django.core.management.base import BaseCommand, CommandError
from networkanalyzer.network_apis import velocloud
import ipaddress, json, collections
from django.conf import settings
from networkanalyzer.management.commands._private import load_velocloud_API_tokens
from networkanalyzer.models import Network, Site, Link, Edge, Ha, ModelJSONEncoder, Database1, Database2, Database3
class Command(BaseCommand):
    help = 'Saves the network report to a database'

    def handle(self, *args, **options):
        #TODO DB3 still not ready!
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
                    #edger = vcanalyzer.call("edge/getEdge", {"edgeId": edge['id'], "enterpriseId": enterprise['id'], "with": vcanalyzer.default_fields_to_request})
                    if len(edge["recentLinks"]) > 0:
                        by_edge = collections.defaultdict(list)
                        #if len(edge["recentLinks"])>1:
                        #    assert 0, json.dumps(edge, indent=4)
                        for link in edge["recentLinks"]:
                            #assert 0, json.dumps(edge, indent=4)
                            by_edge[link['edgeId']].append(link)
                        for(edge_id, links_for_edge) in by_edge.items():
                            interfaces = set(link["interface"] for link in links_for_edge)
                            modes = set(link.get("linkMode") for link in links_for_edge)
                            interface_type = set(f"{link['interface']}/{link['networkType']}" for link in links_for_edge)
                            db1 = Database1.objects.create(site_name=edge['site']['id'],
                                                           interface_name=','.join(interfaces),
                                                           link_name=edge_id,
                                                           link_mode=','.join(modes),
                                                           number_of_interfaces=len(interfaces))
                            db2 = Database2.objects.create(site_name=edge['site']['id'],
                                                           interface_name=','.join(interfaces),
                                                           interface_type=interface_type)
                            events1 = vcanalyzer.get_enterprise_events(enterprise['id'])
                            events2 = vcanalyzer.get_edge_events(enterprise['id'], edge['id'])
                            # continuing by here on Monday
                            db3 = Database3.objects.create(site_name=edge['site']['id'],
                                                           interface_name=','.join(interfaces),
                                                           event_type=None, outage_duration=None, outage_data=None)

