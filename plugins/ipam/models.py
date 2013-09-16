from django.db import models
from django.utils.translation import ugettext as _
import netaddr as na


class IPAM(models.Manager):

    def create_network(self, netaddr):
        network = Network(netaddr=netaddr)
        network.save()
        return True

    def create_sunet(self, netaddr, hostcount=None):
        if hostcount:
            for subnet in na.Network(netaddr).subnet(hostcount):
                Subnet(supernet=netaddr, netaddr=subnet, mac="")
        return True

    def delete_network(self, netaddr):
        return True

    def delete_subnet(self, sunbet):
        return True

    def allocate_addr(self, subnet):
        return True

    def release_addr(self, addr):
        return True

    def get_registed_network_by_netaddr(self, netaddr):
        return Network.objects.get(netaddr=netaddr)


class Network(models.Model):
    netaddr = models.IPAddressField(null=False, unique=True)
    is_used = models.BooleanField(default=False)

    def __unicode__(self):
        return self.netaddr

    class Meta:
        verbose_name = _("Network")


class Subnet(models.Model):
    supernet = models.ForeignKey(Network)
    netaddr = models.IPAddressField(null=False, unique=True)
    owner = models.CharField(max_length=20, null=False, unique=True)
    is_used = models.BooleanField(default=False)

    def __unicode__(self):
        return self.netaddr

    class Meta:
        verbose_name = _("Subnet")


class IPAddr(models.Model):
    supernet = models.ForeignKey(Subnet)
    addr = models.IPAddressField(null=False, unique=True)
    mac = models.CharField(max_length=20, null=False, unique=True)
    is_used = models.BooleanField(default=False)
    objects = IPAM()

    def __unicode__(self):
        return self.addr

    class Meta:
        verbose_name = _("IPAddr")
