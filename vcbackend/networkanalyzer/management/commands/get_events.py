import collections, json
from networkanalyzer.network_apis import velocloud
from networkanalyzer.management.commands._private import load_velocloud_API_tokens, S3Command
from networkanalyzer.models import Network, Site, Link, Edge, Ha, ModelJSONEncoder, RDSEdge, Event


def total_bytes_and_apps_list(apps_list):
    total_bytes = sum(app['totalBytes'] for app in apps_list)
    return {"total_bytes": total_bytes, "apps": apps_list}


class Command(S3Command):
    help = 'Saves the network report to a database'
    totaller_fields = ('bytesTx', 'bytesRx', 'bpsOfBestPathRx', 'bpsOfBestPathTx', 'totalBytes')

    def add_arguments(self, parser):
        parser.add_argument('interval_last_seconds', nargs='?', type=int, default=3600)
        parser.add_argument('num_top_apps', nargs='?', type=int, default=10)


    def get_metrics_and_save_secondary_data(self, vcanalyzer, bucket, enterprise, edge, date_now, timestamp, interval):
        elm_s3_path = f"velocloud/edge_link_metrics/{date_now.year}-{date_now.month}-{date_now.day}/{timestamp}"
        elsm_s3_path = f"velocloud/edge_link_status_metrics/{date_now.year}-{date_now.month}-{date_now.day}/{timestamp}"
        ealm_s3_path = f"velocloud/edge_app_link_metrics/{date_now.year}-{date_now.month}-{date_now.day}/{timestamp}"
        eam_s3_path = f"velocloud/edge_app_metrics/{date_now.year}-{date_now.month}-{date_now.day}/{timestamp}"

        linkms = vcanalyzer.get_edge_link_metrics(enterprise['id'], edge['id'], interval)
        linkas = vcanalyzer.get_edge_app_metrics(enterprise['id'], edge['id'], interval)
        linkss = vcanalyzer.get_edge_status_metrics(enterprise['id'], edge['id'])
        linkals = vcanalyzer.get_edge_app_link_metrics(enterprise['id'], edge['id'], interval)
        save_dict(bucket, f"{elm_s3_path}/edge-{edge['id']}.json", linkms['result'])
        save_dict(bucket, f"{elsm_s3_path}/edge-{edge['id']}.json", linkss['result'])
        save_dict(bucket, f"{ealm_s3_path}/edge-{edge['id']}.json", linkals['result'])
        save_dict(bucket, f"{eam_s3_path}/edge-{edge['id']}.json", linkas['result'])
        return (linkms, linkas, linkss, linkals)


    def process_link(self, link):
        """Processes a link, returning a Link object"""
        link.pop('id', None)  # deletes the id field if None
        extant_links = Link.objects.filter(logicalId=link["logicalId"], internalId=link["internalId"])
        if extant_links.exists():
            extant_link = extant_links.get()
            assert extant_link.internalId == link["internalId"], (extant_link.logicalId, link)
            return extant_link
        else:
            lc = Link.objects.create(**link)
            return lc

    def save_edge_to_db(self, edge):
        # The edge 'id' fields are being deleted, because id is assigned in a non-unique way by the Velocloud API
        edge['edgeId'] = edge.pop('id', None)  # deletes the edge id field if present
        site_id_finds = Site.objects.filter(id=edge['site']['id'])
        if site_id_finds.exists():
            edge['site'] = site_id_finds.get()
        else:
            edge['site'] = Site.objects.create(**edge['site'])

        for link in edge['recentLinks']:
            self.process_link(link)
        edge.pop('recentLinks')
        #klass = Edge
        klass = RDSEdge
        new_edge = {}
        for (key, value) in edge.items():
            new_key = key.lower().replace("_", "")
            new_edge[new_key] = value
        #edge_find = klass.objects.filter(activationKey=edge['activationKey'])
        edge_find = klass.objects.filter(activationkey=new_edge['activationkey'])
        if edge_find.exists():
            edgeobj = edge_find.get()
        else:
            print("created")
            edgeobj = klass.objects.create(**edge)
        edgeobj.save()
        return edgeobj

    def get_or_create_edge(self, edge_dict):
        finder = RDSEdge.objects.filter(logicalid=edge_dict['logicalId'], enterpriseid=edge_dict['enterpriseId'])
        if finder.exists():
            return finder.first()
        else:
            raise Exception("This edge object should be in the database")

    def handle(self, *args, **options):
        edges_cnt = 0
        (bucket, timestamp, date_now, credentials) = self.bucket_timestamp_date_now_credentials()

        # that data should be converted to app parameters later
        for network in credentials:
            vcanalyzer = velocloud.VelocloudAPICaller(network)
            enterprises = vcanalyzer.explore_enterprises()
            for enterprise in enterprises.values():
                edges = vcanalyzer.get_enterprise_edges(enterprise['id'])
                for edge in edges['result']:
                    edge_events = vcanalyzer.get_edge_events(enterprise['id'], edge['id'])
                    if len(edge_events["result"]["data"])>0:
                        for event in edge_events["result"]["data"]:
                            event_finder = Event.objects.filter(id=event['id'])
                            if not event_finder.exists():
                                eo = Event.objects.create(**event)
                                eo.save()




def save_dict(bucket, path, obj):
    fileobj = bucket.Object(path)
    fileobj.put(Body=json.dumps(obj, cls=ModelJSONEncoder, indent=4).encode('UTF-8'))
