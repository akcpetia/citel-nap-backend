import dateutil.parser

from networkanalyzer.network_apis import velocloud
import json, collections, re
from networkanalyzer.management.commands._private import load_velocloud_API_tokens, S3Command
from networkanalyzer.models import Network, Site, Link, Edge, Ha, ModelJSONEncoder, Database3

regexps = {"LINK": re.compile("Link (.*) is (no longer|now) DEAD")}

def event_time_and_type(event):
    eventdatetime = dateutil.parser.parse(event['eventTime'])
    #Sometimes, DEAD and ALIVE events are registered in the same time, eg. '2023-02-07T14:03:15.000Z',
    # so that, it seems that the events are registered at a granularity of seconds, then
    # a second sorting key has to be used to compare the event, where DEAD
    # evaluates lower than ALIVE
    if event['event'].endswith("_DEAD"):
        dead_or_alive_key = 0
    else:
        # event should end with _ALIVE
        dead_or_alive_key = 1
    return (eventdatetime, dead_or_alive_key)


class Command(S3Command):
    help = 'Saves the network report to a database'

    def handle_events_set_grouped_by_event_type(self, s3_path, bucket, edge, by_event_type):
        if len(by_event_type) > 0:
            for subject in ("EDGE_INTERFACE", "LINK"):
                dead_name = f"{subject}_DEAD"
                alive_name = f"{subject}_ALIVE"
                if dead_name in by_event_type and alive_name in by_event_type:
                    dead_links = collections.defaultdict(list)
                    alive_links = collections.defaultdict(list)
                    for event in by_event_type[dead_name]:
                        link_re_match = regexps[subject].match(event['message'])
                        link_type = link_re_match.group(1)
                        identifier = (event['edgeName'], link_type)
                        dead_links[identifier].append(event)
                    for event in by_event_type[alive_name]:
                        link_re_match = regexps[subject].match(event['message'])
                        link_type = link_re_match.group(1)
                        identifier = (event['edgeName'], link_type)
                        alive_links[identifier].append(event)
                    matched_links = set(dead_links.keys()) & set(alive_links.keys())
                    if len(matched_links):
                        for matched_link in matched_links:
                            (store_id, link_type) = matched_link
                            alives = alive_links[matched_link]
                            deads = dead_links[matched_link]
                            all_events = alives + deads
                            all_events.sort(key=event_time_and_type)
                            death_s = None
                            for (ievent, event) in enumerate(all_events):
                                if event['event'] == dead_name:
                                    if ievent % 2 != 0:
                                        # assert 0
                                        pass  # check that the event 0-based index is even
                                    death_s = [event]
                                elif event['event'] == alive_name:
                                    if death_s is None:
                                        continue  # alive event came first
                                        # later we will need to match all events,
                                        # but for now, leaving it is OK
                                    assert len(death_s) == 1  # checks that only 1 dead event is found before an alive event
                                    death_datetime = dateutil.parser.parse(death_s[0]['eventTime'])
                                    revival_datetime = dateutil.parser.parse(event['eventTime'])
                                    down_duration = revival_datetime - death_datetime
                                    outage_data = json.dumps([death_s[0], event])
                                    db3 = Database3.objects.create(site_name=edge['site']['id'], interface_name=link_type, event_type=dead_name,
                                                                   outage_duration=down_duration, outage_data=outage_data)
                                    death_s = None
                                    fileobj = bucket.Object(f"{s3_path}/alive-event-{event['id']}.json")
                                    fileobj.put(Body=json.dumps(db3.json(), cls=ModelJSONEncoder, indent=4).encode('UTF-8'))

    def handle(self, *args, **options):
        #The S3 urls saved to are like s3://citel-nap/velocloud/db3/2023-2-6/1675714313.811725/alive-event-{event['id']}.json
        (bucket, timestamp, date_now, credentials) = self.bucket_timestamp_date_now_credentials()
        s3_path = f"velocloud/db3/{date_now.year}-{date_now.month}-{date_now.day}/{timestamp}"
        for network in credentials:
            vcanalyzer = velocloud.VelocloudAPICaller(network)
            enterprises = vcanalyzer.explore_enterprises()
            for enterprise in enterprises.values():
                edgesv1 = vcanalyzer.get_enterprise_edges(enterprise['id'])
                for edge in edgesv1["result"]:
                    edge_events = vcanalyzer.get_edge_events(enterprise['id'], edge['id'])
                    by_event_type = collections.defaultdict(list)
                    for event in edge_events['result']['data']:
                        by_event_type[event['event']].append(event)
                    if edge_events['result']['metaData']['more']:
                        pag = f"/enterprises/{enterprise['logicalId']}/events?nextPageLink={edge_events['result']['metaData']['nextPageLink']}"
                        while True:
                            eventsv2 = vcanalyzer.call_v2(pag, {})
                            for event in eventsv2["data"]:
                                by_event_type[event['event']].append(event)
                            if eventsv2['metaData']["more"]:
                                pag = f"/enterprises/{enterprise['logicalId']}/events?nextPageLink={eventsv2['metaData']['nextPageLink']}"
                            else:
                                break
                    self.handle_events_set_grouped_by_event_type(s3_path, bucket, edge, by_event_type)