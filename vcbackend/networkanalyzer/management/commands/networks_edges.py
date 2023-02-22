import collections, json
from networkanalyzer.network_apis import velocloud
from networkanalyzer.management.commands._private import load_velocloud_API_tokens, S3Command
from networkanalyzer.models import Network, Site, Link, Edge, Ha, ModelJSONEncoder, RDSEdge


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
        linkms = vcanalyzer.get_edge_link_metrics(enterprise['id'], edge['edgeId'], interval)
        linkas = vcanalyzer.get_edge_app_metrics(enterprise['id'], edge['edgeId'], interval)
        linkss = vcanalyzer.get_edge_status_metrics(enterprise['id'], edge['edgeId'])
        linkals = vcanalyzer.get_edge_app_link_metrics(enterprise['id'], edge['edgeId'], interval)
        save_dict(bucket, f"{elm_s3_path}/edge-{edge['edgeId']}.json", linkms['result'])
        save_dict(bucket, f"{elsm_s3_path}/edge-{edge['edgeId']}.json", linkss['result'])
        save_dict(bucket, f"{ealm_s3_path}/edge-{edge['edgeId']}.json", linkals['result'])
        save_dict(bucket, f"{eam_s3_path}/edge-{edge['edgeId']}.json", linkas['result'])
        return (linkms, linkas, linkss, linkals)


    def process_link(self, link, edgeId):
        """Processes a link, returning a Link object"""
        link.pop('id', None)  # deletes the id field if None
        link['edgeId'] = edgeId
        extant_links = Link.objects.filter(logicalId=link["logicalId"], internalId=link["internalId"])
        if extant_links.exists():
            extant_link = extant_links.get()
            extant_link.edgeId = edgeId
            extant_link.save()
            assert extant_link.internalId == link["internalId"], (extant_link.logicalId, link)
            return extant_link
        else:
            lc = Link.objects.create(**link)
            return lc

    def save_edge_to_db(self, edge):
        # The edge 'id' fields are being deleted, because id is assigned in a non-unique way by the Velocloud API
        edge['edgeId'] = edge.pop('id', None)  # deletes the edge id field if present
        if 'site' in edge:
            site_id_finds = Site.objects.filter(id=edge['site']['id'])
            if site_id_finds.exists():
                edge['site'] = site_id_finds.get()
            else:
                edge['site'] = Site.objects.create(**edge['site'])

        recent_links = edge.pop('recentLinks', None)#pops the recentLinks edge item, if it exists
        if recent_links is not None:
            for link in recent_links:
                self.process_link(link, edge['edgeId'])

        klass = RDSEdge
        new_edge = {}
        for (key, value) in edge.items():
            new_key = key.lower().replace("_", "")
            new_edge[new_key] = value
        if 'site' in new_edge:
            new_edge["site_id"] = new_edge.pop("site").id
        edge_find = klass.objects.filter(logicalid=new_edge['logicalid'])
        if edge_find.exists():
            edgeobj = edge_find.first()
        else:
            print("created")
            edgeobj = klass.objects.create(**new_edge)
        edgeobj.save()
        return edgeobj

    def handle_edge(self, edge, enterprise, vcanalyzer, bucket, date_now, timestamp, interval, options):
        edgeobj = self.save_edge_to_db(edge)
        try:
            health_dict = vcanalyzer.call_v2(f"/enterprises/{enterprise['logicalId']}/edges/{edge['logicalId']}/healthStats", {})
        except:
            # does not save health node for this edge for now
            health_dict = None
        edge['health'] = json.dumps(health_dict)
        s3_path = f"velocloud/edges/{date_now.year}-{date_now.month}-{date_now.day}/{timestamp}"
        link_states_count = collections.Counter()
        if "recentLinks" in edge:
            for link in edge['recentLinks']:
                link_states_count[link['state']] += 1

        edge_states_count = collections.Counter()
        edge_models_count = collections.Counter()
        (linkms, linkas, linkss, linkals) = self.get_metrics_and_save_secondary_data(vcanalyzer, bucket, enterprise, edge, date_now, timestamp, interval)

        edge_states_count[edge['edgeState']] += 1
        edge_models_count[edge['modelNumber']] += 1
        elm_summary = {fld: 0 for fld in self.totaller_fields}
        for result in linkms['result']:
            for fld in self.totaller_fields:
                elm_summary[fld] += result[fld]
        assert elm_summary['totalBytes'] == (elm_summary['bytesTx'] + elm_summary['bytesRx'])
        # in the "veloCloud Portal GUI - API Calls per Dataset.pdf" document, item 5, it says
        # 'totalBytesRx' and 'totalBytesTx' as field names, but the data fields are not accessible
        # through that names, indeed, they are 'bytesRx' and 'bytesTx'

        # Calculates the average throughputs
        elm_summary['bytesTxThroughput'] = elm_summary['bytesTx'] / options['interval_last_seconds']
        elm_summary['bytesRxThroughput'] = elm_summary['bytesRx'] / options['interval_last_seconds']
        elm_summary['totalBytesThroughput'] = elm_summary['totalBytes'] / options['interval_last_seconds']
        eam_apps_by_category = collections.defaultdict(list)
        eam_apps_by_category_totalized = {}
        eam_apps = sorted(linkas['result'], key=lambda x: x['totalBytes'], reverse=True)
        for eam_app in eam_apps:
            eam_apps_by_category[eam_app['category']].append(eam_app)
        for (category, eam_category) in eam_apps_by_category.items():
            eam_apps_by_category_totalized[category] = total_bytes_and_apps_list(eam_category)
        eam_data = {"top_apps": total_bytes_and_apps_list(eam_apps[0:options['num_top_apps']]),
                    "apps_by_category": eam_apps_by_category_totalized}

        edge["summary"] = dict(edge_states_count=edge_states_count,
                                       edge_models_count=edge_models_count,
                                       link_states_count=link_states_count,
                                       edge_apps_metrics=eam_data, edge_link_metrics=elm_summary)
        edgeobj.summary = edge["summary"]
        edgeobj.save()
        save_dict(bucket, f"{s3_path}/edge-{edge['edgeId']}.json", edge)
        self.edges_cnt+=1
        print("Edges processed:", self.edges_cnt)

    def handle(self, *args, **options):
        self.edges_cnt = 0
        (bucket, timestamp, date_now, credentials) = self.bucket_timestamp_date_now_credentials()

        # that data should be converted to app parameters later
        interval = velocloud.last_X_seconds(options['interval_last_seconds'])
        for network in credentials:
            vcanalyzer = velocloud.VelocloudAPICaller(network)
            enterprises = vcanalyzer.explore_enterprises()
            for enterprise in enterprises.values():
                edges = vcanalyzer.get_enterprise_edges(enterprise['id'])
                events = vcanalyzer.get_enterprise_events(enterprise['id'], interval)
                severities_cnt = collections.Counter(evt['severity'] for evt in events['result']['data'])
                if events['result']['metaData']['more']:
                    next_page_link = events['result']['metaData']['nextPageLink']
                    while True:
                        cv2 = vcanalyzer.call_v2(f"/enterprises/{enterprise['logicalId']}/events?nextPageLink={next_page_link}", {})
                        for edge in cv2['data']:
                            self.handle_edge(edge, enterprise, vcanalyzer, bucket, date_now, timestamp, interval, options)
                        severities_cnt.update(evt['severity'] for evt in cv2['data'])
                        if cv2['metaData']['more']:
                            next_page_link = cv2['metaData']['nextPageLink']
                        else:
                            break
                #TODO to save the severities count
                for edge in edges['result']:
                    self.handle_edge(edge, enterprise, vcanalyzer, bucket, date_now, timestamp, interval, options)



def save_dict(bucket, path, obj):
    fileobj = bucket.Object(path)
    fileobj.put(Body=json.dumps(obj, cls=ModelJSONEncoder, indent=4).encode('UTF-8'))
