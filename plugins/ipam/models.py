from django.db import models
from django.utils.translation import ugettext as _
import random
import netaddr as na
from ccf.plugins.common import exception


class HostCountOutOfRangeException(Exception):

    def __init__(self, message=None):
        super(HostCountOutOfRangeException, self).__init__(message)


class IPAM(models.Manager):

    def create_net(self, netaddr):
        network = Network(netaddr=netaddr)
        network.save()
        return network

    def create_subnet_64(self, supernet, ipcount=64):
        if supernet.is_used:
            raise exception.NetWorkInUse(network=supernet.netaddr)
        for subnet_addr in na.Network(supernet.netaddr).subnet(ipcount):
            Subnet(supernet=supernet.id, netaddr=subnet_addr).save()
        supernet.is_used = True
        supernet.save()

    def create_subnet_base(self, supernet):
        if supernet.is_used:
            raise exception.NetWorkInUse(network=supernet.netaddr)
        Subnet(supernet=supernet.id, netaddr=supernet.netaddr).save()
        supernet.is_used = True
        supernet.save()

    def delete_network(self, netaddr):
        network = Network.objects.get(netaddr=netaddr)
        network.is_used = False
        network.save()

    def delete_subnet(self, subnet_addr):
        network = Subnet.objects.get(netaddr=subnet_addr)
        network.is_used = False
        network.save()

    def allocate_addr(self, owner):
        return True

    def release_addr(self, addr):
        return True

    def get_registed_network_by_netaddr(self, netaddr):
        return Network.objects.get(netaddr=netaddr)

    def generate_mac_address(self):
        """Generate an Ethernet MAC address."""
        mac = [0xfa, 0x16, 0x3e,
               random.randint(0x00, 0xff),
               random.randint(0x00, 0xff),
               random.randint(0x00, 0xff)]
        result = ':'.join(map(lambda x: "%02x" % x, mac))
        if self.filter(mac=result):
            self.generate_mac_address()
        return result


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
    owner = models.CharField(max_length=20, null=True, unique=True)
    is_used = models.BooleanField(default=False)

    def next(self):
        pass

    def __unicode__(self):
        return self.netaddr

    class Meta:
        verbose_name = _("Subnet")


class IPUsage(models.Model):
    supernet = models.ForeignKey(Subnet)
    addr = models.IPAddressField(null=False, unique=True)
    mac = models.CharField(max_length=20, null=False, unique=True)
    objects = IPAM()

    def __unicode__(self):
        return self.addr

    class Meta:
        verbose_name = _("IPAddr")
