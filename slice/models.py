# coding:utf-8
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_delete, pre_delete
from django.db.models import F
from django.dispatch import receiver
from django.utils.translation import ugettext as _
from django.db import transaction


from project.models import Project, Island
from plugins.ipam.models import Subnet, IPUsage
from common.views import increase_failed_counter, decrease_failed_counter, decrease_counter_api
from plugins.openflow.virttool_api import virttool_del_slice
from slice.slice_exception import DbError
from adminlog.models import log, SUCCESS, FAIL

import datetime

SLICE_STATE_STOPPED = 0
SLICE_STATE_STARTED = 1
SLICE_STATE_STOPPING = 3
SLICE_STATE_STARTING = 4

SLICE_TYPE_USABLE = 0
SLICE_TYPE_DELETE = 1
USER_DELETE = 0
ADMINISTRATOR_DELETE = 1
EXPIRED_DELETE = 2
SLICE_STATES = ((SLICE_STATE_STOPPED, 'stopped'),
                (SLICE_STATE_STARTED, 'started'),
                (SLICE_STATE_STOPPING, 'stopping'),
                (SLICE_STATE_STARTING, 'starting'),)
VPN_STATES = SLICE_STATES
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
    changed = models.IntegerField(null=True)
    ct_change = models.NullBooleanField(null=True)
    vm_num = models.IntegerField(default=0)
    vpn_state = models.IntegerField(choices=VPN_STATES, default=0)

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
        self.changed = 0
        self.save()

    def starting(self):
        self.state = SLICE_STATE_STARTING
        self.save()

    def stopping(self):
        self.state = SLICE_STATE_STOPPING
        self.save()

    def get_virttool(self):
        virttools = self.virttool_set.all()
        if virttools:
            return virttools[0]
        else:
            return None

    def get_controller(self):
        controllers = self.controller_set.all().order_by("-id")
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
        return self.switch_set.all()
#         controller_vms = self.get_controller_vms()
#         swich_ids = []
#         for controller_vm in controller_vms:
#             if controller_vm.switch_port:
#                 if self.switchport_set.filter(switch=controller_vm.switch_port.switch).count() == 1:
#                     swich_ids.append(controller_vm.switch_port.switch.id)
#         return self.switch_set.exclude(id__in=swich_ids)

    def get_normal_switches(self):
        switches = self.get_switches()
        normal_switches = []
        for switch in switches:
            if not switch.is_virtual():
                normal_switches.append(switch)
        return normal_switches

    def get_virtual_switches(self):
        switches = self.get_switches()
        virtual_switches = []
        for switch in switches:
            if switch.is_virtual():
                virtual_switches.append(switch.virtualswitch)
        return virtual_switches

    def get_servers(self):
        switches = self.get_switches()
        servers = []
        for switch in switches:
            if switch.is_virtual():
                servers.append(switch.virtualswitch.server)
        return servers

    def get_gre_switches(self):
        switches = self.get_switches()
        gre_switches = []
        for switch in switches:
            if switch.has_gre_tunnel:
                gre_switches.append(switch)
        return gre_switches

    def get_virtual_switches_server(self):
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
        return self.virtualmachine_set.filter(type=1).order_by("-id")

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
            if flag == '1':
                self.flowspace_changed(0)
            else:
                self.flowspace_changed(1)
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

    def checkband(self):
        from plugins.openflow.models import Link
        switch_ports = self.get_switch_ports
        if Link.objects.filter(source__in=switch_ports, target__in=switch_ports).count() > 0:
            return 1
        else:
            return 0
#         for switch_port_src in switch_ports:
#             for switch_port_dst in switch_ports:
#                 if Link.objects.filter(source=switch_port_src, target=switch_port_dst).count() > 0:
#                     return 1

    def port_added(self, switch_port):
        if self.sliceport_set.filter(switch_port=switch_port).count() == 0:
            return False
        else:
            return True

    def switch_added(self, switch):
        if self.sliceswitch_set.filter(switch=switch).count() == 0:
            return False
        else:
            return True

    @transaction.commit_manually
    def delete(self, *args, **kwargs):
        from plugins.openflow.controller_api import delete_controller
        from plugins.vt.api import slice_delete_route
        import traceback
        try:
            print "0:get user"
            user = kwargs.get("user")
            print "1:delete slice on virttool"
            if self.ct_change != None:
                try:
                    virttool_del_slice(self.get_virttool(), self.id)
                except:
                    raise
                else:
                    self.ct_change = None
                    self.state = SLICE_STATE_STOPPED
                    self.save()
                    transaction.commit()
            print "2:delete route"
            if self.get_nw():
                if self.vpn_state == 1:
                    slice_delete_route(self)
                    self.vpn_state = 0
                    self.save()
                    transaction.commit()
            print "3:delete controller"
            delete_controller(self.get_controller(), False)
            print "4:delete slice record"
            slice_deleted = SliceDeleted(name=self.name,
                show_name=self.show_name,
                owner_name=self.owner.username,
                description=self.description,
                project_name=self.project.name,
                date_created=self.date_created,
                date_expired=self.date_expired)
            if user == None:
                slice_deleted.type = 2
            else:
                if user.is_superuser:
                    slice_deleted.type = 1
                else:
                    slice_deleted.type = 0
            del kwargs['user']
            super(self.__class__, self).delete(*args, **kwargs)
        except Exception, ex:
            import traceback
            traceback.print_exc()
            print "5:delete slice failed and change slice record"
            transaction.rollback()
#             log(user, None, u"删除虚网(" + self.show_name + u")失败！", result_code=FAIL)
#             transaction.commit()
            try:
                self.failure_reason = ex.message
                if self.type == 0:
                    self.type = 1
                    increase_failed_counter("slice")
#                     decrease_counter_api("slice", self)
#                 else:
#                     decrease_failed_counter("slice", self)
#                     increase_failed_counter("slice")
                self.date_expired = datetime.datetime.now()
                self.save()
            except:
                print "6:change slice record failed! raise exception"
                transaction.rollback()
                raise DbError("虚网删除失败！")
            else:
                transaction.commit()
                print "6:change slice record success"
                return False
        else:
            print "5:delete slice success and create SliceDeleted record "
            try:
                slice_deleted.save()
            except:
                print "6:create SliceDeleted record failed! raise exception"
                transaction.rollback()
#                 log(user, None, u"删除虚网(" + self.show_name + u")失败！", result_code=FAIL)
#                 transaction.commit()
                raise DbError("虚网删除失败！")
            else:
#                 log(user, None, u"删除虚网(" + self.show_name + u")成功！", result_code=SUCCESS)
                transaction.commit()
                print "6:create SliceDeleted record success!"
                return True

    def flowspace_changed(self, flag):
#         0：启动DHCP；1：停止DHCP；2：添加虚拟机、添加外接设备；3：删除虚拟机、删除外接设备；
        a = self.changed
        if a == None:
            return
        if flag == None:
            a = None
        else:
            if flag == 0:
                if a & 0b0100 == 0:
                    a = a | 0b0100 & 0b1110
                else:
                    a = a & 0b1011
            if flag == 1:
                if a & 0b0100 == 0:
                    a = a | 0b0101
                else:
                    a = a & 0b1011
            if flag == 2:
                if a & 0b1000 == 0:
                    a = a | 0b1000
            if flag == 3:
                if a & 0b1000 == 0:
                    a = a | 0b1010
        self.changed = a
        self.save()

    def ct_changed(self):
        if self.ct_change == False:
            self.ct_change = True
            self.save()

    def log_info(self):
        ret = u"虚网名称：" + self.show_name
        return ret

    def get_can_unicom_slices(self):
        can_unicom_slices = []
        owner_slices = self.owner.slice_set.filter(type=SLICE_TYPE_USABLE)
        unicom_slices = self.get_unicom_slices()
        for owner_slice in owner_slices:
            if owner_slice not in unicom_slices and (owner_slice != self):
                gw = owner_slice.get_gw()
                if gw and gw.usable():
                    can_unicom_slices.append(owner_slice)
        return can_unicom_slices

    def get_unicom_slices(self):
        unicom_slices = []
        src_unicoms = UnicomSlice.objects.filter(dst_slice=self)
        for src_unicom in src_unicoms:
            if src_unicom.src_slice not in unicom_slices:
                gw = src_unicom.src_slice.get_gw()
                if gw and gw.usable():
                    unicom_slices.append(src_unicom.src_slice)
        dst_unicoms = UnicomSlice.objects.filter(src_slice=self)
        for dst_unicom in dst_unicoms:
            if dst_unicom.dst_slice not in unicom_slices:
                gw = dst_unicom.dst_slice.get_gw()
                if gw and gw.usable():
                    unicom_slices.append(dst_unicom.dst_slice)
        return unicom_slices

    def can_edit_unicom(self):
        gw = self.get_gw()
        if gw and gw.usable():
            return True
        else:
            return False

    @transaction.commit_on_success
    def add_unicom_slice(self, other_slice):
        print "add_unicom_slice"
        try:
            unicom_count = UnicomSlice.objects.filter(src_slice=self, dst_slice=other_slice).count()
            if unicom_count > 0:
                return True
            unicom_count = UnicomSlice.objects.filter(src_slice=other_slice, dst_slice=self).count()
            if unicom_count > 0:
                return True
            gw_src = self.get_gw()
            gw_dst = other_slice.get_gw()
            if gw_src and gw_dst and gw_src.usable() and gw_dst.usable():
                UnicomSlice(src_slice=self, dst_slice=other_slice).save()
                add_unicom_slice_api(self, other_slice)
                return True
            else:
                print "f1"
                return False
        except:
            transaction.rollback()
            print "f2"
#             import traceback
#             traceback.print_exc()
            return False

    @transaction.commit_on_success
    def del_unicom_slice(self, other_slice):
        print "del_unicom_slice"
        try:
            dst_unicoms = UnicomSlice.objects.filter(src_slice=self, dst_slice=other_slice)
            src_unicoms = UnicomSlice.objects.filter(src_slice=other_slice, dst_slice=self)
            if dst_unicoms.count() + src_unicoms.count() > 0:
                dst_unicoms.delete()
                src_unicoms.delete()
                gw_src = self.get_gw()
                gw_dst = other_slice.get_gw()
                if gw_src and gw_dst and gw_src.usable() and gw_dst.usable():
                    del_unicom_slice_api(self, other_slice)
            return True
        except:
            transaction.rollback()
            return False

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


# @receiver(pre_delete, sender=Slice)
# def pre_delete_slice(sender, instance, **kwargs):
#     print "pre delete slice"
#
#
@receiver(post_delete, sender=Slice)
def post_delete_slice(sender, instance, **kwargs):
    print "post delete slice"
    print "delete subnet"
    try:
        IPUsage.objects.delete_subnet(instance.uuid)
    except Subnet.DoesNotExist:
        pass
    except Exception:
        raise
    print "delete route on unicom slices"
    try:
        unicom_slices = instance.get_unicom_slices()
        for unicom_slice in unicom_slices:
            if not instance.del_unicom_slice(unicom_slice):
                raise DbError("虚网通信关系删除失败！")
    except Exception:
        raise


class UnicomSlice(models.Model):
    src_slice = models.ForeignKey(Slice, related_name="source_slice")
    dst_slice = models.ForeignKey(Slice, related_name="target_slice")

    class Meta:
        unique_together = (("src_slice", "dst_slice"), )


def add_unicom_slice_api(slice_obj, unicom_slice):
    pass


def del_unicom_slice_api(slice_obj, unicom_slice):
    pass

