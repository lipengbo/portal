from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.db.models import F

from project.models import *
from resources.models import *

# Create your models here.
class Gateway(Server):
    pass


class SwitchPort(Resource):

    #: the switch that the rule is applied on, can be Switch or VirtualSwitch
    switch = models.ForeignKey(Switch)
    port = models.PositiveIntegerField()
    slices = models.ManyToManyField(Slice, through="SlicePort")

    class Meta:
        unique_together = (("switch", "port"), )


class SlicePort(models.Model):
    slice = models.ForeignKey(Slice)
    switch_port = models.ForeignKey(SwitchPort)


    class Meta:
        unique_together = (("slice", "switch_port"), )

class VirtualSwitch(Switch):
    """
        A virtual switch service that created on a Physical Server
    """
    server = models.ForeignKey(Server)

class Network(Resource):
    netaddr = models.IPAddressField(null=False)
    netmask = models.IPAddressField(null=False)
    slices = models.ManyToManyField(Slice, through="SliceNetwork")

    class Meta:
        unique_together = ("netaddr", "netmask")

class Subnet(Resource):
    network = models.ForeignKey(Network)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    host = generic.GenericForeignKey('content_type', 'object_id')
    start = models.IPAddressField(null=False)
    netmask = models.IPAddressField(null=False)
    type = models.IntegerField(default=1) # 1: static, 2: dynamic

    class Meta:
        unique_together = (u"network", u"object_id", u"start", u"netmask")

class IPAddress(models.Model):
    ip_range = models.ForeignKey(Subnet)
    address = models.IPAddressField(null=False)
    available  = models.BooleanField(default=False)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    host = generic.GenericForeignKey('content_type', 'object_id')

    def __unicode__(self):
        return self.address

    class Meta:
        pass

class SliceNetwork(models.Model):
    network = models.ForeignKey(Network)
    slice = models.ForeignKey(Slice)
    use_dhcp = models.BooleanField(default=False)
    public = models.BooleanField(default=False)
    description = models.TextField(null=True)
    ip_ranges = models.ManyToManyField(Subnet)
    ip_addresses = models.ManyToManyField(IPAddress, related_name="ipaddress_slice_network")
    dnses = models.ManyToManyField(IPAddress)
    dhcpes = models.ManyToManyField(IPAddress, related_name="dhcp_slice_networks")

    def __unicode__(self):
        return self.name

    class Meta:
        pass


class IslandSliceNetworkGateway(IslandResource):
    slice_network = models.ForeignKey(SliceNetwork)
    gateway = models.ForeignKey(Gateway)

    def __unicode__(self):
        return self.address

    class Meta:
        unique_together = ("slice_network", "island")

class NAT(Resource):
    """
    primary key: level + public_address
    """
    slice = models.ForeignKey(Slice)
    parent = models.ForeignKey("self", null=True)
    public_ip = models.ForeignKey(IPAddress, related_name="public_ip_nats")
    private_ip = models.ForeignKey(IPAddress, related_name="private_ip_nats")
    date_expired = models.DateTimeField()
    available = models.BooleanField(default=False)

    def __unicode__(self):
        return self.public_ip
