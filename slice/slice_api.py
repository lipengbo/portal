# coding:utf-8
from slice.models import Slice
from project.models import Project
from slice.slice_exception import DbError
from plugins.openflow.flowvisor_api import flowvisor_del_slice, flowvisor_del_flowspace, flowvisor_add_flowspace
from plugins.openflow.flowspace_api import matches_to_arg_match
from django.db import transaction
import time
import datetime

import logging
LOG = logging.getLogger("ccf")


@transaction.commit_on_success
def create_slice_api(project, name, description, island, user):
    """slice添加交换端口
    """
    LOG.debug('create_slice_api')
    try:
        Slice.objects.get(name=name)
    except Slice.DoesNotExist:
        if project and island and user:
            flowvisors = island.flowvisor_set.all()
            if flowvisors:
                date_now = datetime.datetime.now()
                date_delta = datetime.timedelta(days=30)
                expiration_date = date_now + date_delta
                try:
                    slice_obj = Slice(owner=user,
                        name=name,
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
    try:
        Slice.objects.get(id=slice_obj.id)
    except Slice.DoesNotExist:
        pass
    else:
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
    LOG.debug('delete_slice_api')
    try:
        Slice.objects.get(id=slice_obj.id)
    except Slice.DoesNotExist:
        pass
    else:
        slice_id = slice_obj.id
        try:
#             删除虚拟机
#             删除dhcp
#             删除网关
#             删除控制器
#             删除slice网络地址
#             删除交换机端口
#             删除底层slice
            flowvisor_del_slice(slice_obj.get_flowvisor, slice_obj.name)
#             删除slice记录
            slice_obj.delete()
        except Exception, ex:
            transaction.rollback()
            raise DbError(ex)


def update_slice_virtual_network(slice_obj):
    """更新slice的虚网，添加或删除交换机端口、网段、gateway、dhcp、vm后调用
    """
    LOG.debug('update_slice_virtual_network')
    try:
        Slice.objects.get(id=slice_obj.id)
    except Slice.DoesNotExist:
        return False
    flowvisor = slice_obj.get_flowvisor()
    flowspace_name = str(slice_obj.name) + '_df'
    try:
        flowvisor_del_flowspace(flowvisor, flowspace_name)
    except Exception, ex:
        LOG.debug(str(ex))
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
                flowvisor_add_flowspace(flowvisor, flowspace_name, slice_obj.name,
                    default_flowspace.actions, 'cdn%nf', switch_port.switch.dpid,
                    default_flowspace.priority, arg_match)
            except Exception, ex:
                LOG.debug(str(ex))
    return True


def get_slice_topology(slice_obj):
    """获取slice拓扑信息
    """
    LOG.debug('get_slice_topology')
    switches = []
    links = []
    specials = []
    normals = []
    haved_dpids = get_slice_dpids(slice_obj)
    for haved_dpid in haved_dpids:
        switch = {'dpid': haved_dpid}
        switches.append(switch)
    flowvisor = slice_obj.get_flowvisor()
    if flowvisor:
        link_objs = flowvisor.flowvisorlink_set.filter(
            src_dpid__in=haved_dpids, dst_dpid__in=haved_dpids)
    for link_obj in link_objs:
        link = {'src_switch': link_obj.src_dpid, 'dst_switch': link_obj.dst_dpid}
        links.append(link)
    haved_server_ovs_ids = []
    server_ovss = get_slice_server_ovss(slice_obj)
    for server_ovs in server_ovss:
        haved_server_ovs_ids.append(server_ovs.id)
    haved_server_ids = []
    haved_servers = get_slice_servers(slice_obj)
    for haved_server in haved_servers:
        haved_server_ids.append(haved_server.id)
    vms = get_slice_vms(slice_obj)
    for vm in vms:
        if vm.belong_server_id in haved_server_ids:
            link1s = ceni_facility_topology.objects.filter(
                facility1_classid=1, facility2_classid=2,
                facility1_id=vm.belong_server_id, facility2_id__in=haved_server_ovs_ids)
            link2s = ceni_facility_topology.objects.filter(
                facility2_classid=1, facility1_classid=2,
                facility2_id=vm.belong_server_id, facility1_id__in=haved_server_ovs_ids)
            links = []
            links.extend(link1s)
            links.extend(link2s)
            status = isVmOn(vm.belong_server_id, vm.id)
            if status:
                host_status = 1
            else:
                host_status = 0
            vm_infos = []
            for link in links:
                try:
                    if link.facility1_classid == 2:
                        switch = ceni_facility_server.objects.get(
                            id=link1s[0].facility1_id)
                    else:
                        switch = ceni_facility_server.objects.get(
                            id=link1s[0].facility2_id)
                    vm_infos.append({'macAddress': vm.ip, 'switchDPID': switch.dpid,
                        'hostid': vm.id, 'hostStatus': host_status})
                except:
                    pass
            if len(vm_infos) == 1:
                normals.extend(vm_infos)
            else:
                specials.extend(vm_infos)
    topology = {'switches': switches, 'links': links,
                'normals': normals, 'specials': specials}
    return topology


def get_slice_ovss(slice_obj):
    """获取slice选择的交换机
    """
    LOG.debug('get_slice_ovss')


def get_slice_dpids(slice_obj):
    """获取slice选择的交换机
    """
    LOG.debug('get_slice_dpids')
    haved_dpids = []
    if slice_obj:
        ovss = get_slice_ovss(slice_obj)
        for ovs in ovss:
            haved_dpids.append(ovs.dpid)
    return haved_dpids


def get_slice_resource(slice_obj):
    """获取slice资源，包括节点、flowvisor、控制器、交换机端口
    """
    LOG.debug('get_slice_resource')
