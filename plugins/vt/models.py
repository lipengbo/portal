from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from resources.models import ComputeResource, Server
from slice.models import Slice
from plugins.ipam.models import IPUsage
from plugins.common import utils


class Image(models.Model):
    uuid = models.CharField(max_length=36, unique=True)
    name = models.CharField(max_length=36)
    url = models.CharField(max_length=256)
    type = models.IntegerField(null=True)
    version = models.CharField(null=True, max_length=32)

    def __unicode__(self):
        return self.name


class Flavor(models.Model):
    name = models.CharField(max_length=64)
    cpu = models.IntegerField()
    ram = models.IntegerField()
    hdd = models.IntegerField()

    def __unicode__(self):
        return self.name


class VirtualMachine(ComputeResource):
    uuid = models.CharField(max_length=20, null=True, unique=True)
    ip = models.ForeignKey(IPUsage)
    mac = models.CharField(max_length=20, null=True)
    enable_dhcp = models.BooleanField(default=True)
    slice = models.ForeignKey(Slice)
    flavor = models.ForeignKey(Flavor)
    image = models.ForeignKey(Image)
    server = models.ForeignKey(Server)

    def get_ipaddr(self):
        return self.ip.ipaddr

    def get_netmask(self):
        return self.ip.supernet.get_netmask()

    def get_network(self):
        return self.ip.supernet.get_network()

    def get_ip_range_size(self):
        return self.ip.supernet.get_size()

    def get_prefixlen(self):
        return self.ip.supernet.get_prefixlen()

    def get_cidr(self):
        return self.ip.supernet.get_cidr()

    def get_broadcast(self):
        return self.ip.supernet.get_broadcast()

    def get_slice_id(self):
        return self.slice.id

    def get_image_uuid(self):
        return self.image.uuid

    def get_image_name(self):
        return self.image.name

    def get_image_url(self):
        return self.image.url

    def create_vm(self):
        print '----------------------create a vm=%s -------------------------' % self.name

    def delete_vm(self):
        print '----------------------delete a vm=%s -------------------------' % self.name


class HostMac(models.Model):
    mac = models.CharField(max_length=32)
    host_type = models.ForeignKey(ContentType)
    host_id = models.PositiveIntegerField()
    #: the switch that the rule is applied on, can be Switch or VirtualSwitch
    host = generic.GenericForeignKey('host_type', 'host_id')


@receiver(post_save, sender=VirtualMachine)
def vm_pre_save(sender, instance, **kwargs):
    print '--------------------vm pre save-------------------------'
    print kwargs
    print '--------------------vm pre save-------------------------'
    instance.ip = IPUsage.objects.allocate_ip(instance.slice.name)
    instance.uuid = utils.gen_uuid()
    instance.mac = utils.generate_mac_address(instance.get_ipaddr())


@receiver(post_save, sender=VirtualMachine)
def vm_post_save(sender, instance, **kwargs):
    if kwargs.get('created'):
        instance.create_vm()
        print '-------------------Add HostMac----------------------------'


@receiver(post_save, sender=VirtualMachine)
def vm_post_delete(sender, instance, **kwargs):
    print '--------------------vm post delete-------------------------'
    print kwargs
    print '--------------------vm post delete-------------------------'
    IPUsage.objects.release_ip(instance.ip)
    instance.delete_vm()
    print '-------------------Delete HostMac----------------------------'
