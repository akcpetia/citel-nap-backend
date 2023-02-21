from django.contrib.auth.models import User
from .models import Edge, RDSEdge, Site, Device, Link, Database3, Event
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'groups']


class RDSEdgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RDSEdge
        exclude = []


class EdgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Edge
        exclude = []


class SiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Site
        exclude = []


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        exclude = []


class LinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Link
        exclude = []


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        exclude = []


class Database3Serializer(serializers.ModelSerializer):
    class Meta:
        model = Database3
        exclude = []