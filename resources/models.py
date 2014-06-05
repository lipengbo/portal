#coding: utf-8

from django.db import models
from django.db.models.base import ModelBase
from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext as _

from plugins.common.agent_client import AgentClient
from etc.config import function_test

from project.models import Island
from slice.models import Slice

OVS_TYPE = {'NOMAL': 1, 'EXTERNAL': 2, 'RELATED': 3}
PORT_MONOPOLIZE = 0
PORT_SHARE = 1
PORT_TYPES = ((PORT_MONOPOLIZE, 'port_monopolize'),
              (PORT_SHARE, 'port_share'),)

class ResourceBase(ModelBase):

    def __init__(cls, name, bases, attrs):
        if not hasattr(cls, 'registry'):
            # this is the base class.  Create an empty registry
            cls.registry = {}
        else:
            # this is a derived class.  Add cls to the registry
            interface_id = name.lower()
            cls.registry[interface_id] = cls
        return super(ResourceBase, cls).__init__(name, bases, attrs)


class Resource(models.Model):

    __metaclass__ = ResourceBase

    name = models.CharField(max_length=128, verbose_name=_("name"), help_text=_("Please entitled with Server+IP"))

    def on_create_slice(self):
        pass

    def on_delete_slice(self):
        pass

    def on_start_slice(self):
        pass

    def on_add_into_slice(self, slice_obj):
        pass

    def on_remove_from_slice(self, slice_obj):
        pass

    def __unicode__(self):
        return self.name

    class Meta:
        abstract = True


class IslandResource(Resource):
    island = models.ForeignKey(Island, verbose_name=_("Island"))

    class Meta:
        abstract = True


class ServiceResource(IslandResource):
    ip = models.IPAddressField(verbose_name="IP")
    password = models.CharField(max_length=20, verbose_name=_("password"))
    slices = models.ManyToManyField(Slice, blank=True)
    #state = models.IntegerField(choices=((0, _("Stopped")), (1, _("Started"))), default=1, verbose_name=_("state"))

    def __unicode__(self):
        return self.name

    class Meta:
        abstract = True


class Server(IslandResource):
    username = models.CharField(max_length=20, verbose_name=_("username"))
    password = models.CharField(max_length=20, verbose_name=_("password"))
    state = models.IntegerField(null=True, verbose_name=_("state"), choices=((0, _("Not available")), (1, _("Available"))))
    cpu = models.CharField(max_length=256, null=True, default=0, verbose_name="CPU")
    mem = models.IntegerField(null=True, default=0, verbose_name=_("memory"))
    #bandwidth = models.IntegerField(null=True, default=0, verbose_name=_("bandwidth"))
    disk = models.IntegerField(null=True, default=0, verbose_name=_("disk"))
    ip = models.IPAddressField(null=False, unique=True, verbose_name="IP")
    #mac = models.CharField(max_length=256, null=True)
    os = models.CharField(max_length=256, blank=True, null=True, verbose_name=_("os"))
    update_time = models.DateTimeField(auto_now_add=True)

    def get_link_vs(self):
        virtualswitchs = self.virtualswitch_set.all()
        if virtualswitchs:
            return virtualswitchs[0]
        else:
            return None

    @staticmethod
    def admin_options():
        options = {
            'exclude_fields': ('name', 'password', 'username', 'disk', 'mem', 'bandwidth'),
            'form_exclude_fields': ('cpu', 'disk', 'mem'),
            'related_models': [{'app_label': 'resources', 'model': 'virtualswitch'}],
        }
        return options

    class Meta:
        verbose_name = _("Server")


class SwitchResource(IslandResource):
    ip = models.IPAddressField(verbose_name="IP")
    username = models.CharField(max_length=20, verbose_name=_("username"), help_text="用户名和密码是交换机所在服务器的系统用户名和密码")
    password = models.CharField(max_length=20, verbose_name=_("password"))
    dpid = models.CharField(max_length=256, help_text="dpid以冒号“:”分隔", verbose_name="DPID")
    has_gre_tunnel = models.BooleanField(default=False, verbose_name=_("Has GRE tunnel"))
    slices = models.ManyToManyField(Slice, through="SliceSwitch")

    def __unicode__(self):
        return self.name

    class Meta:
        abstract = True


class Switch(SwitchResource):

    def on_add_into_slice(self, slice_obj):
        SliceSwitch.objects.get_or_create(switch=self, slice=slice_obj)

    def is_virtual(self):
        try:
            self.virtualswitch
        except VirtualSwitch.DoesNotExist:
            return False
        else:
            return True

    def on_remove_from_slice(self, slice_obj):
        slice_switches = SliceSwitch.objects.filter(
            switch=self, slice=slice_obj)
        slice_switches.delete()

    def type(self):
        if self.has_gre_tunnel:
            return OVS_TYPE['NOMAL']
        try:
            self.virtualswitch
        except VirtualSwitch.DoesNotExist:
            return OVS_TYPE['NOMAL']
        else:
            return OVS_TYPE['RELATED']

    def get_edge_ports(self):
        from plugins.openflow.models import Link
        edge_ports = []
        ports = self.switchport_set.all()
        for port in ports:
            links_src_c = Link.objects.filter(source=port).count()
            links_tag_c = Link.objects.filter(target=port).count()
            if links_src_c + links_tag_c == 0:
                edge_ports.append(port)
        return edge_ports

    @staticmethod
    def admin_options():
        options = {
            'exclude_fields': ('switch_ptr', 'port', 'http_port', 'has_gre_tunnel', 'name', 'password', 'username'),
        }
        return options

    class Meta:
        verbose_name = _("Switch")


class SliceSwitch(models.Model):
    slice = models.ForeignKey(Slice)
    switch = models.ForeignKey(Switch)

    class Meta:
        unique_together = (("slice", "switch"), )
        verbose_name = _("Slice Switch")


class SwitchPort(Resource):

    #: the switch that the rule is applied on, can be Switch or VirtualSwitch
    switch = models.ForeignKey(Switch)
    port = models.IntegerField()
    slices = models.ManyToManyField(Slice, through="SlicePort", blank=True)

    def __unicode__(self):
        return '{} - {}'.format(self.switch, self.port)

    def on_add_into_slice(self, slice_obj):
        SlicePort.objects.get_or_create(
            switch_port=self, slice=slice_obj)
        slice_switches = SliceSwitch.objects.filter(
            slice=slice_obj, switch=self.switch)
        if not slice_switches:
            slice_obj.add_resource(self.switch)

    def on_remove_from_slice(self, slice_obj):
        slice_ports = SlicePort.objects.filter(
            switch_port=self, slice=slice_obj)
        for slice_port in slice_ports:
            switch = slice_port.switch_port.switch
            slice_port.delete()
            if not slice_obj.get_switch_ports().filter(switch=switch):
                slice_obj.remove_resource(switch)

    def can_monopolize(self):
        slice_ports_c = SlicePort.objects.filter(switch_port=self).count()
        if slice_ports_c > 0:
            return False
        else:
            return True

    def monopolized(self):
        slice_ports_c = SlicePort.objects.filter(switch_port=self, type=0).count()
        if slice_ports_c > 0:
            return True
        else:
            return False

    def is_edge(self):
        from plugins.openflow.models import Link
        links_src_c = Link.objects.filter(source=self).count()
        links_tag_c = Link.objects.filter(target=self).count()
#         print self, links_src_c, links_tag_c
        if links_src_c + links_tag_c == 0:
            return True
        else:
            return False

    def log_info(self):
        return u'交换机名称：'+ self.switch.name + '\n'+ \
                u'接入端口：' + str(self.port)

    class Meta:
        unique_together = (("switch", "port"), )
        verbose_name = _("Switch Port")


class SlicePort(models.Model):
    slice = models.ForeignKey(Slice)
    switch_port = models.ForeignKey(SwitchPort)
    type = models.IntegerField(choices=PORT_TYPES,
                               default=PORT_SHARE)

    class Meta:
        unique_together = (("slice", "switch_port"), )
        verbose_name = _("Slice Port")


class OwnerDevice(models.Model):
    mac_list = models.CharField(max_length=1024)
    slice_port = models.ForeignKey(SlicePort)

    class Meta:
        verbose_name = _("Owner Device")


class VirtualSwitch(Switch):

    """
        A virtual switch service that created on a Physical Server
    """
    server = models.ForeignKey(Server, verbose_name=_("Server"))

    def get_vms(self, slice_obj):
        return slice_obj.get_vms.filter(server=self.server)

    class Meta:
        verbose_name = _("Virtual Switch")


@receiver(pre_save, sender=Server)
def vm_pre_save(sender, instance, **kwargs):
    if not function_test:
        agent_client = AgentClient(instance.ip)
        try:
            info = agent_client.get_host_info(timeout=5)
            instance.cpu = info['cpu']
            instance.mem = info['mem']
            instance.disk = info['hdd']
            instance.os = info['os']
            instance.state = 1
        except:
            instance.state = 0
