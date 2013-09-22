from django.db import models
from django.db.models.signals import post_save
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from resources.models import Resource, Server, IslandResource
from slice.models import Slice

# Create your models here.
class Gateway(Server):
    pass


class SliceNetwork(models.Model):
    network = models.ForeignKey(Network)
    slice = models.ForeignKey(Slice)
    use_dhcp = models.BooleanField(default=False)
    public = models.BooleanField(default=False)
    description = models.TextField(null=True)
    subnets = models.ManyToManyField(Subnet)
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
