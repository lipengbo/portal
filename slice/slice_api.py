# coding:utf-8
from slice.models import *
from slice.slice_exception import DbError, IslandError, NameExistError
from plugins.openflow.flowvisor_api import flowvisor_del_slice,\
    flowvisor_del_flowspace, flowvisor_add_flowspace,\
    flowvisor_update_slice_status, flowvisor_add_slice
from plugins.openflow.flowspace_api import matches_to_arg_match,\
    flowspace_nw_add, flowspace_gw_add, flowspace_dhcp_add,\
    flowspace_dhcp_del, flowspace_gw_del
from plugins.openflow.controller_api import slice_change_controller,\
    delete_controller, create_add_controller
from plugins.vt.api import create_vm_for_gateway
from resources.ovs_api import slice_add_ovs_ports
from plugins.ipam.models import IPUsage
from plugins.common.ovs_client import get_switch_stat, get_sFlow_metric
from resources.models import Switch
from django.db import transaction
import datetime
import traceback

import logging
LOG = logging.getLogger("ccf")


def create_slice_step(project, name, description, island, user, ovs_ports,
                      controller_info, slice_nw, gw_host_id, gw_ip, dhcp_selected):
    slice_obj = None
    try:
        print 1
        slice_obj = create_slice_api(project, name, description, island, user)
        print 2
        print ovs_ports
        slice_add_ovs_ports(slice_obj, ovs_ports)
        print slice_obj.get_switches()
        print 3
        create_add_controller(slice_obj, controller_info)
        print 4
        flowvisor_add_slice(island.flowvisor_set.all()[0], name,
                            slice_obj.get_controller(), user.email)
        print 5
#         创建并添加网段
        IPUsage.objects.subnet_create_success(slice_obj.name)
        print 6
        flowspace_nw_add(slice_obj, [], slice_nw)
#         创建并添加网关
#         创建并添加dhcp
        enabled_dhcp = (int(dhcp_selected) == 1)
        print 7
        if gw_host_id and int(gw_host_id) > 0:
            print 8
            try:
                gw = create_vm_for_gateway(island, slice_obj, int(gw_host_id),
                                           image_name='gateway',
                                           enable_dhcp=enabled_dhcp)
            except Exception, ex:
                LOG.debug(traceback.print_exc())
                raise DbError(ex)
            print 9
#             flowspace_gw_add(slice_obj, gw.mac)
        print 10
#         创建并添加虚拟机
        return slice_obj
    except:
        print 11
        if slice_obj:
            print 12
            slice_obj.delete()
        print 13
        raise


@transaction.commit_on_success
def create_slice_api(project, name, description, island, user):
    """slice添加交换端口
    """
    print 'create_slice_api'
    try:
        Slice.objects.get(name=name)
    except Slice.DoesNotExist:
        if project and island and user:
            flowvisors = island.flowvisor_set.all()
            if flowvisors:
                date_now = datetime.datetime.now()
#                 date_delta = datetime.timedelta(seconds=5)
                date_delta = datetime.timedelta(days=30)
                expiration_date = date_now + date_delta
                slice_names = name.split('_')
                if len(slice_names) > 1:
                    del slice_names[-1]
                show_name = ('_').join(slice_names)
                try:
                    slice_obj = Slice(owner=user,
                                      name=name,
                                      show_name=show_name,
                                      description=description,
                                      project=project,
                                      date_expired=expiration_date)
                    slice_obj.save()
                    slice_obj.add_island(island)
                    slice_obj.add_resource(flowvisors[0])
                    return slice_obj
                except Exception, ex:
                    transaction.rollback()
                    raise DbError(ex)
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
    if slice_obj:
        if slice_obj.description != new_description:
            try:
                slice_obj.change_description(new_description)
            except Exception, ex:
                transaction.rollback()
                raise DbError(ex)


@transaction.commit_on_success
def delete_slice_api(slice_obj):
    """删除slice
    """
    print 'delete_slice_api'
    if slice_obj:
        try:
#             删除虚拟机
#             删除dhcp
#             删除网关
#             删除slice网络地址
#             print 1
#             del_nw = slice_obj.get_nw()
#             print 2
#             flowspace_nw_del(slice_obj, del_nw)
            print 3
            try:
                IPUsage.objects.delete_subnet(slice_obj.name)
            except:
                pass
            print 4
#             删除底层slice
            flowvisor_del_slice(slice_obj.get_flowvisor(), slice_obj.name)
            print 5
#             删除控制器
            delete_controller(slice_obj.get_controller())
            print 6
#             删除交换机端口
#             删除slice记录
        except Exception, ex:
            transaction.rollback()
            raise DbError(ex)


@transaction.commit_on_success
def start_slice_api(slice_obj):
    """启动slice
    """
    LOG.debug('start_slice_api')
    try:
        Slice.objects.get(id=slice_obj.id)
    except Exception, ex:
        raise DbError(ex)
    else:
        if slice_obj.state == SLICE_STATE_STOPPED:
            try:
                all_vms = slice_obj.get_vms()
                for vm in all_vms:
                    if vm.state == 8:
                        raise DbError("资源分配中，请稍后启动！")
                controller = slice_obj.get_controller()
                if controller.host and controller.host.state != 1:
                    raise DbError("请确保控制器已启动！")
                gw = slice_obj.get_gw()
                if gw and gw.enable_dhcp and gw.state != 1:
                    raise DbError("请确保dhcp已启动！")
                slice_obj.start()
                flowvisor_update_slice_status(slice_obj.get_flowvisor(),
                                              slice_obj.name, True)
            except Exception:
                transaction.rollback()
                raise
            else:
                try:
                    update_slice_virtual_network(slice_obj)
                except:
                    pass


@transaction.commit_on_success
def stop_slice_api(slice_obj):
    """停止slice
    """
    LOG.debug('stop_slice_api')
    try:
        Slice.objects.get(id=slice_obj.id)
    except Exception, ex:
        raise DbError(ex)
    else:
        if slice_obj.state == SLICE_STATE_STARTED:
            try:
                slice_obj.stop()
                flowvisor_update_slice_status(slice_obj.get_flowvisor(),
                                              slice_obj.name, False)
            except Exception:
                transaction.rollback()
                raise


def update_slice_virtual_network(slice_obj):
    """更新slice的虚网，添加或删除交换机端口、网段、gateway、dhcp、vm后调用
    """
    LOG.debug('update_slice_virtual_network')
    try:
        Slice.objects.get(id=slice_obj.id)
    except Exception, ex:
        return DbError(ex)
    flowvisor = slice_obj.get_flowvisor()
    flowspace_name = str(slice_obj.name) + '_df'
    try:
        flowvisor_del_flowspace(flowvisor, flowspace_name)
    except:
        raise
    flowspace_dhcp_del(slice_obj, True)
    del_gateways = slice_obj.get_gws()
    for del_gateway in del_gateways:
        flowspace_gw_del(slice_obj, del_gateway)
    gw = slice_obj.get_gw()
    if gw and gw.state != 8 and gw.state != 9:
        flowspace_gw_add(slice_obj, gw.mac)
        if gw.enable_dhcp:
            flowspace_dhcp_add(slice_obj, True)
    switch_ports = slice_obj.get_switch_ports()
    default_flowspaces = slice_obj.get_default_flowspaces()
    for switch_port in switch_ports:
        for default_flowspace in default_flowspaces:
            in_port = str(switch_port.port)
            arg_match = matches_to_arg_match(
                in_port, default_flowspace.dl_vlan,
                default_flowspace.dl_vpcp, default_flowspace.dl_src,
                default_flowspace.dl_dst, default_flowspace.dl_type,
                default_flowspace.nw_src, default_flowspace.nw_dst,
                default_flowspace.nw_proto, default_flowspace.nw_tos,
                default_flowspace.tp_src, default_flowspace.tp_dst)
            try:
                flowvisor_add_flowspace(flowvisor, flowspace_name,
                                        slice_obj.name,
                                        default_flowspace.actions, 'cdn%nf',
                                        switch_port.switch.dpid,
                                        default_flowspace.priority, arg_match)
            except:
                raise


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
        switchs_ports = []
        for switch_id in switch_ids:
            switchs_ports.append({'id': switch_id, 'ports': ports[switch_id]})
        bandwidth = get_slice_links_bandwidths(switchs_ports, maclist)

        topology = {'switches': switches, 'links': links,
                    'normals': normals, 'specials': specials,
                    'bandwidth': bandwidth, 'maclist': maclist}
    except Exception, ex:
        print 1
        print ex
        return []
    else:
        print 2
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
                except Exception, ex:
                    print ex
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
