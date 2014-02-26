from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete, pre_delete, pre_save
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User

from resources.models import IslandResource, Server, SwitchPort
from slice.models import Slice
from plugins.ipam.models import IPUsage
from plugins.openflow.models import Controller
from plugins.common import utils
from plugins.common.agent_client import AgentClient
from plugins.common.exception import ConnectionRefused
from django.utils.translation import ugettext as _
import errno
from socket import error as socket_error
from etc.config import function_test
DOMAIN_STATE_TUPLE = (
    (0, _('nostate')),
    (1, _('running')),
    (2, _('blocked')),
    (3, _('paused')),
    (4, _('shutdown')),
    (5, _('shutoff')),
    (6, _('crashed')),
    (7, _('pmsuspended')),
    (8, _('building')),
    (9, _('failed')),
    (10, _('not exist'))
)
DOMAIN_STATE_DIC = {
    'nostate': 0,
    "running": 1,
    "blocked": 2,
    "paused": 3,
    "shutdown": 4,
    "shutoff": 5,
    "crashed": 6,
    "pmsuspended": 7,
    "building": 8,
    "failed": 9,
    "notexist": 10,
}
HOST_STATE = {
    'active': 1,
    'disactive': 0,
}
VM_TYPE = (
    (0, _('vm for controller')),
    (1, _('vm for slice')),
    (2, _('vm for gateway'))
)


class Image(models.Model):
    uuid = models.CharField(max_length=36, unique=True)
    name = models.CharField(max_length=36)
    url = models.CharField(max_length=256)
    type = models.IntegerField(null=True)
    version = models.CharField(max_length=32, null=True)
    username = models.CharField(max_length=36, null=True)
    password = models.CharField(max_length=36, null=True)
    os = models.CharField(max_length=256, null=True)

    def __unicode__(self):
        #return self.os and self.os or ""
        return self.name

    class Meta:
        verbose_name = _("Image")


class Flavor(models.Model):
    name = models.CharField(max_length=64)
    cpu = models.IntegerField()
    ram = models.IntegerField()
    hdd = models.IntegerField()

    def __unicode__(self):
        return _(self.name)

    class Meta:
        verbose_name = _("Flavor")


class VirtualMachine(IslandResource):
    uuid = models.CharField(max_length=36, null=True, unique=True)
    ip = models.ForeignKey(IPUsage, null=True, related_name="virtualmachine_set")
    gateway_public_ip = models.ForeignKey(IPUsage, null=True, related_name="gateway_set")
    mac = models.CharField(max_length=20, null=True)
    enable_dhcp = models.BooleanField(default=False)
    slice = models.ForeignKey(Slice)
    flavor = models.ForeignKey(Flavor)
    image = models.ForeignKey(Image)
    server = models.ForeignKey(Server)
    switch_port = models.ForeignKey(SwitchPort, null=True)
    state = models.IntegerField(null=True, choices=DOMAIN_STATE_TUPLE)
    type = models.IntegerField(null=False, choices=VM_TYPE)

    def get_ipaddr(self):
        return self.ip.ipaddr

    def get_gw_mac(self):
        return utils.generate_mac_address(self.gateway_public_ip.ipaddr)

    def get_netmask(self):
        return str(self.ip.supernet.get_network().netmask)

    def get_network(self):
        return str(self.ip.supernet.get_network().network)

    def get_ip_range_size(self):
        return self.ip.supernet.get_network().size

    def get_prefixlen(self):
        return self.ip.supernet.get_network().prefixlen

    def get_cidr(self):
        return str(self.ip.supernet.get_network().cidr)

    def get_broadcast(self):
        return str(self.ip.supernet.get_network().broadcast)

    def get_gateway_prefixlen(self):
        return self.gateway_public_ip.supernet.get_network().prefixlen

    def get_slice_id(self):
        return self.slice.id

    def get_user_keys(self):
        user = self.slice.owner
        ssh_keys = []
        for i in SSHKey.objects.filter(user=user):
            ssh_keys.append(i.sshkey)
        return ssh_keys

    def create_vm(self):
        if function_test:
            print '----------------------create a vm=%s -------------------------' % self.name
        else:
            vmInfo = {}
            vmInfo['name'] = self.uuid
            vmInfo['mem'] = self.flavor.ram
            vmInfo['cpus'] = self.flavor.cpu
            vmInfo['img'] = self.image.uuid
            vmInfo['hdd'] = self.flavor.hdd
            vmInfo['glanceURL'] = self.image.url
            vmInfo['type'] = self.type
            vmInfo['network'] = []
            network = {}
            network['address'] = self.get_ipaddr() + '/' + str(self.get_prefixlen())
            network['gateway'] = self.ip.supernet.get_gateway_ip()
            vmInfo['network'].append(network)
            if self.gateway_public_ip:
                network = {}
                network['address'] = self.gateway_public_ip.ipaddr + '/' + str(self.gateway_public_ip.supernet.get_network().prefixlen)
                network['gateway'] = self.gateway_public_ip.supernet.get_gateway_ip()
                vmInfo['network'].append(network)
            keys = self.get_user_keys()
            str_keys = '\n'.join(keys)
            agent_client = AgentClient(self.server.ip)
            agent_client.create_vm(vmInfo, key=str_keys)

    def delete_vm(self):
        try:
            if function_test:
                print '----------------------delete a vm=%s -------------------------' % self.name
            else:
                agent_client = AgentClient(self.server.ip)
                agent_client.delete_vm(self.uuid)
        except socket_error as serr:
            if serr.errno == errno.ECONNREFUSED or serr.errno == errno.EHOSTUNREACH:
                raise ConnectionRefused()

    def do_action(self, action):
        if function_test:
            print '----------------------vm action=%s-------------------------' % action
            result = True
        else:
            agent_client = AgentClient(self.server.ip)
            switch_port = self.switch_port
            if switch_port:
                ofport = switch_port.port
            else:
                ofport = None
            result = agent_client.do_domain_action(self.uuid, action, ofport)
        return result

    def add_sshkeys(self, key):
        if function_test:
            print '-------------------add ssh key = %s----------------------------' % key
        else:
            agent_client = AgentClient(self.server.ip)
            agent_client.add_sshkeys(self.uuid, key)

    def delete_sshkeys(self, key):
        if function_test:
            print '-------------------del ssh key = %s----------------------------' % key
        else:
            agent_client = AgentClient(self.server.ip)
            agent_client.delete_sshkeys(self.uuid, key)

    class Meta:
        verbose_name = _("Virtual Machine")


class SSHKey(models.Model):
    user = models.ForeignKey(User)
    title = models.CharField(max_length=256)
    sshkey = models.CharField(max_length=500)
    vms = models.ManyToManyField(VirtualMachine)

    def __unicode__(self):
        return self.title

    class Meta:
        #unique_together = (("user", "sshkey"), )
        verbose_name = _("SSH Keys")


class HostMac(models.Model):
    mac = models.CharField(max_length=32)
    host_type = models.ForeignKey(ContentType)
    host_id = models.PositiveIntegerField()
    #: the switch that the rule is applied on, can be Switch or VirtualSwitch
    host = generic.GenericForeignKey('host_type', 'host_id')

    class Meta:
        verbose_name = _("Host Mac")


@receiver(pre_save, sender=VirtualMachine)
def vm_pre_save(sender, instance, **kwargs):
    if not instance.ip:
        instance.ip = IPUsage.objects.allocate_ip(instance.slice.uuid)
    if not instance.uuid:
        instance.uuid = utils.gen_uuid()
    if not instance.mac:
        instance.mac = utils.generate_mac_address(instance.get_ipaddr())
    if not instance.state:
        instance.state = DOMAIN_STATE_DIC['building']


@receiver(post_save, sender=VirtualMachine)
def vm_post_save(sender, instance, **kwargs):
    if kwargs.get('created'):
        instance.create_vm()


@receiver(pre_delete, sender=VirtualMachine)
def vm_pre_delete(sender, instance, **kwargs):
    instance.delete_vm()
    if instance.type == 0:
        controllers = Controller.objects.filter(object_id=instance.id)
        controllers.delete()


@receiver(post_delete, sender=VirtualMachine)
def vm_post_delete(sender, instance, **kwargs):
    IPUsage.objects.release_ip(instance.ip)
    if instance.gateway_public_ip:
        IPUsage.objects.release_ip(instance.gateway_public_ip)
    try:
        if instance.switch_port:
            instance.switch_port.delete()
    except:
        pass


@receiver(post_save, sender=SSHKey)
def sshkey_post_save(sender, instance, **kwargs):
    if kwargs.get('created'):
        slices = Slice.objects.filter(owner=instance.user)
        for slice in slices:
            for vm in slice.get_vms():
                vm.add_sshkeys(instance.sshkey)


@receiver(post_delete, sender=SSHKey)
def sshkey_post_delete(sender, instance, **kwargs):
    vms = instance.vms.all()
    for vm in vms:
        vm.delete_sshkeys(instance.sshkey)
