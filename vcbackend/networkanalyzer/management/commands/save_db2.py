from networkanalyzer.network_apis import velocloud
import json, collections
from django.conf import settings
from networkanalyzer.management.commands._private import load_velocloud_API_tokens, S3Command
from networkanalyzer.models import Network, Site, Link, Edge, Ha, ModelJSONEncoder, Database1, Database2, Database3

class Command(S3Command):
    help = 'Saves the network report to a database'

    def handle(self, *args, **options):
        # The S3 urls saved to are like s3://citel-nap/velocloud/db2/2023-2-6/1675714313.811725/device-{edge['site']['id']}.json
        (bucket, timestamp, date_now, credentials) = self.bucket_timestamp_date_now_credentials()
        s3_path = f"velocloud/db2/{date_now.year}-{date_now.month}-{date_now.day}/{timestamp}"
        for network in credentials:
            vcanalyzer = velocloud.VelocloudAPICaller(network)
            enterprises = vcanalyzer.explore_enterprises()
            for enterprise in enterprises.values():
                edges = vcanalyzer.get_enterprise_edges(enterprise['id'])
                for edge in edges["result"]:
                    by_edge = collections.defaultdict(list)
                    for link in edge["recentLinks"]:
                        by_edge[link['edgeId']].append(link)
                    for(edge_id, links_for_edge) in by_edge.items():
                        interfaces = set(link["interface"] for link in links_for_edge)
                        interface_type = list(set(f"{link['interface']}/{link['networkType']}" for link in links_for_edge))
                        db2 = Database2.objects.create(site_name=edge['site']['id'],
                                                       interface_name=','.join(interfaces),
                                                       interface_type=interface_type)
                        fileobj = bucket.Object(f"{s3_path}/device-{edge['site']['id']}.json")
                        fileobj.put(Body=json.dumps(db2.json(), cls=ModelJSONEncoder, indent=4).encode('UTF-8'))

