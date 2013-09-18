from django.db import models
from django.utils.translation import ugettext as _
import random
import netaddr as na
from plugins.common import exception


class HostCountOutOfRangeException(Exception):

    def __init__(self, message=None):
        super(HostCountOutOfRangeException, self).__init__(message)


class IPAM(models.Manager):

    def create_subnet_64(self, supernet, owner, ipcount=64):
        subnetaddrs = Subnet.objects.filter(supernet=supernet).order_by('-id')
        if subnetaddrs:
            subnetaddr = subnetaddrs[0]
            subnet = self.next_sub(subnetaddr)
            if subnet:
                result = Subnet(supernet=supernet, netaddr=str(
                    subnet), owner=owner)
                result.save()
                self.generate_ip_usage(subnet)
            else:
                raise exception.NetworkNoMoreSubNet(network=supernet.netaddr)
        else:
            subnet = [subnet for subnet in na.Network(
                supernet.netaddr).subnet(ipcount, count=1)][0]
            result = Subnet(supernet=supernet, netaddr=str(
                subnet), owner=owner)
            result.save()
            supernet.is_used = True
            supernet.save()
            self.generate_ip_usage(subnet)
        return result

    def create_subnet_base(self, supernet, owner='base'):
        supernet = Network.objects.get(netaddr=supernet)
        if supernet.is_used:
            raise exception.NetWorkInUse(network=supernet.netaddr)
        result = Subnet(
            supernet=supernet, netaddr=supernet.netaddr, owner=owner)
        result.save()
        supernet.is_used = True
        supernet.save()
        self.generate_ip_usage(supernet)
        return result

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

    def next_sub(self, subnet):
        if subnet.supernet in subnet.supernet():
            return subnet.next()
        return None

    def delete_network(self, netaddr):
        network = Network.objects.get(netaddr=netaddr)
        network.delete()

    def delete_subnet(self, subnet_addr):
        network = Subnet.objects.get(netaddr=subnet_addr)
        network.delete()

    def allocate_ip(self, owner):
        ip_obj = self.objects.filter(supernet__owner=owner, is_used=False)[0]
        ip_obj.is_used = True
        ip_obj.save()
        return ip_obj.ip, na.IPNetwork(ip_obj.supernet.netaddr).prefixlen

    def release_ip(self, ip):
        ip_obj = self.objects.get(ip=ip)
        ip_obj.is_used = False
        ip_obj.save()
        return True

    def generate_ip_usage(self, subnet):
        mysubnet = Subnet.objects.get(netaddr=str(subnet))
        print mysubnet
        for ip in subnet.iter_hosts():
            mac = self.generate_mac_address()
            IPUsage(supernet=mysubnet, ip=str(ip), mac=mac).save()


class Network(models.Model):
    TYPE_CHOICE = ((0, "subnet for physics, It's a Class B IP Address"),
                  (1, 'subnet for slice, It contains 64 ips'),)
    netaddr = models.IPAddressField(null=False, unique=True)
    type = models.IntegerField(null=False, choices=TYPE_CHOICE)
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
    ip = models.IPAddressField(null=False, unique=True)
    mac = models.CharField(max_length=20, null=False, unique=True)
    is_used = models.BooleanField(default=False)
    objects = IPAM()

    def __unicode__(self):
        return self.addr

    class Meta:
        verbose_name = _("IPAddr")
