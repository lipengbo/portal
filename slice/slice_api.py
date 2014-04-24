# coding:utf-8
from slice.models import *
from slice.slice_exception import DbError, IslandError, NameExistError
from plugins.openflow.flowvisor_api import flowvisor_del_slice,\
    flowvisor_del_flowspace, flowvisor_add_flowspace,\
    flowvisor_update_slice_status, flowvisor_add_slice,\
    flowvisor_del_port, flowvisor_add_port
from plugins.openflow.flowspace_api import matches_to_arg_match,\
    flowspace_nw_add, flowspace_gw_add, flowspace_dhcp_add,\
    flowspace_dhcp_del, flowspace_gw_del
from plugins.openflow.controller_api import slice_change_controller,\
    delete_controller, create_add_controller
from plugins.vt.api import create_vm_for_gateway
from resources.ovs_api import slice_add_ovs_or_ports
from plugins.ipam.models import IPUsage
from plugins.common.ovs_client import get_switch_stat, get_sFlow_metric
from resources.models import Switch
from django.db import transaction
import datetime
import traceback
import calendar
from etc.config import gw_controller

from plugins.vt.api import get_slice_gw_mac, schedul_for_controller_and_gw

import logging
LOG = logging.getLogger("ccf")

from etc import config
# import time
# from etc.config import slice_expiration_days


def create_slice_step(project, slice_uuid, name, description, island, user, ovs_or_ports,
                      controller_info, slice_nw, gw_host_id, gw_ip, dhcp_selected, tp_mod):
    print "create_slice_step"
    slice_obj = None
    try:
        print "1:create slice record, add island, add flowvisor"
        slice_obj = create_slice_api(project, slice_uuid, name, description, island, user)
        print "2:add ovses or ports"
        slice_add_ovs_or_ports(slice_obj, ovs_or_ports, tp_mod)
        print "3:scheduler for resources"
        schedul_for_controller_and_gw(controller_info, gw_host_id, island)
        print "4:create and add controller"
        create_add_controller(slice_obj, controller_info)
        print "5:create slice on flowvisor"
        flowvisor_add_slice(island.flowvisor_set.all()[0], slice_obj.id,
                            slice_obj.get_controller(), user.email)
        print "6:create subnet"
        IPUsage.objects.subnet_create_success(slice_obj.uuid)
        print "7:add nw flowspace in database"
        flowspace_nw_add(slice_obj, [], slice_nw)
        print "8:create gateway"
        enabled_dhcp = (int(dhcp_selected) == 1)
        if gw_host_id and int(gw_host_id) > 0:
            gw = create_vm_for_gateway(island, slice_obj, int(gw_host_id),
                                       image_name='gateway',
                                       enable_dhcp=enabled_dhcp)
        print "9:create slice success and return"
        return slice_obj
    except Exception, ex:
        LOG.debug(traceback.print_exc())
        print "10:create slice failed and delete slice"
        if slice_obj:
            try:
                slice_obj.delete()
            except Exception:
                if slice_obj:
                    slice_obj.type = 1
                    slice_obj.save()
        print "11:delete slice success and raise exception"
        raise DbError(ex.message)


def create_slice_api(project, slice_uuid, name, description, island, user):
    """slice创建
    """
    print 'create_slice_api'
    try:
        Slice.objects.get(name=name)
    except Slice.DoesNotExist:
        try:
            slice_expiration_days = int(config.slice_expiration_days)
        except:
            slice_expiration_days = 30
        else:
            if slice_expiration_days <= 0:
                slice_expiration_days = 30
        if project and island and user:
            flowvisors = island.flowvisor_set.all()
            if flowvisors:
                try:
                    slice_obj = None
                    date_now = datetime.datetime.now()
    #                 date_delta = datetime.timedelta(seconds=slice_expiration_days)
                    date_delta = datetime.timedelta(days=slice_expiration_days)
                    expiration_date = date_now + date_delta
                    slice_names = name.split('_')
                    if len(slice_names) > 1:
                        del slice_names[-1]
                    show_name = ('_').join(slice_names)
                    slice_obj = Slice(owner=user,
                                      name=name,
                                      show_name=show_name,
                                      description=description,
                                      project=project,
                                      date_expired=expiration_date,
                                      uuid=slice_uuid)
                    slice_obj.save()
                    slice_obj.add_island(island)
                    slice_obj.add_resource(flowvisors[0])
                    return slice_obj
                except Exception, ex:
                    if slice_obj:
                        try:
                            slice_obj.delete()
                        except:
                            pass
                    raise DbError("虚网创建失败!")
            else:
                raise IslandError("所选节点无可用flowvisor！")
        else:
            raise DbError("数据库异常!")
    else:
        raise NameExistError("slice名称已存在!")


@transaction.commit_on_success
def edit_slice_api(slice_obj, new_description, new_controller):
    """编辑slice，编辑描述信息、控制器、交换机端口
    """
    LOG.debug('edit_slice_api')
    try:
        slice_change_description(slice_obj, new_description)
        slice_change_controller(slice_obj, new_controller)
    except:
        raise


@transaction.commit_on_success
def slice_change_description(slice_obj, new_description):
    """编辑slice，编辑描述信息、控制器、交换机端口
    """
    LOG.debug('slice_change_description')
    try:
        if slice_obj and slice_obj.description != new_description:
            slice_obj.change_description(new_description)
    except Exception, ex:
        transaction.rollback()
        raise DbError("编辑失败！")


@transaction.commit_on_success
def delete_slice_api(slice_obj):
    """删除slice
    """
    print 'delete_slice_api'
    if slice_obj:
        try:
            print "p1:delete subnet"
            try:
                IPUsage.objects.delete_subnet(slice_obj.uuid)
            except:
                pass
            print "p2:delete controller"
            delete_controller(slice_obj.get_controller(), False)
            print "p3:pre delete slice success"
        except Exception, ex:
            print "p4:pre delete slice failed and raise exception"
            transaction.rollback()
            raise DbError(ex.message)


@transaction.commit_on_success
def start_slice_api1(slice_obj):
    """启动slice
    """
    print 'start_slice_api'
    from slice.tasks import start_slice_sync
    try:
        if slice_obj and slice_obj.state == SLICE_STATE_STOPPED:
            all_vms = slice_obj.get_vms()
            for vm in all_vms:
                if vm.state == 8:
                    raise DbError("资源分配中，请稍后启动！")
            controller = slice_obj.get_controller()
            if controller.host and controller.host.state != 1:
                raise DbError("请确保控制器已启动！")
            gw = slice_obj.get_gw()
            if gw and gw.enable_dhcp and gw.state != 1:
                raise DbError("请确保gateway已启动！")
            flowvisor = slice_obj.get_flowvisor()
            if flowvisor == None:
                raise DbError("虚网启动异常！")
            try:
                slice_obj.starting()
                start_slice_sync.delay(slice_obj.id)
            except Exception, ex:
                raise DbError("虚网启动失败！")
    except Exception, ex:
        transaction.rollback()
        raise


@transaction.commit_on_success
def start_slice_api(slice_obj):
    """启动slice
    """
    print 'start_slice_api'
    from slice.tasks import start_slice_sync
    try:
        controller_flag = False
        gw_flag = False
        if slice_obj and slice_obj.state == SLICE_STATE_STOPPED:
            all_vms = slice_obj.get_vms()
            for vm in all_vms:
                if vm.state == 8:
                    raise DbError("资源分配中，请稍后启动！")
            controller = slice_obj.get_controller()
            if controller.host and controller.host.state != 1:
                if controller.host.state == 0 or controller.host.state == 5:
                    controller_flag = True
                else:
                    if controller.state == 12:
                        pass
                    if controller.host.state == 13:
                        raise DbError("操作失败，请稍后再试！")
                    else:
                        raise DbError("请确保控制器可用！")
            gw = slice_obj.get_gw()
            if gw and gw.enable_dhcp and gw.state != 1:
                if gw.state == 0 or gw.state == 5:
                    gw_flag = True
                else:
                    if gw.state == 12:
                        pass
                    if gw.state == 13:
                        raise DbError("操作失败，请稍后再试！")
                    else:
                        raise DbError("请确保gateway可用！")
            flowvisor = slice_obj.get_flowvisor()
            if flowvisor == None:
                raise DbError("虚网启动失败！")
            if slice_obj.state == 0:
                slice_flag = True
            if slice_obj.state == 4:
                raise DbError("操作失败，请稍后再试！")
            try:
                if slice_flag:
                    slice_obj.starting()
                    if controller_flag:
                        controller.host.state = 12
                        controller.host.save()
                    if gw_flag:
                        gw.state = 12
                        gw.save()
                    start_slice_sync.delay(slice_obj.id, controller_flag, gw_flag)
            except Exception, ex:
                import traceback
                traceback.print_exc()
                raise DbError("虚网启动失败！")
    except Exception, ex:
        transaction.rollback()
        raise


@transaction.commit_on_success
def stop_slice_api(slice_obj):
    """停止slice
    """
    LOG.debug('stop_slice_api')
    from slice.tasks import stop_slice_sync
    try:
        Slice.objects.get(id=slice_obj.id)
    except Exception, ex:
        raise DbError(ex.message)
    else:
        if slice_obj.state == SLICE_STATE_STARTED:
            try:
                slice_obj.stopping()
                stop_slice_sync.delay(slice_obj.id)
            except Exception:
                transaction.rollback()
                raise


def add_flowspace(in_port, dl_vlan, dl_vpcp, dl_src, dl_dst, dl_type,
    nw_src, nw_dst, nw_proto, nw_tos, tp_src, tp_dst, flowvisor, name,
    slice_name, slice_action, pwd, dpid, priority):
    try:
        arg_match = matches_to_arg_match(in_port, dl_vlan, dl_vpcp, dl_src,
                                         dl_dst, dl_type, nw_src, nw_dst,
                                         nw_proto, nw_tos, tp_src, tp_dst, flowvisor.type)
        flowvisor_add_flowspace(flowvisor, name, slice_name, slice_action,
                                pwd, dpid, priority, arg_match)
    except:
        raise


def update_slice_virtual_network_cnvp(slice_obj):
    try:
        Slice.objects.get(id=slice_obj.id)
    except Exception, ex:
        raise DbError(ex.message)
    if slice_obj.changed != None and slice_obj.changed & 0b1100 == 0:
        return
    flowvisor = slice_obj.get_flowvisor()
    switch_ports = slice_obj.get_switch_ports()
    dpids = []
    dhcp_macs = []
    for switch_port in switch_ports:
        if switch_port.switch.type() == 3:
            if switch_port.switch.dpid not in dpids:
                dpids.append(switch_port.switch.dpid)
            vms = switch_port.virtualmachine_set.all()
            for vm in vms:
                if (vm.type == 1 and vm.enable_dhcp and vm.mac):
                    dhcp_macs.append({'dpid': switch_port.switch.dpid, 'mac': vm.mac})
#delete flowspace port, add port flowspace
    try:
        if slice_obj.changed == None or (slice_obj.changed != None and slice_obj.changed & 0b1101 != 4):
            flowvisor_del_flowspace(flowvisor, slice_obj.id, None)
            flowvisor_del_port(flowvisor, slice_obj.id, None, None)
            for switch_port in switch_ports:
                flowvisor_add_port(flowvisor, slice_obj.id, switch_port.switch.dpid, switch_port.port)
            slice_nw = slice_obj.get_nw()
            for dpid in dpids:
                arg_match = matches_to_arg_match("", "", "", "", "", "0x800",
                                 slice_nw, slice_nw, "", "", "", "", flowvisor.type)
                flowvisor_add_flowspace(flowvisor, None,
                                        slice_obj.id,
                                        4, 'cdn%nf',
                                        dpid,
                                        100, arg_match)
                arg_match = matches_to_arg_match("", "", "", "", "", "0x806",
                                 slice_nw, slice_nw, "", "", "", "", flowvisor.type)
                flowvisor_add_flowspace(flowvisor, None,
                                        slice_obj.id,
                                        4, 'cdn%nf',
                                        dpid,
                                        100, arg_match)
                arg_match = matches_to_arg_match("", "", "", "", "", "0x800",
                                 slice_nw, "other", "", "", "", "", flowvisor.type)
                flowvisor_add_flowspace(flowvisor, None,
                                        slice_obj.id,
                                        4, 'cdn%nf',
                                        dpid,
                                        100, arg_match)
                arg_match = matches_to_arg_match("", "", "", "", "", "0x800",
                                 "other", slice_nw, "", "", "", "", flowvisor.type)
                flowvisor_add_flowspace(flowvisor, None,
                                        slice_obj.id,
                                        4, 'cdn%nf',
                                        dpid,
                                        100, arg_match)
        dhcp_tag = slice_obj.get_dhcp()
        if dhcp_tag:
            for dhcp_mac in dhcp_macs:
                arg_match = matches_to_arg_match("", "", "", dhcp_mac['mac'], "", "0x800",
                                 "0.0.0.0", "255.255.255.255", "", "", "", "", flowvisor.type)
                flowvisor_add_flowspace(flowvisor, None,
                                        slice_obj.id,
                                        4, 'cdn%nf',
                                        dhcp_mac['dpid'],
                                        100, arg_match)
    except:
        raise


def update_slice_virtual_network_cnvp_pt(slice_obj):
    try:
        Slice.objects.get(id=slice_obj.id)
    except Exception, ex:
        raise DbError(ex.message)
    if slice_obj.changed != None and slice_obj.changed & 0b1100 == 0:
        return
    flowvisor = slice_obj.get_flowvisor()
    switch_ports = slice_obj.get_switch_ports()
    dpids = []
    dhcp_macs = []
    for switch_port in switch_ports:
        if switch_port.switch.type() == 3:
            if switch_port.switch.dpid not in dpids:
                dpids.append(switch_port.switch.dpid)
            vms = switch_port.virtualmachine_set.all()
            for vm in vms:
                if (vm.type == 1 and vm.enable_dhcp and vm.mac):
                    dhcp_macs.append({'dpid': switch_port.switch.dpid, 'mac': vm.mac})
#delete flowspace port, add port flowspace
    try:
        if slice_obj.changed == None or (slice_obj.changed != None and slice_obj.changed & 0b1101 != 4):
            flowvisor_del_flowspace(flowvisor, slice_obj.id, None)
            flowvisor_del_port(flowvisor, slice_obj.id, None, None)
            for switch_port in switch_ports:
                flowvisor_add_port(flowvisor, slice_obj.id, switch_port.switch.dpid, switch_port.port)
            slice_nw = slice_obj.get_nw()
            for dpid in dpids:
                arg_match = matches_to_arg_match("", "", "", "", "", "0x800",
                                 slice_nw, slice_nw, "", "", "", "", flowvisor.type)
                flowvisor_add_flowspace(flowvisor, None,
                                        slice_obj.id,
                                        4, 'cdn%nf',
                                        dpid,
                                        100, arg_match)
                arg_match = matches_to_arg_match("", "", "", "", "", "0x806",
                                 slice_nw, slice_nw, "", "", "", "", flowvisor.type)
                flowvisor_add_flowspace(flowvisor, None,
                                        slice_obj.id,
                                        4, 'cdn%nf',
                                        dpid,
                                        100, arg_match)
                arg_match = matches_to_arg_match("", "", "", "", "", "0x800",
                                 slice_nw, "other", "", "", "", "", flowvisor.type)
                flowvisor_add_flowspace(flowvisor, None,
                                        slice_obj.id,
                                        4, 'cdn%nf',
                                        dpid,
                                        100, arg_match)
                arg_match = matches_to_arg_match("", "", "", "", "", "0x800",
                                 "other", slice_nw, "", "", "", "", flowvisor.type)
                flowvisor_add_flowspace(flowvisor, None,
                                        slice_obj.id,
                                        4, 'cdn%nf',
                                        dpid,
                                        100, arg_match)
        dhcp_tag = slice_obj.get_dhcp()
        if dhcp_tag:
            for dhcp_mac in dhcp_macs:
                arg_match = matches_to_arg_match("", "", "", dhcp_mac['mac'], "", "0x800",
                                 "0.0.0.0", "255.255.255.255", "", "", "", "", flowvisor.type)
                flowvisor_add_flowspace(flowvisor, None,
                                        slice_obj.id,
                                        4, 'cdn%nf',
                                        dhcp_mac['dpid'],
                                        100, arg_match)
    except:
        raise


def update_slice_virtual_network_flowvisor(slice_obj):
    try:
        Slice.objects.get(id=slice_obj.id)
    except Exception, ex:
        raise DbError(ex.message)
    if slice_obj.changed != None and slice_obj.changed & 0b1100 == 0:
        return
    flowvisor = slice_obj.get_flowvisor()
    flowspace_name = str(slice_obj.id) + '_df'
    switch_ports = slice_obj.get_switch_ports()
    default_flowspaces = slice_obj.get_default_flowspaces()
    dpids = []
    slice_gw = get_slice_gw_mac(slice_obj)
    try:
        if slice_obj.changed == None or (slice_obj.changed != None and slice_obj.changed & 0b1101 != 4):
            flowspace_dhcp_del(slice_obj, True)
            del_gateways = slice_obj.get_gws()
            for del_gateway in del_gateways:
                flowspace_gw_del(slice_obj, del_gateway)
        gw = slice_obj.get_gw()
        if gw and gw.state != 8 and gw.state != 9:
            if slice_obj.changed == None or (slice_obj.changed != None and slice_obj.changed & 0b1101 != 4):
                flowspace_gw_add(slice_obj, gw.mac)
            if gw.enable_dhcp:
                flowspace_dhcp_add(slice_obj, True)
        if slice_obj.changed != None and (slice_obj.changed & 0b1101 == 4):
            for switch_port in switch_ports:
                for default_flowspace in default_flowspaces:
                    if default_flowspace.priority == 1:
                        in_port = str(switch_port.port)
                        arg_match = matches_to_arg_match(
                            in_port, default_flowspace.dl_vlan,
                            default_flowspace.dl_vpcp, default_flowspace.dl_src,
                            default_flowspace.dl_dst, default_flowspace.dl_type,
                            default_flowspace.nw_src, default_flowspace.nw_dst,
                            default_flowspace.nw_proto, default_flowspace.nw_tos,
                            default_flowspace.tp_src, default_flowspace.tp_dst, flowvisor.type)
                        flowvisor_add_flowspace(flowvisor, flowspace_name,
                                                slice_obj.id,
                                                default_flowspace.actions, 'cdn%nf',
                                                switch_port.switch.dpid,
                                                default_flowspace.priority, arg_match)
            return
        flowvisor_del_port(flowvisor, slice_obj.id, None, None)
        flowvisor_del_flowspace(flowvisor, slice_obj.id, flowspace_name)
        for switch_port in switch_ports:
            for default_flowspace in default_flowspaces:
                if not (default_flowspace.dl_src == slice_gw or default_flowspace.dl_dst == slice_gw):
                    in_port = str(switch_port.port)
                    arg_match = matches_to_arg_match(
                        in_port, default_flowspace.dl_vlan,
                        default_flowspace.dl_vpcp, default_flowspace.dl_src,
                        default_flowspace.dl_dst, default_flowspace.dl_type,
                        default_flowspace.nw_src, default_flowspace.nw_dst,
                        default_flowspace.nw_proto, default_flowspace.nw_tos,
                        default_flowspace.tp_src, default_flowspace.tp_dst, flowvisor.type)
                    flowvisor_add_flowspace(flowvisor, flowspace_name,
                                            slice_obj.id,
                                            default_flowspace.actions, 'cdn%nf',
                                            switch_port.switch.dpid,
                                            default_flowspace.priority, arg_match)
                else:
                    if gw_controller and (switch_port.switch.dpid not in dpids):
                        arg_match = matches_to_arg_match(
                            None, default_flowspace.dl_vlan,
                            default_flowspace.dl_vpcp, default_flowspace.dl_src,
                            default_flowspace.dl_dst, default_flowspace.dl_type,
                            default_flowspace.nw_src, default_flowspace.nw_dst,
                            default_flowspace.nw_proto, default_flowspace.nw_tos,
                            default_flowspace.tp_src, default_flowspace.tp_dst, flowvisor.type)
                        flowvisor_add_flowspace(flowvisor, flowspace_name,
                                                slice_obj.id,
                                                default_flowspace.actions, 'cdn%nf',
                                                switch_port.switch.dpid,
                                                default_flowspace.priority, arg_match)
            if switch_port.switch.dpid not in dpids:
                dpids.append(switch_port.switch.dpid)
    except:
        raise


def update_slice_virtual_network(slice_obj):
    """更新slice的虚网，添加或删除交换机端口、网段、gateway、dhcp、vm后调用
    """
    print 'update_slice_virtual_network'
    flowvisor = slice_obj.get_flowvisor()
    if flowvisor:
        if flowvisor.type == 1:
            update_slice_virtual_network_cnvp(slice_obj)
        else:
            update_slice_virtual_network_flowvisor(slice_obj)
    else:
        raise DbError("数据库异常!")


def get_slice_topology(slice_obj):
    """获取slice拓扑信息
    """
    print 'get_slice_topology'
#     交换机
    try:
        switches = []
        dpids = []
        switch_objs = slice_obj.get_switches()
        for switch_obj in switch_objs:
            ports = []
            one_switch_ports = slice_obj.get_one_switch_ports(switch_obj)
            for one_switch_port in one_switch_ports:
                ports.append({'name': one_switch_port.name,
                              'port': one_switch_port.port})
            switch = {'dpid': switch_obj.dpid,
                      'name': switch_obj.name,
                      'type': switch_obj.type(),
                      'id': switch_obj.id,
                      'ports': ports}
            switches.append(switch)
            dpids.append(switch_obj.dpid)
#         print switches
        switch_ports = slice_obj.get_switch_ports()
#         for switch_port in switch_ports:
#             switch_dpids.append(switch_port.switch.dpid)
#         switch_dpids = list(set(switch_dpids))
#         for switch_dpid in switch_dpids:
#             switch = {'dpid': switch_dpid, 'name':}
#             switches.append(switch)
#     链接
        links = []
        switch_ids = []
        ports = {}
        flowvisor = slice_obj.get_flowvisor()
        if flowvisor:
            link_objs = flowvisor.link_set.filter(
                source__in=switch_ports, target__in=switch_ports)
        for link_obj in link_objs:
            if (link_obj.source.switch.dpid in dpids) and (link_obj.target.switch.dpid in dpids):
                link = {'src_switch': link_obj.source.switch.dpid,
                        'src_port_name': link_obj.source.name,
                        'src_port': link_obj.source.port,
                        'dst_switch': link_obj.target.switch.dpid,
                        'dst_port': link_obj.target.port,
                        'dst_port_name': link_obj.target.name}
                links.append(link)
                if link_obj.source.switch.id in switch_ids:
                    if link_obj.source.port not in ports[link_obj.source.switch.id]:
                        ports[link_obj.source.switch.id].append(link_obj.source.port)
                else:
                    switch_ids.append(link_obj.source.switch.id)
                    ports[link_obj.source.switch.id] = [link_obj.source.port]
                if link_obj.target.switch.id in switch_ids:
                    if link_obj.target.port not in ports[link_obj.target.switch.id]:
                        ports[link_obj.target.switch.id].append(link_obj.target.port)
                else:
                    switch_ids.append(link_obj.target.switch.id)
                    ports[link_obj.target.switch.id] = [link_obj.target.port]
    #     带宽
        maclist = []
    #     虚拟机
        specials = []
        normals = []
        servers = []
        virtual_switches = slice_obj.get_virtual_switches()
        for virtual_switch in virtual_switches:
            servers.append(virtual_switch.server)
        vms = slice_obj.get_vms()
        for vm in vms:
            if vm.mac:
                mac = ''.join(vm.mac.split(':')).upper()
                maclist.append(mac)
            virtual_switch = vm.server.get_link_vs()
            if virtual_switch:
                if vm.type == 1:
                    vm_info = {'macAddress': vm.mac,
                               'switchDPID': virtual_switch.dpid,
                               'hostid': vm.id,
                               'hostStatus': vm.state,
                               'name': vm.name,
                               'ip': vm.ip.ipaddr}
                    normals.append(vm_info)
#     带宽
        bandwidth = []
        for switch_id in switch_ids:
            try:
                switch = Switch.objects.get(id=switch_id)
            except:
                pass
            else:
                for port in ports[switch_id]:
                    bandwidth.append({'id': (str(switch_id) + '_' + str(port)),
                                'cur_bd': 0, 'total_bd': 0})

        topology = {'switches': switches, 'links': links,
                    'normals': normals, 'specials': specials,
                    'bandwidth': bandwidth, 'maclist': maclist}
    except Exception, ex:
        print "get topology failed"
        return []
    else:
        print "get topology success"
        return topology


def get_links_bandwidths(switchs_ports):
    print 'get_links_bandwidths'
    ret = []
    for switch_ports in switchs_ports:
        try:
            switch = Switch.objects.get(id=switch_ports['id'])
        except:
            pass
        else:
            switch_stat = get_switch_stat(switch.ip)
            recv_data = 0
            send_data = 0
            for br in switch_stat:
                for port in br['ports']:
                    if port['name'] in switch_ports['port_names']:
                        recv_data = int(port['stats']['recv']['byte'])
                        send_data = int(port['stats']['send']['byte'])
                        ret.append({'id': (str(switch.id) + '_' + port['name']),
                                    'bd': (recv_data + send_data)})
                        switch_ports['port_names'].remove(port['name'])
            for port_name in switch_ports['port_names']:
                ret.append({'id': (str(switch.id) + '_' + port_name), 'bd': 0})
    return ret


def get_links_max_bandwidths(switchs_ports):
    print 'get_links_max_bandwidths'
    ret = []
    for switch_ports in switchs_ports:
        try:
            switch = Switch.objects.get(id=switch_ports['id'])
        except:
            pass
        else:
            for port in switch_ports['port_names']:
                print 5
                ret.append({'id': (str(switch.id) + '_' + port),
                            'bd': '1111000000'})
                print 6
    return ret


def get_slice_links_bandwidths(switchs_ports, maclist):
    print 'get_slice_links_bandwidths'
#     time.sleep(15)
    ret = []
    for switch_ports in switchs_ports:
        try:
            switch = Switch.objects.get(id=switch_ports['id'])
        except:
            pass
        else:
            for port in switch_ports['ports']:
                try:
                    dpid = ''.join(switch.dpid.split(':'))
#                     print '====================='
#                     print switch.ip
#                     print dpid
#                     print maclist
#                     print '====================='
                    band = get_sFlow_metric(switch.ip, dpid, int(port), maclist)
#                     band = [0, 0]
                except Exception, ex:
                    #print ex
                    ret.append({'id': (str(switch.id) + '_' + str(port)),
                                'cur_bd': 0, 'total_bd': 0})
                else:
#                     band = [None, None]
                    print band
                    if band:
                        if band[0] is not None and band[1] is not None:
                            ret.append({'id': (str(switch.id) + '_' + str(port)),
                                        'cur_bd': band[1] * 8.0,
                                        'total_bd': band[0]})
                        else:
                            ret.append({'id': (str(switch.id) + '_' + str(port)),
                                        'cur_bd': 0, 'total_bd': 0})
                    else:
                        ret.append({'id': (str(switch.id) + '_' + str(port)),
                                    'cur_bd': 0, 'total_bd': 0})
    return ret


def get_slice_resource(slice_obj):
    """获取slice资源，包括节点、flowvisor、控制器、交换机端口
    """
    LOG.debug('get_slice_resource')


def get_count_show_data(target, type, total_num, stype):
    from common.models import Counter, FailedCounter, DeletedCounter
    print "get_slice_count_show"
    date_now = datetime.datetime.now()
    show_dates = []
    show_nums = []
    if target == 'project':
        target_id = 0
    else:
        target_id = 1
    if type == "year":
        year = 2013
        if int(date_now.strftime('%Y')) - 10 >= year:
            year = int(date_now.strftime('%Y')) - 10 + 1
        for i in range(0, 10):
            if int(stype) == 0:
                sc = Counter.objects.filter(target=target_id,
                                            date__year=str(year),
                                            type=0)
            if int(stype) == 1:
                sc = FailedCounter.objects.filter(target=target_id,
                                            date__year=str(year),
                                            type=0)
            if int(stype) == 2:
                sc = DeletedCounter.objects.filter(target=target_id,
                                            date__year=str(year),
                                            type=0)
            show_dates.append(str(year) + "年")
            year = year + 1
            if sc:
                num = sc[0].count
            else:
                num = 0
            show_nums.append(num)
    else:
        if type == "month":
            year = int(date_now.strftime('%Y'))
            for i in range(0, 12):
                if int(stype) == 0:
                    sc = Counter.objects.filter(target=target_id,
                                                date__year=str(year),
                                                date__month=str(i + 1),
                                                type=1)
                if int(stype) == 1:
                    sc = FailedCounter.objects.filter(target=target_id,
                                                date__year=str(year),
                                                date__month=str(i + 1),
                                                type=1)
                if int(stype) == 2:
                    sc = DeletedCounter.objects.filter(target=target_id,
                                                date__year=str(year),
                                                date__month=str(i + 1),
                                                type=1)
                show_dates.append(str(i + 1) + "月")
#                 if month == 1:
#                     month = 12
#                     year = year - 1
#                 else:
#                     month = month - 1
                if sc:
                    num = sc[0].count
                else:
                    num = 0
                show_nums.append(num)
        else:
            month_days = calendar.monthrange(int(date_now.strftime('%Y')), int(date_now.strftime('%m')))[1]
            for i in range(0, month_days):
                if int(stype) == 0:
                    sc = Counter.objects.filter(target=target_id,
                                                date__year=date_now.strftime('%Y'),
                                                date__month=date_now.strftime('%m'),
                                                date__day=str(i + 1),
                                                type=2)
                if int(stype) == 1:
                    sc = FailedCounter.objects.filter(target=target_id,
                                                date__year=date_now.strftime('%Y'),
                                                date__month=date_now.strftime('%m'),
                                                date__day=str(i + 1),
                                                type=2)
                if int(stype) == 2:
                    sc = DeletedCounter.objects.filter(target=target_id,
                                                date__year=date_now.strftime('%Y'),
                                                date__month=date_now.strftime('%m'),
                                                date__day=str(i + 1),
                                                type=2)
                show_dates.append(str(i + 1))
                if sc:
                    num = sc[0].count
                else:
                    num = 0
                show_nums.append(num)
#     show_dates.reverse()
#     show_nums.reverse()
    ret = {"show_dates": show_dates, "show_nums": show_nums}
    return ret


def topology_mapping(slice_obj):
    """拓扑映射
    """
    LOG.debug('topology_mapping')
    
