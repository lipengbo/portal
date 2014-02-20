from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_delete, pre_delete
from django.db.models import F
from django.dispatch import receiver
from django.utils.translation import ugettext as _


from project.models import Project, Island
from plugins.ipam.models import Subnet
from common.views import increase_failed_counter, decrease_failed_counter, decrease_counter_api
from plugins.openflow.flowvisor_api import flowvisor_del_slice

import datetime

SLICE_STATE_STOPPED = 0
SLICE_STATE_STARTED = 1
SLICE_TYPE_USABLE = 0
SLICE_TYPE_DELETE = 1
USER_DELETE = 0
ADMINISTRATOR_DELETE = 1
EXPIRED_DELETE = 2
SLICE_STATES = ((SLICE_STATE_STOPPED, 'stopped'),
                (SLICE_STATE_STARTED, 'started'),)
SLICE_TYPES = ((SLICE_TYPE_USABLE, 'usable'),
                (SLICE_TYPE_DELETE, 'delete'),)
SLICE_DELETE_TYPE = ((USER_DELETE, 'usable'),
                     (ADMINISTRATOR_DELETE, 'administrator'),
                     (EXPIRED_DELETE, 'expired'),)
# Create your models here.


class Slice(models.Model):
    owner = models.ForeignKey(User)
    name = models.CharField(max_length=256)
    show_name = models.CharField(max_length=256)
    description = models.CharField(max_length=1024)
    project = models.ForeignKey(Project)
    date_created = models.DateTimeField(auto_now_add=True)
    date_expired = models.DateTimeField()
    state = models.IntegerField(choices=SLICE_STATES,
                                default=SLICE_STATE_STOPPED)
    type = models.IntegerField(choices=SLICE_TYPES,
                               default=SLICE_TYPE_USABLE)
    failure_reason = models.TextField()
    islands = models.ManyToManyField(Island, through="SliceIsland")
    uuid = models.CharField(max_length=36, null=True, unique=True)

    def created_date(self):
        return self.date_created

    def add_island(self, island):
        SliceIsland.objects.get_or_create(
            island=island, slice=self)

    def change_description(self, description):
        self.description = description
        self.save()

    def add_resource(self, resource):
        resource.on_add_into_slice(self)

    def remove_resource(self, resource):
        resource.on_remove_from_slice(self)

    def stop(self):
        self.state = SLICE_STATE_STOPPED
        self.save()

    def start(self):
        self.state = SLICE_STATE_STARTED
        self.save()

    def get_flowvisor(self):
        flowvisors = self.flowvisor_set.all()
        if flowvisors:
            return flowvisors[0]
        else:
            return None

    def get_controller(self):
        controllers = self.controller_set.all()
        if controllers:
            return controllers[0]
        else:
            return None

    def get_island(self):
        islands = self.islands.all()
        if islands:
            return islands[0]
        else:
            return None

    def get_switches(self):
        controller_vms = self.get_controller_vms()
        swich_ids = []
        for controller_vm in controller_vms:
            if controller_vm.switch_port:
                if self.switchport_set.filter(switch=controller_vm.switch_port.switch).count() == 1:
                    swich_ids.append(controller_vm.switch_port.switch.id)
        return self.switch_set.exclude(id__in=swich_ids)

    def get_virtual_switches(self):
        from resources.models import VirtualSwitch
        switches = self.get_switches()
        virtual_switches = []
        for switch in switches:
            if switch.is_virtual():
                virtual_switches.append(switch.virtualswitch)
        return virtual_switches

    def get_virtual_switches_gre(self):
        from resources.models import VirtualSwitch
        switches = self.get_switches()
        virtual_switches = []
        for switch in switches:
            if switch.is_virtual() and switch.has_gre_tunnel:
                virtual_switches.append(switch.virtualswitch)
        return virtual_switches

    def get_virtual_switches_server(self):
        from resources.models import VirtualSwitch
        switches = self.get_switches()
        virtual_switches = []
        for switch in switches:
            if switch.is_virtual() and not switch.has_gre_tunnel:
                virtual_switches.append(switch.virtualswitch)
        return virtual_switches

    def get_default_flowspaces(self):
        return self.flowspacerule_set.filter(is_default=1)

    def get_switch_ports(self):
        return self.switchport_set.all()

    def get_one_switch_ports(self, switch):
        return self.switchport_set.filter(switch=switch)

    def get_vms(self):
        return self.virtualmachine_set.all()

    def get_common_vms(self):
        return self.virtualmachine_set.filter(type=1)

    def get_controller_vms(self):
        return self.virtualmachine_set.filter(type=0)

    def get_nws(self):
        default_flowspaces = self.flowspacerule_set.filter(is_default=1, dl_type='0x800')
        nws = []
        for default_flowspace in default_flowspaces:
            if default_flowspace.nw_src != '' and default_flowspace.nw_src == default_flowspace.nw_dst:
                nws.append(default_flowspace.nw_dst)
        return nws

    def get_nw(self):
        try:
            nw_obj = Subnet.objects.get(owner=self.uuid)
            return nw_obj.netaddr
        except:
            return None

    def get_nw_num(self):
        nw = self.get_nw()
        nw_num = 0
        if nw:
            nw_num = 1
            num = int(nw.split('/')[1])
            for i in range(0, (32 - num)):
                nw_num = 2 * nw_num
        return nw_num

    def get_gws(self):
        default_flowspaces = self.flowspacerule_set.filter(is_default=1, dl_type='0x800')
        gws = []
        for default_flowspace in default_flowspaces:
            if default_flowspace.dl_src != '':
                gws.append(default_flowspace.dl_src)
        return gws

    def get_gw(self):
        gws = self.virtualmachine_set.filter(type=2)
        if gws:
            return gws[0]
        else:
            return None

    def get_dhcp(self):
        gws = self.virtualmachine_set.filter(type=2, enable_dhcp=True)
        if gws:
            return gws[0]
        else:
            return None

    def set_dhcp(self, flag):
        gws = self.virtualmachine_set.filter(type=2)
        if gws:
            print "------------", flag
            if flag == '1':
                gws[0].enable_dhcp = True
            else:
                gws[0].enable_dhcp = False
            gws[0].save()
            return True
        else:
            return False

    def get_dhcp_vm_macs(self):
        default_flowspaces = self.flowspacerule_set.filter(is_default=1, dl_type='')
        dhcp_vm_macs = []
        for default_flowspace in default_flowspaces:
            if default_flowspace.dl_src != '':
                dhcp_vm_macs.append(default_flowspace.dl_src)
        return dhcp_vm_macs

    def get_show_name(self):
        return self.show_name

    def be_count(self):
        sc = SliceCount.objects.filter(date_created__year=self.date_created.strftime('%Y'),
                                  date_created__month=self.date_created.strftime('%m'),
                                  date_created__day=self.date_created.strftime('%d'))
        if sc:
            sc[0].num = sc[0].num + 1
            sc[0].save()
        else:
            nsc = SliceCount(date_created=self.date_created,
                             num=1)
            nsc.save()

    def delete(self, *args, **kwargs):
        try:
            print "1:delete slice on flowvisor"
            flowvisor_del_slice(self.get_flowvisor(), self.id)
            print "2:delete slice record"
            super(self.__class__, self).delete(*args, **kwargs)
            print "3:delete slice record success"
        except Exception, ex:
            print "4:delete slice failed and change slice record"
            self.failure_reason = ex.message
            if self.type == 0:
                self.type = 1
                increase_failed_counter("slice")
                decrease_counter_api("slice", self)
            else:
                decrease_failed_counter("slice", self)
                increase_failed_counter("slice")
            self.date_expired = datetime.datetime.now()
            self.save()
            print "5:raise exception"
            raise

    def __unicode__(self):
        return self.name

    class Meta:
        permissions = (
            ('view_slice', _('View Slice')),
        )

class SliceDeleted(models.Model):
    name = models.CharField(max_length=256)
    show_name = models.CharField(max_length=256)
    owner_name = models.CharField(max_length=256)
    description = models.TextField()
    project_name = models.CharField(max_length=256)
    date_created = models.DateTimeField()
    date_expired = models.DateTimeField()
    date_deleted = models.DateTimeField(auto_now_add=True)
    type = models.IntegerField(choices=SLICE_DELETE_TYPE,
                               default=USER_DELETE)

    def __unicode__(self):
        return self.name


class SliceIsland(models.Model):
    slice = models.ForeignKey(Slice)
    island = models.ForeignKey(Island)

    class Meta:
        unique_together = (("slice", "island"), )


class SliceCount(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    num = models.IntegerField(default=1)

    class Meta:
        verbose_name = ("slice count")


@receiver(pre_delete, sender=Slice)
def pre_delete_slice(sender, instance, **kwargs):
    print "pre delete slice"
    from slice.slice_api import delete_slice_api
    delete_slice_api(instance)


# @receiver(post_delete, sender=Slice)
# def post_delete_slice(sender, instance, **kwargs):
#     print "delete post"
#     if instance.id:
#         print "s1"
#     else:
#         print "s2"
#     if instance.project:
#         print "s3"
#     else:
#         print "s4"
#     try:
#         flowvisor_del_slice(instance.get_flowvisor(), instance.id)
#     except:
#         raise
