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


class Network(models.Model):
    serverUrl = models.URLField(unique=True)


class Site(models.Model, JSONReprMixin):
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
    type = models.TextField()


class AbstractEdge(models.Model, JSONReprMixin):
    class Meta:
        abstract = True
    edgeId = models.IntegerField(unique=True, help_text="The ID used in the Velocloud API")
    created = ZeroNullDateTime(null=True)
    enterpriseId = models.IntegerField()
    siteId = models.IntegerField()
    activationKey = models.CharField(max_length=100)
    activationKeyExpires = models.CharField(max_length=100)
    activationState = models.TextField()#States, like ACTIVATED
    activationTime = ZeroNullDateTime(null=True)
    softwareVersion = models.TextField()
    buildNumber = models.TextField()
    factorySoftwareVersion = models.TextField()
    factoryBuildNumber = models.TextField()
    softwareUpdated = ZeroNullDateTime(null=True)
    selfMacAddress = models.TextField()# like 18:5a:58:02:68:00
    deviceId = models.CharField(max_length=50, null=True) #like 1E559898-B71A-4E34-8CCF-1B163BDCA70E
    logicalId = models.CharField(max_length=50) #like 8706f2ca-5651-40fe-a260-37da01ffe75f
    serialNumber = models.TextField(null=True) #like 6618PK2,
    modelNumber = models.TextField() #like edge610
    deviceFamily = models.TextField() #like EDGE6X0
    name = models.CharField(max_length=50)#like Tech Team Lab 610
    dnsName = models.CharField(max_length=50, null=True)
    description = models.TextField(null=True)
    alertsEnabled = models.IntegerField() # like 1
    operatorAlertsEnabled = models.IntegerField() #like 1
    edgeState = models.TextField() # like CONNECTED
    edgeStateTime = ZeroNullDateTime(null=True)
    isLive = models.IntegerField() # like 0
    systemUpSince = ZeroNullDateTime() # like 2020-01-21T00:13:11.000Z
    serviceUpSince = ZeroNullDateTime(null=True)
    lastContact = ZeroNullDateTime(null=True)
    serviceState = models.TextField()#like IN_SERVICE",
    endpointPkiMode=models.CharField(max_length=40)#like "CERTIFICATE_REQUIRED",
    haState = models.CharField(max_length=40)
    haPreviousState= models.CharField(max_length=40)#UNCONFIGURED"
    haLastContact = ZeroNullDateTime(null=True)
    haSerialNumber = models.TextField(null=True)
    modified = ZeroNullDateTime()
    customInfo = models.TextField(null=True)
    isSoftwareVersionSupportedByVco = models.BooleanField(null=True)
    isHub = models.BooleanField()
    # ha, vnfs, recentLinks
    ha = models.JSONField()
    vnfs = models.TextField(null=True, blank=True)
    recentLinks = models.ManyToManyField('Link')
    site = models.ForeignKey('Site', null=True, on_delete=models.deletion.SET_NULL)
    bastionState = models.TextField(null=True)
    index = models.IntegerField(null=True)
    summary = models.TextField()


class Edge(AbstractEdge):
    pass


class RDSEdge(models.Model, JSONReprMixin):
    index = models.BigIntegerField(blank=True, null=True)
    edgeid = models.BigIntegerField(db_column='edgeId', blank=True, null=True)  # Field name made lowercase.
    created = models.TextField(blank=True, null=True)
    enterpriseid = models.BigIntegerField(db_column='enterpriseId', blank=True, null=True)  # Field name made lowercase.
    siteid = models.BigIntegerField(db_column='siteId', blank=True, null=True)  # Field name made lowercase.
    activationkey = models.TextField(db_column='activationKey', blank=True, null=True)  # Field name made lowercase.
    activationkeyexpires = models.TextField(db_column='activationKeyExpires', blank=True, null=True)  # Field name made lowercase.
    activationstate = models.TextField(db_column='activationState', blank=True, null=True)  # Field name made lowercase.
    activationtime = models.TextField(db_column='activationTime', blank=True, null=True)  # Field name made lowercase.
    softwareversion = models.TextField(db_column='softwareVersion', blank=True, null=True)  # Field name made lowercase.
    buildnumber = models.TextField(db_column='buildNumber', blank=True, null=True)  # Field name made lowercase.
    factorysoftwareversion = models.TextField(db_column='factorySoftwareVersion', blank=True, null=True)  # Field name made lowercase.
    factorybuildnumber = models.TextField(db_column='factoryBuildNumber', blank=True, null=True)  # Field name made lowercase.
    softwareupdated = models.TextField(db_column='softwareUpdated', blank=True, null=True)  # Field name made lowercase.
    selfmacaddress = models.TextField(db_column='selfMacAddress', blank=True, null=True)  # Field name made lowercase.
    deviceid = models.TextField(db_column='deviceId', blank=True, null=True)  # Field name made lowercase.
    logicalid = models.TextField(db_column='logicalId', blank=True, null=True)  # Field name made lowercase.
    serialnumber = models.TextField(db_column='serialNumber', blank=True, null=True)  # Field name made lowercase.
    modelnumber = models.TextField(db_column='modelNumber', blank=True, null=True)  # Field name made lowercase.
    devicefamily = models.TextField(db_column='deviceFamily', blank=True, null=True)  # Field name made lowercase.
    name = models.TextField(blank=True, null=True)
    dnsname = models.TextField(db_column='dnsName', blank=True, null=True)  # Field name made lowercase.
    description = models.TextField(blank=True, null=True)
    alertsenabled = models.BigIntegerField(db_column='alertsEnabled', blank=True, null=True)  # Field name made lowercase.
    operatoralertsenabled = models.BigIntegerField(db_column='operatorAlertsEnabled', blank=True, null=True)  # Field name made lowercase.
    edgestate = models.TextField(db_column='edgeState', blank=True, null=True)  # Field name made lowercase.
    edgestatetime = models.TextField(db_column='edgeStateTime', blank=True, null=True)  # Field name made lowercase.
    islive = models.BigIntegerField(db_column='isLive', blank=True, null=True)  # Field name made lowercase.
    systemupsince = models.TextField(db_column='systemUpSince', blank=True, null=True)  # Field name made lowercase.
    serviceupsince = models.TextField(db_column='serviceUpSince', blank=True, null=True)  # Field name made lowercase.
    lastcontact = models.TextField(db_column='lastContact', blank=True, null=True)  # Field name made lowercase.
    servicestate = models.TextField(db_column='serviceState', blank=True, null=True)  # Field name made lowercase.
    endpointpkimode = models.TextField(db_column='endpointPkiMode', blank=True, null=True)  # Field name made lowercase.
    hastate = models.TextField(db_column='haState', blank=True, null=True)  # Field name made lowercase.
    hapreviousstate = models.TextField(db_column='haPreviousState', blank=True, null=True)  # Field name made lowercase.
    halastcontact = models.TextField(db_column='haLastContact', blank=True, null=True)  # Field name made lowercase.
    haserialnumber = models.TextField(db_column='haSerialNumber', blank=True, null=True)  # Field name made lowercase.
    modified = models.TextField(blank=True, null=True)
    custominfo = models.TextField(db_column='customInfo', blank=True, null=True)  # Field name made lowercase.
    issoftwareversionsupportedbyvco = models.BooleanField(db_column='isSoftwareVersionSupportedByVco', blank=True, null=True)  # Field name made lowercase.
    ishub = models.BooleanField(db_column='isHub', blank=True, null=True)  # Field name made lowercase.
    ha = models.TextField(blank=True, null=True)
    vnfs = models.TextField(blank=True, null=True)
    site_id = models.BigIntegerField(blank=True, null=True)
    bastionstate = models.TextField(db_column='bastionState', blank=True, null=True)  # Field name made lowercase.
    summary = models.JSONField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'edge'


class Device(models.Model, JSONReprMixin):
    index = models.BigIntegerField(blank=True, null=True)
    site_name = models.BigIntegerField(blank=True, null=True)
    interface_name = models.TextField(blank=True, null=True)
    link_name = models.BigIntegerField(blank=True, null=True)
    link_mode = models.TextField(blank=True, null=True)
    number_of_interfaces = models.BigIntegerField(blank=True, null=True)
    created_at = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'devices'


class Link(models.Model, JSONReprMixin):
    created = models.DateTimeField()
    edgeId = models.IntegerField()
    logicalId= models.CharField(max_length=50)# like 00:ff:4b:e3:2a:74:0000
    internalId = models.CharField(max_length=50) # like 00000006-1fce-4389-96a9-fdf72902d1eb
    interface= models.TextField() # like GE6
    macAddress = models.CharField(max_length=50, null=True) #can be null
    overlayType = models.TextField() # like IPv4
    ipAddress = models.TextField() # like 162.156.172.52
    ipV6Address = models.TextField(null=True)
    netmask = models.CharField(max_length=30, null=True)
    networkSide = models.TextField() # like WAN
    networkType= models.TextField() # like ETHERNET
    displayName= models.TextField() # like TELUS GPON
    userOverride = models.IntegerField()
    isp= models.CharField(max_length=50, null=True)
    org= models.CharField(max_length=50, null=True)
    lat= models.FloatField()
    lon= models.FloatField()
    lastActive= ZeroNullDateTime()
    state = models.TextField() # like STABLE
    backupState= models.TextField() # like UNCONFIGURED
    linkMode= models.TextField() # like ACTIVE
    vpnState= models.TextField() # like STABLE
    lastEvent = ZeroNullDateTime(null=True)
    lastEventState = models.TextField() # like STABLE
    alertsEnabled = models.IntegerField()
    operatorAlertsEnabled = models.IntegerField()
    serviceState = models.TextField() # like IN_SERVICE
    modified = ZeroNullDateTime()
    effectiveState = models.TextField() # like STABLE


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


