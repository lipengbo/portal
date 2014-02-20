#coding: utf-8

import hashlib
import json
import logging

logger = logging.getLogger("plugins")

from django.db import models
from django.db import transaction
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.db.models import F
from django.dispatch import receiver
from django.conf import settings
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext as _

from resources.models import ServiceResource, Resource, \
        SwitchPort, Switch, Server, VirtualSwitch
from slice.models import Slice


class Controller(ServiceResource):
    username = models.CharField(max_length=20, verbose_name=_("username"))
    is_root = models.BooleanField(default=False)
    port = models.IntegerField()
    content_type = models.ForeignKey(ContentType, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    #: served on a ComputeResource like Server or VirtualMachine
    host = generic.GenericForeignKey('content_type', 'object_id')

    def on_add_into_slice(self, slice_obj):
        self.slices.add(slice_obj)

    def on_remove_from_slice(self, slice_obj):
        self.slices.remove(slice_obj)

    def is_used(self):
        return self.slices.all().count() > 0

    class Meta:
        verbose_name = _("Controller")


class Flowvisor(ServiceResource):
    def __init__(self, *args, **kwargs):
        password = self._meta.get_field('password')
        password.help_text = '填写flowvisor密码'
        super(Flowvisor, self).__init__(*args, **kwargs)

    http_port = models.IntegerField(verbose_name=_("Http Port"))

    def on_add_into_slice(self, slice_obj):
        self.slices.add(slice_obj)

    @staticmethod
    def admin_options():
        options = {
            'exclude_fields': ('name', 'password', 'username', 'port', 'http_port', 'content_type', 'object_id'),
            'ct_model': ('resources', 'server')
        }
        return options

    def validate_unique(self, exclude=None):
        if not self.id:
            try:
                Flowvisor.objects.get(name=self.name)
                e = ValidationError(_("%(model_name)s with this %(field_label)s already exists.") % {"field_label": self._meta.get_field('name').verbose_name, "model_name": self._meta.verbose_name})
                e.message_dict = {}
                e.message_dict["name"] = e.messages
                raise e
            except Flowvisor.DoesNotExist:
                return self.name
        super(Flowvisor, self).validate_unique(exclude)

    class Meta:
        verbose_name = _("Flowvisor")


class FlowSpaceRule(Resource):
    slice = models.ForeignKey(Slice)
    switch = models.ForeignKey(Switch, null=True)
    priority = models.IntegerField()
    in_port = models.CharField(max_length=256)
    dl_vlan = models.CharField(max_length=256)
    dl_vpcp = models.CharField(max_length=256)
    dl_src = models.CharField(max_length=256)
    dl_dst = models.CharField(max_length=256)
    dl_type = models.CharField(max_length=256)
    nw_src = models.CharField(max_length=256)
    nw_dst = models.CharField(max_length=256)
    nw_proto = models.CharField(max_length=256)
    nw_tos = models.CharField(max_length=256)
    tp_src = models.CharField(max_length=256)
    tp_dst = models.CharField(max_length=256)
    is_default = models.IntegerField()
    actions = models.CharField(max_length=256)

class Link(models.Model):

    flowvisor = models.ForeignKey(Flowvisor)
    source = models.ForeignKey(SwitchPort, related_name="source_links")
    target = models.ForeignKey(SwitchPort, related_name="target_links")

    class Meta:
        verbose_name = _("Link")

class FlowvisorLinksMd5(models.Model):
    md5 = models.CharField(max_length=32)
    flowvisor = models.OneToOneField(Flowvisor)

    class Meta:
        verbose_name = _("Flowvisor link md5")

@receiver(post_save, sender=Flowvisor)
def update_links(sender, instance, created, **kwargs):
    if settings.DEBUG and not hasattr(settings, "CAN_FETCH_FLOWVISOR"):
        return
    from plugins.openflow.flowvisor_api import flowvisor_get_switches, flowvisor_get_links
#     import pdb;pdb.set_trace()
    port_name_dict = {}
    try:
        switches = flowvisor_get_switches(instance)
    except Exception, e:
        print e
        return
    else:
        for switch in switches:
            dpid = switch['dpid']
            port_name_dict[dpid] = {}
            for port in switch['ports']:
                port_name_dict[dpid][port['portNumber']] = port['name']
        create_virtualswitch(instance.island, switches)
    try:
        links = flowvisor_get_links(instance)
    except Exception, e:
        print e
        return
    digest = hashlib.md5(json.dumps(links)).hexdigest()
    try:
        md5_obj = instance.flowvisorlinksmd5
        if md5_obj.md5 == digest: #: if the digests are the same, then no update
            return
        else: #: or update the md5 digest and do the updates and deletions
            md5_obj.md5 = digest
            md5_obj.save()
    except FlowvisorLinksMd5.DoesNotExist:
        #: if it's the first time update, create a md5 record
        FlowvisorLinksMd5(md5=digest, flowvisor=instance).save()

    #: delete all existing links and ports
    instance.link_set.all().delete()

    for link in links:
        src_port = link['src-port']
        dst_port = link['dst-port']
        try:
            source_switch = Switch.objects.get(dpid=link['src-switch'])
        except Switch.DoesNotExist, e:
            logger.error('========== FETCHING ' + link['src-switch'] + " ==========")
            raise Exception(u"DPID为" + link['src-switch'] + u"的交换机没有录入")
        try:
            target_switch = Switch.objects.get(dpid=link['dst-switch'])
        except Switch.DoesNotExist, e:
            logger.error('========== FETCHING ' + link['dst-switch'] + " ==========")
            raise Exception(u"DPID为" + link['dst-switch'] + u"的交换机没有录入")
        try:
            src_port_name = port_name_dict[source_switch.dpid][int(src_port)]
        except KeyError:
            src_port_name = 'eth' + src_port
        try:
            dst_port_name = port_name_dict[target_switch.dpid][int(dst_port)]
        except KeyError:
            dst_port_name = 'eth' + dst_port
        source_port, created = SwitchPort.objects.get_or_create(
                switch=source_switch,
                port=src_port,
                defaults={'name': src_port_name})
        target_port, created = SwitchPort.objects.get_or_create(
                switch=target_switch,
                port=dst_port,
                defaults={'name': dst_port_name})

        link_obj = Link(flowvisor=instance,
                source=source_port,
                target=target_port)
        link_obj.save()

    for dpid, port_entry in port_name_dict.items():
        source_switch = Switch.objects.get(dpid=dpid)
        for port_num, port_name in port_entry.items():
            source_port, created = SwitchPort.objects.get_or_create(
            switch=source_switch,
            port=port_num,
            defaults={'name': port_name})

def create_virtualswitch(island, datapaths):
    for datapath in datapaths:
        dpid = datapath['dpid']
        if dpid.startswith('00:ff:'):# only virtual switch
            target_switch = datapath['target_switch']
            ip = target_switch[0]
            try:
                server = Server.objects.get(ip=ip)
            except Server.DoesNotExist, e:
                logger.error('============= IP: ' + ip + '=============')
                raise Exception(u"IP为" + ip + u"的服务器没有录入")
            virtual_switch, created = VirtualSwitch.objects.get_or_create(dpid=dpid,
                    ip=ip, defaults={'name': "v-ovs" + str(VirtualSwitch.objects.count() + 1), 'island': island, 'password': '123', 'username': 'admin', 'server': server})

