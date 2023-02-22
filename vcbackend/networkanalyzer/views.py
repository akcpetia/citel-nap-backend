from django.shortcuts import render
from django.conf import settings
import dotenv, boto3, datetime, re, io, json

# Create your views here.
from django.contrib.auth.models import User
from rest_framework import viewsets, permissions, response
from networkanalyzer.serializers import UserSerializer, EdgeSerializer, RDSEdgeSerializer, SiteSerializer
from networkanalyzer.serializers import DeviceSerializer, LinkSerializer, Database3Serializer, EventSerializer
from networkanalyzer.models import Edge, RDSEdge, Site, Device, Link, Database3, Event
from rest_framework_jwt.authentication import JSONWebTokenAuthentication


def merge_in_site_info(data_dict, site):
    sitejs = site.dict()
    for (siteprop, siteprop_value) in sitejs.items():
        if siteprop not in ('id', 'created', 'name', 'modified', 'logicalId'):
            data_dict[siteprop] = siteprop_value
    data_dict['site'] = None


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class RDSEdgesViewSet(viewsets.ModelViewSet):
    queryset = RDSEdge.objects.all()
    serializer_class = RDSEdgeSerializer
    permission_classes = [permissions.IsAuthenticated]

    # we need a filter on siteid for edges and links
    def retrieve(self, request, pk=None):
        qs = self.get_queryset()
        element = qs.filter(pk=pk).get()
        site = Site.objects.get(id=element.site_id)
        eljs = element.dict()
        merge_in_site_info(eljs, site)
        eljs['supportTickets'] = {'open': 0, 'minor': 0, 'request': 0}
        eljs['processedDays'] = 1 #TODO put this value based in the processed days
        return response.Response(data=eljs)

    def list(self, request, pk=None):
        qs = self.get_queryset()
        filter_params = {}
        if pk is not None:
            filter_params['id'] = pk
        siteId = self.request.query_params.get('siteId')
        if siteId:
            filter_params['siteId'] = siteId
        if len(filter_params) > 0:
            qs = qs.filter(**filter_params)

        fqs = self.filter_queryset(qs)
        page = self.paginate_queryset(fqs)

        serializer = self.get_serializer(page, many=True)
        for element in serializer.data:
            site = Site.objects.get(id=element['site'])
            merge_in_site_info(element, site)
            element['supportTickets'] = {'open': 0, 'minor': 0, 'request': 0}
            element['processedDays'] = 1  # TODO put this value based in the processed days
        return self.get_paginated_response(serializer.data)

class EdgesViewSet(viewsets.ModelViewSet):
    # this class should no longer be used, because we are using now an updated database table
    queryset = Edge.objects.all()
    serializer_class = EdgeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, pk=None):
        qs = self.get_queryset()
        filter_params = {}
        if pk is not None:
            filter_params['id'] = pk
        siteId = self.request.query_params.get('siteId')
        if siteId:
            filter_params['siteId'] = siteId
        if len(filter_params) > 0:
            qs = qs.filter(**filter_params)

        fqs = self.filter_queryset(qs)
        page = self.paginate_queryset(fqs)

        serializer = self.get_serializer(page, many=True)
        for element in serializer.data:
            site = Site.objects.get(id=element['site'])
            merge_in_site_info(element, site)
            element['supportTickets'] = {'open': 0, 'minor': 0, 'request': 0}
            element['processedDays'] = 1  # TODO put this value based in the processed days
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        qs = self.get_queryset()
        element = qs.filter(id=int(pk)).get()#to do use id and pk adequately
        eljs = element.dict()
        merge_in_site_info(eljs, element.site)
        eljs['supportTickets'] = {'open': 0, 'minor': 0, 'request': 0}
        eljs['processedDays'] = 1 #TODO put this value based in the processed days
        return response.Response(data=eljs)


class SitesViewSet(viewsets.ModelViewSet):
    queryset = Site.objects.all()
    serializer_class = SiteSerializer
    permission_classes = [permissions.IsAuthenticated]


class LinksViewSet(viewsets.ModelViewSet):
    queryset = Link.objects.all()
    serializer_class = LinkSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JSONWebTokenAuthentication]


class EventsViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JSONWebTokenAuthentication]


class Database3ViewSet(viewsets.ModelViewSet):
    queryset = Database3.objects.all()
    serializer_class = Database3Serializer
    permission_classes = [permissions.IsAuthenticated]


class OldEdgesViewSet(viewsets.ViewSet):
    def _get_s3_bucket(self):
        aws_credentials = dotenv.dotenv_values(settings.BASE_DIR/'.env')
        s3 = boto3.resource('s3', aws_access_key_id=aws_credentials["aws_access_key_id"], aws_secret_access_key=aws_credentials["aws_secret_access_key"])
        return s3.Bucket('citel-nap')
    def _get_s3_client(self):
        aws_credentials = dotenv.dotenv_values(settings.BASE_DIR/'.env')
        client = boto3.client('s3', aws_access_key_id=aws_credentials["aws_access_key_id"], aws_secret_access_key=aws_credentials["aws_secret_access_key"])
        return client
    def find_s3_folders(self, folder):
        clnt = self._get_s3_client()
        paginator = clnt.get_paginator('list_objects')
        page_iterator = paginator.paginate(Bucket='citel-nap', Delimiter="/", Prefix=folder)

        #We seek the folder names to locate the latest date
        prefixes = set()
        for element in page_iterator:
            common_prefixes_here = element['CommonPrefixes']
            prefixes.update({x['Prefix'][len(folder):-1] for x in common_prefixes_here})
        return list(prefixes)

    def list(self, request):
        prefix = "velocloud/edges/"

        #We seek the folder names to locate the latest date
        edges_dated_folders = self.find_s3_folders(prefix)
        edges_dated_folders_dict = {datetime.datetime.strptime(ed, "%Y-%m-%d"): ed for ed in edges_dated_folders}
        last_date = max(edges_dated_folders_dict.keys())
        last_date_folder = edges_dated_folders_dict[last_date]

        #prefix for the latest date:
        last_date_prefix = f"{prefix}{last_date_folder}/"  # rehydrated with terminal /
        folders = self.find_s3_folders(last_date_prefix)
        folders.sort(key=float)
        used_folder = folders[-1]

        complete_s3_path = f"{prefix}{last_date_folder}/{used_folder}"
        client = self._get_s3_client()
        paginator = client.get_paginator('list_objects')
        page_iterator = paginator.paginate(Bucket='citel-nap', Prefix=complete_s3_path)

        velocloud_Edge_ID_RE = re.compile("edge-(\d+).json")
        edges = {}
        for element in page_iterator:
            for elem in element['Contents']:
                elem_key = elem['Key']
                key_basename = elem_key[len(complete_s3_path)+1:]
                edge_id_matcher = velocloud_Edge_ID_RE.match(key_basename)
                edge_id = int(edge_id_matcher.group(1))
                bytes_file_like_obj = io.BytesIO()
                client.download_fileobj(Bucket='citel-nap', Key=elem['Key'], Fileobj=bytes_file_like_obj)
                bytes_file_like_obj.seek(0)
                edge_info = json.load(bytes_file_like_obj)
                edges[edge_id] = edge_info

        return response.Response(data=edges)


def hello(request, resource=None):
    return render(request, "index.html", {"name": resource or 'World'})

