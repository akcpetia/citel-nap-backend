from django.core.management.base import BaseCommand, CommandError
from networkanalyzer.network_apis import velocloud
import ipaddress, json, collections, datetime
from django.conf import settings
from networkanalyzer.management.commands._private import load_velocloud_API_tokens
from networkanalyzer.models import Network, Site, Link, Edge, Ha, ModelJSONEncoder, Database1, Database2, Database3
import boto3
class Command(BaseCommand):
    help = 'Saves the network report to a database'

    def handle(self, *args, **options):
        credentials = load_velocloud_API_tokens()
        date_now = datetime.datetime.now()
        timestamp = date_now.timestamp()
        s3 = boto3.resource('s3')
        bucket = s3.Bucket('citel-nap')
        s3_path = f"velocloud/db1/{date_now.year}-{date_now.month}-{date_now.day}/{timestamp}"
        for network in credentials:
            vcanalyzer = velocloud.VelocloudAPICaller(network)
            json_file_path = settings.BASE_DIR/"networkanalyzer"/"network_apis"/"sample_Velocloud_API_calls"/f"enterprises_{network['serverUrl']}.json"
            with json_file_path.open('r') as opf:
                enterprises = json.load(opf)
            for enterprise in enterprises.values():
                edges = vcanalyzer.get_enterprise_edges(enterprise['id'])
                for edge in edges["result"]:
                    #edger = vcanalyzer.call("edge/getEdge", {"edgeId": edge['id'], "enterpriseId": enterprise['id'], "with": vcanalyzer.default_fields_to_request})
                    if len(edge["recentLinks"]) > 0:
                        by_edge = collections.defaultdict(list)
                        for link in edge["recentLinks"]:
                            by_edge[link['edgeId']].append(link)
                        for(edge_id, links_for_edge) in by_edge.items():
                            interfaces = set(link["interface"] for link in links_for_edge)
                            modes = set(link.get("linkMode", "unknown") for link in links_for_edge)
                            db1 = Database1.objects.create(site_name=edge['site']['id'],
                                                           interface_name=','.join(interfaces),
                                                           link_name=edge_id,
                                                           link_mode=','.join(modes),
                                                           number_of_interfaces=len(interfaces))
                            fileobj = bucket.Object(f"{s3_path}/device-{edge['site']['id']}.json")
                            db1dict = db1.json()
                            fileobj.put(Body=json.dumps(db1dict, cls=ModelJSONEncoder, indent=4).encode('UTF-8'))



