# coding:utf-8
from models import *
from CENI.Project.project_exception import *
from django.db import transaction
import logging
LOG = logging.getLogger("CENI")
OVS_TYPE = {'NOMAL': 1, 'EXTERNAL': 2, 'RELATED': 3}


@transaction.commit_on_success
def slice_add_ovss(slice_obj, new_dpids):
    """slice添加交换
    """
    LOG.debug('slice_add_ovss')
    from CENI.Project.slice_api import get_slice_flowvisor, get_slice_island, get_slice_dpids, update_slice_virtual_network
    try:
        ceni_slice.objects.get(id=slice_obj.id)
    except Exception, ex:
        raise DbError(ex)
    flowvisor = get_slice_flowvisor(slice_obj)
    island = get_slice_island(slice_obj)
    flag = 0
    if flowvisor and island:
        try:
            for new_dpid in new_dpids:
                try:
                    ovs = ceni_facility_server.objects.get(dpid=new_dpid)
                    ceni_island_facility.objects.get(island_id=island.id,
                                                     facility_type=2,
                                                     facility_id=ovs.id)
                except:
                    pass
                else:
                    flowvisor_ovs = ceni_flowvisor_related(
                        slice_id=slice_obj.id,
                        flowvisor_id=flowvisor.id,
                        related_id=ovs.id,
                        related_type=2,
                        island_id=island.id)
                    flowvisor_ovs.save()
                    haved_dpids = get_slice_dpids(slice_obj)
                    dst_links = flowvisor.flowvisorlink_set.filter(
                        src_dpid__in=haved_dpids, dst_dpid=new_dpid)
                    src_links = flowvisor.flowvisorlink_set.filter(
                        dst_dpid__in=haved_dpids, src_dpid=new_dpid)
                    links = []
                    links.extend(src_links)
                    links.extend(dst_links)
                    for link in links:
                        slice_add_ovs_ports(slice_obj, link.src_dpid, link.src_port)
                        slice_add_ovs_ports(slice_obj, link.dst_dpid, link.dst_port)
                        flag = 1
            if flag == 1:
                update_slice_virtual_network(slice_obj)
        except Exception, ex:
            transaction.rollback()
            raise DbError(ex)
    else:
        raise DbError("数据库异常")


@transaction.commit_on_success
def slice_change_ovss(slice_obj, cur_dpids):
    """slice更新交换
    """
    LOG.debug('slice_change_ovss')
    from CENI.Project.slice_api import get_slice_dpids
    haved_dpids = get_slice_dpids(slice_obj)
    try:
        if set(haved_dpids).issubset(set(cur_dpids)):
            add_dpids = []
            for cur_dpid in cur_dpids:
                if cur_dpid not in haved_dpids:
                    add_dpids.append(cur_dpid)
            slice_add_ovss(slice_obj, add_dpids)
        else:
            slice_remove_all_ovss(slice_obj)
            slice_add_ovss(slice_obj, cur_dpids)
    except:
        raise


@transaction.commit_on_success
def slice_remove_all_ovss(slice_obj):
    """slice移除所有交换
    """
    LOG.debug('slice_remove_all_ovss')
    from CENI.Project.slice_api import get_slice_dpids
    try:
        ceni_slice.objects.get(id=slice_obj.id)
    except Exception, ex:
        pass
    else:
        try:
            haved_dpids = get_slice_dpids(slice_obj)
            slice_remove_ovss(slice_obj, haved_dpids)
        except Exception, ex:
            transaction.rollback()
            raise DbError(ex)


@transaction.commit_on_success
def slice_remove_ovss(slice_obj, remove_dpids):
    """slice移除交换
    """
    LOG.debug('slice_remove_ovss')
    from CENI.Project.slice_api import get_slice_flowvisor, get_slice_dpids, update_slice_virtual_network
    try:
        ceni_slice.objects.get(id=slice_obj.id)
        flowvisor = get_slice_flowvisor(slice_obj)
    except Exception, ex:
        pass
    else:
        flag = 0
        try:
            haved_dpids = get_slice_dpids(slice_obj)
            for remove_dpid in remove_dpids:
                try:
                    ovs = ceni_facility_server.objects.get(dpid=remove_dpid)
                    flowvisor_ovs = ceni_flowvisor_related.objects.get(
                        slice_id=slice_obj.id,
                        related_id=ovs.id,
                        related_type=2)
                except:
                    pass
                else:
                    dst_links = flowvisor.flowvisorlink_set.filter(
                        src_dpid__in=haved_dpids, dst_dpid=remove_dpid)
                    src_links = flowvisor.flowvisorlink_set.filter(
                        dst_dpid__in=haved_dpids, src_dpid=remove_dpid)
                    links = []
                    links.extend(src_links)
                    links.extend(dst_links)
                    for link in links:
                        slice_remove_ovs_ports(slice_obj, link.src_dpid, link.src_port)
                        slice_remove_ovs_ports(slice_obj, link.dst_dpid, link.dst_port)
                    flowvisor_ovs.delete()
                    flag = 1
            if flag == 1:
                update_slice_virtual_network(slice_obj)
        except Exception, ex:
            transaction.rollback()
            raise DbError(ex)


@transaction.commit_on_success
def slice_add_ovs_ports(slice_obj, dpid, port):
    """slice添加交换端口
    """
    LOG.debug('slice_add_ovs_ports')
    try:
        ceni_slice.objects.get(id=slice_obj.id)
        ovs = ceni_facility_server.objects.get(dpid=dpid)
    except Exception, ex:
        raise DbError(ex)
#     dpid_lists = dpid.split(':')
#     if len(dpid_lists) > 2 and dpid_lists[0] == 'ff' and dpid_lists[1] == 'ff':
#         port = -1
    slice_dpid_ports_count = ceni_slice_switch.objects.filter(
        slice_id=slice_obj.id,
        switch_id=ovs.id,
        dpid=ovs.dpid,
        port=port).count()
    if slice_dpid_ports_count == 0:
        try:
            slice_dpid_port = ceni_slice_switch(
                slice_id=slice_obj.id,
                switch_id=ovs.id,
                dpid=ovs.dpid,
                port=port)
            slice_dpid_port.save()
        except Exception, ex:
            transaction.rollback()
            raise DbError(ex)


@transaction.commit_on_success
def slice_remove_ovs_ports(slice_obj, dpid, port):
    """slice移除交换机端口
    """
    LOG.debug('slice_remove_ovs_ports')
    try:
        ceni_slice.objects.get(id=slice_obj.id)
    except Exception, ex:
        pass
    else:
        try:
            slice_dpid_ports = ceni_slice_switch.objects.filter(
                slice_id=slice_obj.id,
                dpid=dpid,
                port=port)
            slice_dpid_ports.delete()
        except Exception, ex:
            transaction.rollback()
            raise DbError(ex)


@transaction.commit_on_success
def slice_remove_all_ovs_ports(slice_obj):
    """slice移除交换机端口
    """
    LOG.debug('slice_remove_ovs_ports')
    try:
        ceni_slice.objects.get(id=slice_obj.id)
    except Exception, ex:
        pass
    else:
        try:
            slice_dpid_ports = ceni_slice_switch.objects.filter(
                slice_id=slice_obj.id)
            slice_dpid_ports.delete()
        except Exception, ex:
            transaction.rollback()
            raise DbError(ex)



def slice_get_ovs_ports():
    """获取slice在一个交换机上选择的端口
    """
    LOG.debug('slice_get_ovs_ports')


def get_ovs_servers(ovs):
    """获取交换机下链接的服务器
    """
    LOG.debug('slice_get_ovs_servers')
    try:
        if get_ovs_type(ovs) == OVS_TYPE['RELATED']:
            ovs_servers = []
            link1s = ceni_facility_topology.objects.filter(
                facility1_classid=1, facility2_classid=2,
                facility2_id=ovs.id)
            link2s = ceni_facility_topology.objects.filter(
                facility2_classid=1, facility1_classid=2,
                facility1_id=ovs.id)
            for link1 in link1s:
                try:
                    server = ceni_facility_server.objects.get(id=link1.facility1_id)
                except:
                    pass
                else:
                    ovs_servers.append(server)
            for link2 in link2s:
                try:
                    server = ceni_facility_server.objects.get(id=link2.facility2_id)
                except:
                    pass
                else:
                    ovs_servers.append(server)
            return ovs_servers
        else:
            return []
    except:
        return []


def slice_get_ovs_vms(slice_obj, ovs):
    """获取slice在一个交换机下创建的虚拟机
    """
    LOG.debug('slice_get_ovs_vms')
    from CENI.Project.slice_api import get_slice_vms
    try:
        if get_ovs_type(ovs) == OVS_TYPE['RELATED']:
            ovs_vms = []
            ovs_servers = get_ovs_servers(ovs)
            ovs_server_ids = []
            for ovs_server in ovs_servers:
                ovs_server_ids.append(ovs_server.id)
            if ovs_server_ids:
                vms = get_slice_vms(slice_obj)
                for vm in vms:
                    if vm.belong_server_id in ovs_server_ids:
                        ovs_vms.append(vm)
            return ovs_vms
        else:
            return []
    except:
        return []


def slice_get_ovs_dhcps(slice_obj, ovs):
    """获取slice在一个交换机下创建的dhcp服务器
    """
    LOG.debug('slice_get_ovs_dhcps')
    from CENI.Project.slice_api import get_slice_dhcps
    try:
        if get_ovs_type(ovs) == OVS_TYPE['RELATED']:
            ovs_dhcps = []
            ovs_servers = get_ovs_servers(ovs)
            ovs_server_ids = []
            for ovs_server in ovs_servers:
                ovs_server_ids.append(ovs_server.id)
            if ovs_server_ids:
                dhcps = get_slice_dhcps(slice_obj)
                for dhcp in dhcps:
                    if dhcp.belong_server_id in ovs_server_ids:
                        ovs_dhcps.append(dhcp)
            return ovs_dhcps
        else:
            return []
    except:
        return []


def slice_get_ovs_gws(slice_obj, ovs):
    """获取slice在一个交换机下创建的网关
    """
    LOG.debug('slice_get_ovs_gws')
    from CENI.Project.slice_api import get_slice_gateways
    try:
        if get_ovs_type(ovs) == OVS_TYPE['RELATED']:
            ovs_gws = []
            ovs_servers = get_ovs_servers(ovs)
            ovs_server_ids = []
            for ovs_server in ovs_servers:
                ovs_server_ids.append(ovs_server.id)
            if ovs_server_ids:
                gws = get_slice_gateways(slice_obj)
                for gw in gws:
                    if gw.belong_server_id in ovs_server_ids:
                        ovs_gws.append(gw)
            return ovs_gws
        else:
            return []
    except:
        return []


def get_ovs_type(ovs):
    """获取交换机类型，交换节点、虚拟机关联节点、网络出口节点
    """
    LOG.debug('get_ovs_type')
    try:
        dpid_lists = ovs.dpid.split(':')
        if len(dpid_lists) > 2 and dpid_lists[0] == '7f' and dpid_lists[1] == 'ff':
            return OVS_TYPE['RELATED']
        if ovs.tag == 2:
            return OVS_TYPE['EXTERNAL']
        return OVS_TYPE['NOMAL']
    except:
        return OVS_TYPE['NOMAL']


def get_ovs_ports():
    """获取交换机所有端口
    """
    LOG.debug('get_ovs_ports')


def get_ovs_vms():
    """获取交换机下挂所有虚拟机
    """
    LOG.debug('get_ovs_vms')


def ovs_can_deleted(slice_obj, ovs):
    """判断交换机是否可从slice中删除，若交换机被用户flowspace选择或创建了虚拟机、dhcp、网关则不能删
    """
    LOG.debug('ovs_can_deleted')
    from CENI.Project.slice_api import get_slice_user_flowspaces
    try:
        ceni_slice.objects.get(id=slice_obj.id)
        ceni_facility_server.objects.get(id=ovs.id)
    except:
        return True
    else:
        user_flowspaces = get_slice_user_flowspaces(slice_obj)
        for user_flowspace in user_flowspaces:
            if ovs.dpid in user_flowspace.dpid.split(','):
                return False
        if slice_get_ovs_vms(slice_obj, ovs) or slice_get_ovs_dhcps(slice_obj, ovs) or slice_get_ovs_gws(slice_obj, ovs):
            return False
        return True
