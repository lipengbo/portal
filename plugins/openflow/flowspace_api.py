# coding:utf-8
from models import *
from django.db import transaction
from CENI.Project.project_exception import *


import logging
LOG = logging.getLogger("CENI")


def flowspace_nw_add(slice_obj, old_nws, new_nm):
    """添加网段时添加flowspace
    """
    LOG.debug('flowspace_nw_add')
    from CENI.Project.slice_api import update_slice_virtual_network
    try:
        ceni_slice.objects.get(id=slice_obj.id)
    except ceni_slice.DoesNotExist:
        return False
    if new_nm:
        name = str(slice_obj.name) + '_df'
        nw_num = len(old_nws)
        if nw_num > 0:
            for i in range(nw_num):
                create_default_flowspace(slice_obj, name, '', '100', '', '',
                    '', '', '', '0x800', old_nws[i], new_nm, '', '', '', '')
                create_default_flowspace(slice_obj, name, '', '100', '', '',
                    '', '', '', '0x800', new_nm, old_nws[i], '', '', '', '')
        create_default_flowspace(slice_obj, name, '', '100', '', '',
            '', '', '', '0x800', new_nm, new_nm, '', '', '', '')
        create_default_flowspace(slice_obj, name, '', '100', '', '',
            '', '', '', '0x806', new_nm, new_nm, '', '', '', '')
        if not update_slice_virtual_network(slice_obj):
            return False
    return True


def flowspace_nw_del(slice_obj, del_nw):
    """删除网段时删除相应flowspace
    """
    LOG.debug('flowspace_nw_del')
    from CENI.Project.slice_api import update_slice_virtual_network
    try:
        ceni_slice.objects.get(id=slice_obj.id)
    except ceni_slice.DoesNotExist:
        return False
    if del_nw:
        name = str(slice_obj.name) + '_df'
        delete_default_flowspace(slice_obj, name, '', '', del_nw, '')
        delete_default_flowspace(slice_obj, name, '', '', '', del_nw)
        if not update_slice_virtual_network(slice_obj):
            return False
    return True


def flowspace_gw_add(slice_obj, new_gateway):
    """添加网关时添加flowspace
    """
    LOG.debug('flowspace_gw_add')
    from CENI.Project.slice_api import get_slice_nws, update_slice_virtual_network
    try:
        ceni_slice.objects.get(id=slice_obj.id)
    except ceni_slice.DoesNotExist:
        return False
    if new_gateway:
        name = str(slice_obj.name) + '_df'
        haved_nws = get_slice_nws(slice_obj)
        for haved_nw in haved_nws:
            create_default_flowspace(slice_obj, name, '', '100', '', '',
                '', '', new_gateway, '0x800', haved_nw, '', '', '', '', '')
            create_default_flowspace(slice_obj, name, '', '100', '', '',
                '', new_gateway, '', '0x800', '', haved_nw, '', '', '', '')
        if not update_slice_virtual_network(slice_obj):
            return False
    return True


def flowspace_gw_del(slice_obj, del_gateway):
    """删除网关时删除相应flowspace
    """
    LOG.debug('flowspace_gw_del')
    from CENI.Project.slice_api import update_slice_virtual_network
    try:
        ceni_slice.objects.get(id=slice_obj.id)
    except ceni_slice.DoesNotExist:
        return False
    if del_gateway:
        name = str(slice_obj.name) + '_df'
        delete_default_flowspace(slice_obj, name, del_gateway, '', '', '')
        delete_default_flowspace(slice_obj, name, '', del_gateway, '', '')
        if not update_slice_virtual_network(slice_obj):
            return False
    return True


def flowspace_dhcp_add(slice_obj, new_dhcp):
    """添加dhcp服务器时添加flowspace
    """
    LOG.debug('flowspace_dhcp_add')
    from CENI.Project.slice_api import get_slice_dhcps, get_slice_vms, update_slice_virtual_network
    try:
        ceni_slice.objects.get(id=slice_obj.id)
    except ceni_slice.DoesNotExist:
        return False
    if new_dhcp:
        name = str(slice_obj.name) + '_df'
        create_default_flowspace(slice_obj, name, '', '1', '', '',
            '', new_dhcp, '', '', '', '', '', '', '', '')
        haved_dhcps = get_slice_dhcps(slice_obj)
        if len(haved_dhcps) == 1:
            haved_vms = get_slice_vms(slice_obj)
            for haved_vm in haved_vms:
                create_default_flowspace(slice_obj, name, '', '1', '', '',
                    '', str(haved_vm.mac), '', '', '', '', '', '', '', '')
        if not update_slice_virtual_network(slice_obj):
            return False
    return True


def flowspace_dhcp_del(slice_obj, del_dhcp):
    """删除dhcp服务器时删除相应flowspace
    """
    LOG.debug('flowspace_dhcp_del')
    from CENI.Project.slice_api import get_slice_dhcps, get_slice_vms, update_slice_virtual_network
    try:
        ceni_slice.objects.get(id=slice_obj.id)
    except ceni_slice.DoesNotExist:
        return False
    if del_dhcp:
        name = str(slice_obj.name) + '_df'
        delete_default_flowspace(slice_obj, name, del_dhcp, '', '', '')
        haved_dhcps = get_slice_dhcps(slice_obj)
        if len(haved_dhcps) == 0:
            haved_vms = get_slice_vms(slice_obj)
            for haved_vm in haved_vms:
                delete_default_flowspace(slice_obj, name, str(haved_vm.mac), '', '', '')
        if not update_slice_virtual_network(slice_obj):
            return False
    return True


def flowspace_vm_add(slice_obj, new_vm):
    """添加虚拟机时添加flowspace
    """
    LOG.debug('flowspace_vm_add')
    from CENI.Project.slice_api import get_slice_dhcps, update_slice_virtual_network
    try:
        ceni_slice.objects.get(id=slice_obj.id)
    except ceni_slice.DoesNotExist:
        return False
    if new_vm:
        haved_dhcps = get_slice_dhcps(slice_obj)
        if len(haved_dhcps) != 0:
            name = str(slice_obj.name) + '_df'
            create_default_flowspace(slice_obj, name, '', '1', '', '',
                '', new_vm, '', '', '', '', '', '', '', '')
            if not update_slice_virtual_network(slice_obj):
                return False
    return True


def flowspace_vm_del(slice_obj, del_vm):
    """删除虚拟机时删除相应flowspace
    """
    LOG.debug('flowspace_vm_del')
    from CENI.Project.slice_api import get_slice_dhcps, update_slice_virtual_network
    try:
        ceni_slice.objects.get(id=slice_obj.id)
    except ceni_slice.DoesNotExist:
        return False
    if del_vm:
        haved_dhcps = get_slice_dhcps(slice_obj)
        if len(haved_dhcps) != 0:
            name = str(slice_obj.name) + '_df'
            delete_default_flowspace(slice_obj, name, del_vm, '', '', '')
            if not update_slice_virtual_network(slice_obj):
                return False
    return True


@transaction.commit_on_success
def create_default_flowspace(slice_obj, name, dpid, priority, in_port, dl_vlan,
    dl_vpcp, dl_src, dl_dst, dl_type, nw_src, nw_dst, nw_proto, nw_tos, tp_src,
    tp_dst):
    """创建默认flowspace
    """
    LOG.debug('create_default_flowspace')
    try:
        flowspace_obj = ceni_flowspace(
            name=name,
            dpid=dpid,
            priority=priority,
            in_port=in_port,
            dl_vlan=dl_vlan,
            dl_vpcp=dl_vpcp,
            dl_src=dl_src,
            dl_dst=dl_dst,
            dl_type=dl_type,
            nw_src=nw_src,
            nw_dst=nw_dst,
            nw_proto=nw_proto,
            nw_tos=nw_tos,
            tp_src=tp_src,
            tp_dst=tp_dst,
            is_default=1,
            actions=7)
        flowspace_obj.save()
        slice_flowspace = ceni_slice_resource(
            slice_id=slice_obj.id,
            resource_type=1,
            resource_id=flowspace_obj.id)
        slice_flowspace.save()
    except Exception, ex:
        transaction.rollback()


@transaction.commit_on_success
def delete_default_flowspace(slice_obj, name, dl_src, dl_dst, nw_src, nw_dst):
    """删除默认flowspace
    """
    LOG.debug('delete_default_flowspace')
    try:
        flowspace_objs = ceni_flowspace.objects.filter(name=name, is_default=1)
        if dl_src:
            flowspace_objs = ceni_flowspace.objects.filter(name=name,
                dl_src=dl_src, is_default=1)
        if dl_dst:
            flowspace_objs = ceni_flowspace.objects.filter(name=name,
                dl_dst=dl_dst, is_default=1)
        if nw_src:
            flowspace_objs = ceni_flowspace.objects.filter(name=name,
                nw_src=nw_src, is_default=1)
        if nw_dst:
            flowspace_objs = ceni_flowspace.objects.filter(name=name,
                nw_dst=nw_dst, is_default=1)
        for flowspace_obj in flowspace_objs:
            slice_flowspace = ceni_slice_resource.objects.filter(
                 slice_id=slice_obj.id,
                 resource_type=1,
                 resource_id=flowspace_obj.id)
            slice_flowspace.delete()
            flowspace_obj.delete()
    except Exception, ex:
        transaction.rollback()


def matches_to_arg_match(in_port, dl_vlan, dl_vpcp, dl_src, dl_dst, dl_type,
    nw_src, nw_dst, nw_proto, nw_tos, tp_src, tp_dst):
    """将12个匹配相转化为flowspace的arg_match参数格式
    """
    LOG.debug('matches_to_arg_match')
    match = ''
    if in_port:
        match += 'in_port=' + in_port + ','
    if dl_vlan:
        match += 'dl_vlan=' + dl_vlan + ','
    if dl_vpcp:
        match += 'dl_vpcp=' + dl_vpcp + ','
    if dl_src:
        match += 'dl_src=' + dl_src + ','
    if dl_dst:
        match += 'dl_dst=' + dl_dst + ','
    if dl_type:
        match += 'dl_type=' + dl_type + ','
    if nw_src:
        match += 'nw_src=' + nw_src + ','
    if nw_dst:
        match += 'nw_dst=' + nw_dst + ','
    if nw_proto:
        match += 'nw_proto=' + nw_proto + ','
    if nw_tos:
        match += 'nw_tos=' + nw_tos + ','
    if tp_src:
        match += 'tp_src=' + tp_src + ','
    if tp_dst:
        match += 'tp_dst=' + tp_dst + ','
    if match == '':
        arg_match = 'any'
    else:
        ls = len(match)
        arg_match = match[0:ls - 1]
    return arg_match


def get_flowspace_topology(slice_obj):
    """获取slice的用户自定义flowspace拓扑信息
    """
    LOG.debug('get_flowspace_topology')


@transaction.commit_on_success
def create_user_flowspace(slice_obj, name, dpid, priority, in_port, dl_vlan,
    dl_vpcp, dl_src, dl_dst, dl_type, nw_src, nw_dst, nw_proto, nw_tos, tp_src,
    tp_dst):
    """创建用户flowspace
    """
    LOG.debug('create_user_flowspace')
    try:
        flowspace_obj = ceni_flowspace(
            name=name,
            dpid=dpid,
            priority=priority,
            in_port=in_port,
            dl_vlan=dl_vlan,
            dl_vpcp=dl_vpcp,
            dl_src=dl_src,
            dl_dst=dl_dst,
            dl_type=dl_type,
            nw_src=nw_src,
            nw_dst=nw_dst,
            nw_proto=nw_proto,
            nw_tos=nw_tos,
            tp_src=tp_src,
            tp_dst=tp_dst,
            is_default=0,
            actions=7)
        flowspace_obj.save()
        slice_flowspace = ceni_slice_resource(
            slice_id=slice_obj.id,
            resource_type=1,
            resource_id=flowspace_obj.id)
        slice_flowspace.save()
    except Exception, ex:
        transaction.rollback()
        raise DbError(ex)


@transaction.commit_on_success
def edit_user_flowspace(flowspace_obj, dpid, priority, in_port, dl_vlan,
    dl_vpcp, dl_src, dl_dst, dl_type, nw_src, nw_dst, nw_proto, nw_tos, tp_src,
    tp_dst):
    """编辑用户flowspace
    """
    LOG.debug('edit_user_flowspace')
    try:
        flowspace_obj.dpid = dpid
        flowspace_obj.priority = priority
        flowspace_obj.in_port = in_port
        flowspace_obj.dl_vlan = dl_vlan
        flowspace_obj.dl_vpcp = dl_vpcp
        flowspace_obj.dl_src = dl_src
        flowspace_obj.dl_dst = dl_dst
        flowspace_obj.dl_type = dl_type
        flowspace_obj.nw_src = nw_src
        flowspace_obj.nw_dst = nw_dst
        flowspace_obj.nw_proto = nw_proto
        flowspace_obj.nw_tos = nw_tos
        flowspace_obj.tp_src = tp_src
        flowspace_obj.tp_dst = tp_dst
        flowspace_obj.save()
    except Exception, ex:
        transaction.rollback()
        raise DbError(ex)


def delete_user_flowspace(flowspace_obj):
    """删除用户flowspace
    """
    LOG.debug('edit_user_flowspace')
    try:
        flowspace_obj.delete()
    except Exception, ex:
        transaction.rollback()
        raise DbError(ex)
