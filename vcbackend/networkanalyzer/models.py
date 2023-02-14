import json, typing, datetime

from django.db import models

class ModelJSONEncoder(json.JSONEncoder):
    def default(self, o: typing.Any) -> typing.Any:
        if isinstance(o, datetime.datetime):
            return o.isoformat()
        elif isinstance(o, datetime.timedelta):
            return o.total_seconds() #returns the time in seconds
        else:
            return super().default(o)

class JSONReprMixin:
    "Allows representing the model as a JSON serializable object"
    def json(self):
        jsond = self.__dict__.copy()
        del jsond['_state']
        return jsond


class ZeroNullDateTime(models.DateTimeField, JSONReprMixin):
    """This field is similar to models.DateTimefield, but when it encounters a '0000-00-00 00:00:00' it deems
    it as a null value (and saves it as such).
    """
    def to_python(self, value):
        if value == "0000-00-00 00:00:00":
            return None
        else:
            return super().to_python(value)

class VolatileIdField(models.IntegerField, JSONReprMixin):
    concrete = False




# Create your models here.
class Network(models.Model):
    serverUrl = models.URLField(unique=True)


class Site(models.Model, JSONReprMixin):
    #id = models.IntegerField(primary_key=True)
    created = models.DateTimeField()
    name = models.CharField(max_length=100, null=True)
    contactName = models.CharField(max_length=100, null=True)
    contactPhone = models.CharField(max_length=30, null=True)
    contactMobile = models.CharField(max_length=30, null=True)
    contactEmail = models.CharField(max_length=100, null=True)
    streetAddress = models.CharField(max_length=100, null=True)
    streetAddress2 = models.CharField(max_length=100, null=True)
    city = models.CharField(max_length=100, null=True)
    state = models.CharField(max_length=100, null=True)
    postalCode = models.CharField(max_length=100, null=True)
    country = models.CharField(max_length=100, null=True)
    lat = models.FloatField(null=True)
    lon = models.FloatField(null=True)
    timezone = models.CharField(max_length=100, null=True)
    locale = models.CharField(max_length=100, null=True)
    shippingSameAsLocation = models.IntegerField(null=True)
    shippingContactName = models.CharField(max_length=100, null=True)
    shippingAddress = models.CharField(max_length=100, null=True)
    shippingAddress2 = models.CharField(max_length=100, null=True)
    shippingCity = models.CharField(max_length=100, null=True)
    shippingState = models.CharField(max_length=100, null=True)
    shippingPostalCode = models.CharField(max_length=100, null=True)
    shippingCountry = models.CharField(max_length=100, null=True)
    modified = models.DateTimeField()
    logicalId = models.CharField(max_length=50, null=True)


class Ha(models.Model, JSONReprMixin):
    type = models.CharField(max_length=20)


class Edge(models.Model, JSONReprMixin):
    edgeId = models.IntegerField(unique=True, help_text="The ID used in the Velocloud API")
    created = models.DateTimeField()
    enterpriseId = models.IntegerField()
    siteId = models.IntegerField()
    activationKey = models.CharField(max_length=100)
    activationKeyExpires = models.CharField(max_length=100)
    activationState = models.CharField(max_length=20)#States, like ACTIVATED
    activationTime = models.DateTimeField()
    softwareVersion = models.CharField(max_length=20)
    buildNumber = models.CharField(max_length=30)
    factorySoftwareVersion = models.CharField(max_length=20)
    factoryBuildNumber = models.CharField(max_length=30)
    softwareUpdated = ZeroNullDateTime(null=True)
    selfMacAddress = models.CharField(max_length=30)# like 18:5a:58:02:68:00
    deviceId = models.CharField(max_length=50, null=True) #like 1E559898-B71A-4E34-8CCF-1B163BDCA70E
    logicalId = models.CharField(max_length=50) #like 8706f2ca-5651-40fe-a260-37da01ffe75f
    serialNumber = models.CharField(max_length=20, null=True) #like 6618PK2,
    modelNumber = models.CharField(max_length=20) #like edge610
    deviceFamily = models.CharField(max_length=20) #like EDGE6X0
    name = models.CharField(max_length=50)#like Tech Team Lab 610
    dnsName = models.CharField(max_length=50, null=True)
    description = models.TextField(max_length=50, null=True)
    alertsEnabled = models.IntegerField() # like 1
    operatorAlertsEnabled = models.IntegerField() #like 1
    edgeState = models.CharField(max_length=20) # like CONNECTED
    edgeStateTime = ZeroNullDateTime(null=True)
    isLive = models.IntegerField() # like 0
    systemUpSince = ZeroNullDateTime() # like 2020-01-21T00:13:11.000Z
    serviceUpSince = ZeroNullDateTime(null=True)
    lastContact = ZeroNullDateTime(null=True)
    serviceState = models.CharField(max_length=20)#like IN_SERVICE",
    endpointPkiMode=models.CharField(max_length=40)#like "CERTIFICATE_REQUIRED",
    haState = models.CharField(max_length=40)
    haPreviousState= models.CharField(max_length=40)#UNCONFIGURED"
    haLastContact = ZeroNullDateTime(null=True)
    haSerialNumber = models.TextField(max_length=50, null=True)
    modified = ZeroNullDateTime()
    customInfo = models.TextField(null=True)
    isSoftwareVersionSupportedByVco = models.BooleanField(null=True)
    isHub = models.BooleanField()
    # ha, vnfs, recentLinks
    ha = models.JSONField()
    vnfs = models.TextField(null=True, blank=True)
    recentLinks = models.ManyToManyField('Link')
    site = models.ForeignKey('Site', null=True, on_delete=models.deletion.SET_NULL)
    bastionState = models.CharField(max_length=20, null=True)


class Link(models.Model, JSONReprMixin):
    #id = models.IntegerField(primary_key=True)
    created = models.DateTimeField()
    edgeId = models.IntegerField()
    logicalId= models.CharField(max_length=50)# like 00:ff:4b:e3:2a:74:0000
    internalId = models.CharField(max_length=50) # like 00000006-1fce-4389-96a9-fdf72902d1eb
    interface= models.CharField(max_length=20) # like GE6
    macAddress = models.CharField(max_length=50, null=True) #can be null
    overlayType = models.CharField(max_length=20) # like IPv4
    ipAddress = models.CharField(max_length=20) # like 162.156.172.52
    ipV6Address = models.CharField(max_length=20, null=True)
    netmask = models.CharField(max_length=30, null=True)
    networkSide = models.CharField(max_length=20) # like WAN
    networkType= models.CharField(max_length=20) # like ETHERNET
    displayName= models.CharField(max_length=20) # like TELUS GPON
    userOverride = models.IntegerField()
    isp= models.CharField(max_length=50, null=True)
    org= models.CharField(max_length=50, null=True)
    lat= models.FloatField()
    lon= models.FloatField()
    lastActive= models.DateTimeField()
    state = models.CharField(max_length=20) # like STABLE
    backupState= models.CharField(max_length=20) # like UNCONFIGURED
    linkMode= models.CharField(max_length=20) # like ACTIVE
    vpnState= models.CharField(max_length=20) # like STABLE
    lastEvent = models.DateTimeField()
    lastEventState = models.CharField(max_length=20) # like STABLE
    alertsEnabled = models.IntegerField()
    operatorAlertsEnabled = models.IntegerField()
    serviceState = models.CharField(max_length=20) # like IN_SERVICE
    modified = models.DateTimeField()
    effectiveState = models.CharField(max_length=20) # like STABLE

class Database1(models.Model, JSONReprMixin):
    site_name = models.IntegerField() #really is a site ID (an integer number)
    interface_name = models.CharField(max_length=30) #like GE2
    link_name = models.IntegerField() # a numeric ID, again (edge ID?)
    link_mode = models.CharField(max_length=30) #Ej ACTIVE/BACKUP from link.linkMode
    number_of_interfaces = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True, null=True)

class Database2(models.Model, JSONReprMixin):
    site_name = models.IntegerField() #really is a site ID (an integer number)
    interface_name = models.CharField(max_length=30) #like GE2
    interface_type = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

class Database3(models.Model, JSONReprMixin):
    site_name = models.IntegerField() #really is a site ID (an integer number)
    interface_name = models.CharField(max_length=30) #like GE2
    event_type = models.CharField(max_length=30) # link or edge
    outage_duration = models.DurationField()
    outage_data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True, null=True)


