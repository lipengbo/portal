#coding: utf-8
import os
import tempfile
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete, pre_delete, pre_save
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db.models import Sum

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
import logging
LOG = logging.getLogger('plugins')
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
    (10, _('not exist')),
    (11, _('resource not enough')),
    (12, _('starting')),
    (13, _('stopping')),
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
    'resource not enough': 11,
    'starting': 12,
    'stopping': 13
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
    type = models.IntegerField(null=True, choices=VM_TYPE)
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


class VirtualMachineManager(models.Manager):

    def user_stat_sum(self, user, kind):
        total = 0
        for slice in user.slice_set.filter(type=0):
            num = slice.virtualmachine_set.filter(type=1).exclude(state__in=(9,10,11)).aggregate(Sum(kind))[kind+'__sum']
            if num:
                total += num
        return total

    def total_vms(self, user):
        total = 0
        for slice in user.slice_set.filter(type=0):
            total += slice.virtualmachine_set.filter(type=1).exclude(state__in=(9,10,11)).count()
        return total

class VirtualMachine(IslandResource):
    uuid = models.CharField(max_length=36, null=True, unique=True)
    ip = models.ForeignKey(IPUsage, null=True, related_name="virtualmachine_set")
    gateway_public_ip = models.ForeignKey(IPUsage, null=True, related_name="gateway_set")
    mac = models.CharField(max_length=20, null=True)
    cpu = models.IntegerField(null=True)
    ram = models.IntegerField(null=True)
    hdd = models.IntegerField(null=True)
    enable_dhcp = models.BooleanField(default=False)
    slice = models.ForeignKey(Slice)
    flavor = models.ForeignKey(Flavor, null=True)
    image = models.ForeignKey(Image)
    server = models.ForeignKey(Server)
    switch_port = models.ForeignKey(SwitchPort, null=True)
    state = models.IntegerField(null=True, choices=DOMAIN_STATE_TUPLE)
    type = models.IntegerField(null=False, choices=VM_TYPE)

    objects = VirtualMachineManager()

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

    def log_info(self):
        if self.type == 2:
            return u'网关名称：'+ self.name +'\n' + u'网关地址：' + self.ip.ipaddr
        elif self.type == 0:
            return u'控制器类型：' + self.name +'\n'+u'控制器地址：'+ self.ip.ipaddr
        else:
            return u"虚拟机名称："+ self.name

    def create_vm(self):
        if function_test:
            print '----------------------create a vm=%s -------------------------' % self.name
        else:
            vmInfo = {}
            if self.flavor is None:
                vmInfo['mem'] = self.ram
                vmInfo['cpus'] = self.cpu
                vmInfo['hdd'] = self.hdd
            else:
                vmInfo['mem'] = self.flavor.ram
                vmInfo['cpus'] = self.flavor.cpu
                vmInfo['hdd'] = self.flavor.hdd

            vmInfo['name'] = self.uuid
            vmInfo['img'] = self.image.uuid
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
            keys = []
            sshkeys = self.slice.sshkey_set.all()
            for key in sshkeys:
                keys.append(key.public_key)
            str_keys = '\n'.join(keys)
            agent_client = AgentClient(self.server.ip)
            agent_client.create_vm(vmInfo, key=str_keys)

    def delete_vm(self):
        try:
            if function_test:
                print '----------------------delete a vm=%s -------------------------' % self.name
            else:
                kk
                agent_client = AgentClient(self.server.ip)
                agent_client.delete_vm(self.uuid)
                print "++++++++++++++++++++++++++++++++++"
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
            print action, "**************", result
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
    slice = models.ForeignKey(Slice)
    name = models.CharField(max_length=256)
    public_key = models.CharField(max_length=500, blank=True)
    private_key = models.CharField(max_length=2048, blank=True)
    fingerprint = models.CharField(max_length=250, blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        unique_together = (("fingerprint"), )
        verbose_name = _("SSH Keys")

    def _generate_fingerprint(self, public_key_file):
        out = utils.execute(['ssh-keygen', '-q', '-l', '-f', public_key_file])
        fingerprint = out.split(' ')[1]
        return fingerprint

    def generate_key_pair(self, bits=None):
        try:
            tmpdir = tempfile.mkdtemp()
            keyfile = os.path.join(tmpdir, 'temp')
            args = ['ssh-keygen', '-q', '-N', '', '-t', 'rsa',
                    '-f', keyfile, '-C', 'Generated by ccf']
            if bits is not None:
                args.extend(['-b', bits])
            utils.execute(args)
            fingerprint = self._generate_fingerprint('%s.pub' % (keyfile))
            if not os.path.exists(keyfile):
                raise Exception('%s not found' % keyfile)
            private_key = open(keyfile).read()
            public_key_path = keyfile + '.pub'
            if not os.path.exists(public_key_path):
                raise Exception('%s not found' % public_key_path)
            public_key = open(public_key_path).read()
        except:
            raise
        finally:
            if os.path.exists(tmpdir):
                utils.execute(['rm', '-rf', tmpdir])
        return (private_key, public_key, fingerprint)


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
    if not instance.uuid:
        instance.uuid = utils.gen_uuid()
        if instance.type == 1:
            instance.name = "VM-" + instance.uuid.split("-")[0]
    #if instance.state == 11:
    #    return
    if not instance.ip:
        instance.ip = IPUsage.objects.allocate_ip(instance.slice.uuid, instance.type)
    if not instance.mac:
        instance.mac = utils.generate_mac_address(instance.get_ipaddr())
    if not instance.state:
        instance.state = DOMAIN_STATE_DIC['building']


@receiver(post_save, sender=VirtualMachine)
def vm_post_save(sender, instance, **kwargs):
    if instance.state == 11:
        return
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
        slice = instance.slice
        for vm in slice.get_vms():
            instance.vms.add(vm)
            vm.add_sshkeys(instance.sshkey)


@receiver(post_save, sender=Slice)
def slice_post_save(sender, instance, **kwargs):
    if kwargs.get('created'):
        try:
            sshkey = SSHKey()
            sshkey.slice = instance
            sshkey.name = '%s_key' % instance.name
            sshkey.private_key, sshkey.public_key, sshkey.fingerprint = sshkey.generate_key_pair()
            sshkey.save()
        except:
            import traceback
            LOG.error(traceback.print_exc())

#@receiver(post_delete, sender=SSHKey)
#def sshkey_post_delete(sender, instance, **kwargs):
    #vms = instance.vms.all()
    #for vm in vms:
        #vm.delete_sshkeys(instance.sshkey)
