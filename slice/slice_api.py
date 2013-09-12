# coding:utf-8
from models import *
from project.models import Project
from slice_exception import *
from django.db import transaction
import time
import datetime

import logging
LOG = logging.getLogger("CENI")


@transaction.commit_on_success
def create_slice_api(project, name, description, island, user):
    """slice添加交换端口
    """
    LOG.debug('create_slice_api')
    try:
        Slice.objects.get(name=name)
    except Slice.DoesNotExist:
        if project and island and user:
            try:
                date_now = datetime.datetime.now()
                date_delta = datetime.timedelta(days=30)
                expiration_date = date_now + date_delta
                slice_obj = Slice(owner=user,
                    name=name,
                    description=description,
                    project=project,
                    date_expired=expiration_date)
                slice_obj.save()
                slice_obj.add_island(island)
                return slice_obj
            except Exception, ex:
                transaction.rollback()
                raise DbError(ex)
        else:
            raise DbError("数据库异常")
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
                slice_obj.description = new_description
                slice_obj.save()
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
            slice_remove_all_ovss(slice_obj)
            slice_resources = ceni_slice_resource.objects.filter(slice_id=slice_obj.id)  
            for slice_resource in slice_resources:
                if slice_resource.resource_type == 1:
                    try:
                        resource = ceni_flowspace.objects.get(id=slice_resource.resource_id)
                    except:
                        slice_resource.delete()
                    else:
                        if resource.is_default == 0:
                            resource.delete()
                            slice_resource.delete()
                else:
                    if slice_resource.resource_type == 2:
                        resource = ceni_virtual_server.objects.get(id=slice_resource.resource_id)
                        try:
                            if get_internet_access_status(resource.id, resource.ip):
                                cancel_internet_access(resource.id, resource.ip)
                        except:
                            pass
                        delete_vm(resource)
                        resource.delete()
                        slice_resource.delete()
            flowvisor_controllers = ceni_flowvisor_related.objects.filter(
                slice_id=slice_obj.id, related_type=1)
            for flowvisor_controller in flowvisor_controllers:
                flowvisor = ceni_facility_server.objects.get(
                    id=flowvisor_controller.flowvisor_id)
                controller = ceni_facility_server.objects.get(
                    id=flowvisor_controller.related_id)
                flowvisor_del_slice(flowvisor, slice_obj)
                slice_remove_controller(slice_obj, flowvisor, controller)
            slice_obj.delete()
        except Exception, ex:
            transaction.rollback()
            raise DbError(ex)
        try:
            slice_clear_network(slice_id)
        except Exception, e:
            LOG.error(str(e))
        delete_slice_perm(int(slice_id))


def update_slice_virtual_network(slice_obj):
    """更新slice的虚网，添加或删除交换机端口、网段、gateway、dhcp、vm后调用
    """
    LOG.debug('update_slice_virtual_network')
    try:
        Slice.objects.get(id=slice_obj.id)
    except Slice.DoesNotExist:
        return False
    flowvisor = get_slice_flowvisor(slice_obj)
    flowspace_name = str(slice_obj.name) + '_df'
    try:
        flowvisor_del_flowspace(flowvisor, flowspace_name)
    except Exception, ex:
        LOG.debug(str(ex))
    dpid_ports = ceni_slice_switch.objects.filter(slice_id=slice_obj.id)
    default_flowspaces = ceni_flowspace.objects.filter(name=flowspace_name,
                                                       is_default=1)
    for dpid_port in dpid_ports:
        for default_flowspace in default_flowspaces:
            if dpid_port.port < 0:
                in_port = ''
            else:
                in_port = str(dpid_port.port)
            arg_match = matches_to_arg_match(
                in_port, default_flowspace.dl_vlan,
                default_flowspace.dl_vpcp, default_flowspace.dl_src,
                default_flowspace.dl_dst, default_flowspace.dl_type,
                default_flowspace.nw_src, default_flowspace.nw_dst,
                default_flowspace.nw_proto, default_flowspace.nw_tos,
                default_flowspace.tp_src, default_flowspace.tp_dst)
            try:
                print arg_match
                flowvisor_add_flowspace(flowvisor, flowspace_name, slice_obj.name,
                    default_flowspace.actions, 'cdn%nf', dpid_port.dpid,
                    default_flowspace.priority, arg_match)
            except Exception, ex:
                LOG.debug(str(ex))
    return True


def get_slice_resource(slice_obj):
    """获取slice资源，包括节点、flowvisor、控制器、交换机端口
    """
    LOG.debug('get_slice_resource')


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
    flowvisor = get_slice_flowvisor(slice_obj)
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


def get_slice_island(slice_obj):
    """获取slice选择的节点
    """
    LOG.debug('get_slice_island')
    try:
        flowvisor_controllers = ceni_flowvisor_related.objects.filter(
            slice_id=slice_obj.id,
            related_type=1)
        if flowvisor_controllers:
            island = ceni_island.objects.get(
                id=flowvisor_controllers[0].island_id)
            return island
        else:
            return None
    except:
        return None


def get_slice_flowvisor(slice_obj):
    """获取slice的flowvisor
    """
    LOG.debug('get_slice_flowvisor')
    try:
        flowvisor_controllers = ceni_flowvisor_related.objects.filter(
            slice_id=slice_obj.id,
            related_type=1)
        if flowvisor_controllers:
            flowvisor = ceni_facility_server.objects.get(
                id=flowvisor_controllers[0].flowvisor_id)
            return flowvisor
        else:
            return None
    except:
        return None


def get_slice_controller(slice_obj):
    """获取slice选择的控制器
    """
    LOG.debug('get_slice_controller')
    try:
        flowvisor_controllers = ceni_flowvisor_related.objects.filter(
            slice_id=slice_obj.id,
            related_type=1)
        if flowvisor_controllers:
            controller = ceni_facility_server.objects.get(
                id=flowvisor_controllers[0].related_id)
            return controller
        else:
            return None
    except:
        return None


def get_slice_ovss(slice_obj):
    """获取slice选择的交换机
    """
    LOG.debug('get_slice_ovss')
    haved_dpids = get_slice_dpids(slice_obj)
    ovss = ceni_facility_server.objects.filter(dpid__in=haved_dpids)
    return ovss


def get_slice_dpids(slice_obj):
    """获取slice选择的交换机
    """
    LOG.debug('get_slice_dpids')
    haved_dpids = []
    if slice_obj:
        flowvisor_controllers = ceni_flowvisor_related.objects.filter(
            slice_id=slice_obj.id,
            related_type=1)
        if flowvisor_controllers:
            flowvisor_ovss = ceni_flowvisor_related.objects.filter(
                slice_id=slice_obj.id,
                flowvisor_id=flowvisor_controllers[0].flowvisor_id,
                related_type=2)
            for flowvisor_ovs in flowvisor_ovss:
                try:
                    ovs = ceni_facility_server.objects.get(id=flowvisor_ovs.related_id)
                except:
                    pass
                else:
                    haved_dpids.append(ovs.dpid)
    return haved_dpids


def get_slice_server_dpids(slice_obj):
    """获取slice关联交换机dpid
    """
    LOG.debug('get_slice_servers')
    haved_dpids = get_slice_dpids(slice_obj)
    haved_server_dpids = []
    for haved_dpid in haved_dpids:
        dpid_lists = haved_dpid.split(':')
        if len(dpid_lists) > 2 and dpid_lists[0] == '7f' and dpid_lists[1] == 'ff':
            haved_server_dpids.append(haved_dpid)
    return haved_server_dpids


def get_slice_server_ovss(slice_obj):
    """获取slice关联交换机dpid
    """
    LOG.debug('get_slice_server_ovss')
    haved_server_dpids = get_slice_server_dpids(slice_obj)
    ovss = ceni_facility_server.objects.filter(id__in=haved_server_dpids)
    return ovss


def get_slice_servers(slice_obj):
    """获取slice可用服务器
    """
    LOG.debug('get_slice_servers')
    haved_server_ovss = get_slice_server_ovss(slice_obj)
    ovs_ids = []
    link_ids = []
    for haved_server_ovs in haved_server_ovss:
        ovs_ids.append(haved_server_ovs.id)
    link1s = ceni_facility_topology.objects.filter(
        facility1_classid=1, facility2_classid=2, facility2_id__in=ovs_ids)
    for link1 in link1s:
        link_ids.append(link1.facility1_id)
    link2s = ceni_facility_topology.objects.filter(
        facility1_classid=2, facility1_id__in=ovs_ids, facility2_classid=1)
    for link2 in link2s:
        link_ids.append(link2.facility2_id)
    servers = ceni_facility_server.objects.filter(id__in=link_ids)
    return servers


def get_slice_ovs_ports(slice_obj):
    """获取slice选择的交换机端口
    """
    LOG.debug('get_slice_ovs_ports')


def get_slice_vms(slice_obj):
    """获取slice的虚拟机
    """
    LOG.debug('get_slice_vms')
    try:
        vm_ids = []
        slice_vms = ceni_slice_resource.objects.filter(
            slice_id=slice_obj.id, resource_type=2)
        for slice_vm in slice_vms:
            vm_ids.append(slice_vm.resource_id)
        vms = ceni_virtual_server.objects.filter(id__in=vm_ids)
        return vms
    except:
        return []


def get_slice_nws(slice_obj):
    """获取slice的网段
    """
    LOG.debug('get_slice_nws')
    return slice_getall_networks_with_simple_format(slice_obj.id)


def get_slice_gateways(slice_obj):
    """获取slice的网关
    """
    LOG.debug('get_slice_gateways')
    return []


def get_slice_dhcps(slice_obj):
    """获取slice的dhcp
    """
    LOG.debug('get_slice_dhcps')
    return []


def get_slice_default_flowspaces(slice_obj):
    """获取slice的默认flowspace
    """
    LOG.debug('get_slice_default_flowspaces')
    try:
        default_flowspaces = []
        slice_flowspaces = ceni_facility_server.objects.filter(
            slice_id=slice_obj.id, facility_type=1)
        for slice_flowspace in slice_flowspaces:
            if slice_flowspace.is_default == 1:
                default_flowspaces.append(slice_flowspace)
        return default_flowspaces
    except:
        return []


def get_slice_user_flowspaces(slice_obj):
    """获取slice的用户自定义flowspace
    """
    LOG.debug('get_slice_user_flowspaces')
    try:
        user_flowspaces = []
        slice_flowspaces = ceni_facility_server.objects.filter(
            slice_id=slice_obj.id, facility_type=1)
        for slice_flowspace in slice_flowspaces:
            if slice_flowspace.is_default == 0:
                user_flowspaces.append(slice_flowspace)
        return user_flowspaces
    except:
        return []
