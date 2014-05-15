# coding:utf-8
from slice.models import Slice
from resources.models import Switch, VirtualSwitch, OVS_TYPE, SwitchPort, SlicePort, OwnerDevice
from slice.slice_exception import DbError
from plugins.openflow.flowspace_api import flowspace_gw_add, flowspace_gw_del
from django.db import transaction
from plugins.openflow.models import Link
import logging
import traceback
LOG = logging.getLogger("CENI")


def slice_add_ovs_or_ports(slice_obj, ovs_or_ports, tp_mod):
    """slice添加交换端口，包括选择交换机模式和选择交换机端口模式。
    """
    LOG.debug('slice_add_ovs_ports')
    try:
        Slice.objects.get(id=slice_obj.id)
        if int(tp_mod) == 2:
            switches = ovs_or_ports
            ports = []
            for switch in switches:
                slice_obj.add_resource(switch)
                s_ports = switch.switchport_set.all()
                ports.extend(s_ports)
            links = Link.objects.filter(source__in=ports, target__in=ports)
            add_ports = []
            for link in links:
                if link.source not in add_ports:
                    add_ports.append(link.source)
                if link.target not in add_ports:
                    add_ports.append(link.target)
            for add_port in add_ports:
                slice_obj.add_resource(add_port)
                if add_port.switch.type() == OVS_TYPE['EXTERNAL']:
                    try:
                        add_port.switch.virtualswitch
                    except VirtualSwitch.DoesNotExist:
                        pass
                    else:
                        flowspace_gw_add(slice_obj, add_port.switch.virtualswitch.server.mac)
        else:
            ports = ovs_or_ports
            for port in ports:
                slice_obj.add_resource(port)
                if port.switch.type() == OVS_TYPE['EXTERNAL']:
                    try:
                        port.switch.virtualswitch
                    except VirtualSwitch.DoesNotExist:
                        pass
                    else:
                        flowspace_gw_add(slice_obj, port.switch.virtualswitch.server.mac)
    except Exception, ex:
#         print ex
        raise DbError("资源分配失败！")


@transaction.commit_on_success
def slice_change_ovs_ports(slice_obj, ovs_ports):
    """slice更新交换端口
    """
    LOG.debug('slice_change_ovs_ports')
    try:
        Slice.objects.get(id=slice_obj.id)
    except Exception, ex:
        raise DbError(ex)
    try:
        haved_ovs_ports = slice_obj.get_switch_ports()
        cur_ovs_port_ids = []
        haved_ovs_port_ids = []
        for haved_ovs_port in haved_ovs_ports:
            haved_ovs_port_ids.append(haved_ovs_port.id)
        for ovs_port in ovs_ports:
            cur_ovs_port_ids.append(ovs_port.id)
            if ovs_port.id not in haved_ovs_port_ids:
                slice_obj.add_resource(ovs_port)
                if ovs_port.switch.type() == OVS_TYPE['EXTERNAL']:
                    flowspace_gw_add(slice_obj, ovs_port.switch.virtualswitch.server.mac)
        for haved_ovs_port in haved_ovs_ports:
            if haved_ovs_port.id not in cur_ovs_port_ids:
                slice_obj.remove_resource(haved_ovs_port)
                if haved_ovs_port.switch.type() == OVS_TYPE['EXTERNAL']:
                    flowspace_gw_del(slice_obj, haved_ovs_port.switch.virtualswitch.server.mac)
    except Exception, ex:
        transaction.rollback()
        raise DbError(ex)


# def get_ovs_type(ovs):
#     """获取交换机类型，交换节点、虚拟机关联节点、网络出口节点
#     """
#     LOG.debug('get_ovs_type')
#     try:
#         dpid_lists = ovs.dpid.split(':')
#         if len(dpid_lists) > 2 and dpid_lists[0] == '7f' and dpid_lists[1] == 'ff':
#             return OVS_TYPE['RELATED']
#         if ovs.tag == 2:
#             return OVS_TYPE['EXTERNAL']
#         return OVS_TYPE['NOMAL']
#     except:
#         return OVS_TYPE['NOMAL']


def find_ovs_by_dpid(dpid):
    """通过dpid查找交换机记录，可能是switch或virtualswitch
    """
    LOG.debug('find_ovs_by_dpid')
    ovss = Switch.objects.filter(dpid=dpid)
    if ovss:
        if ovss[0].is_virtual():
            return ovss[0].virtualswitch
        else:
            return ovss[0]
    else:
        return None


def get_ovs_class(ovs):
    """通过dpid查找交换机记录，可能是Switch或VirtualSwitch
    """
    LOG.debug('get_ovs_class')
    return ovs.__class__.__name__


def get_ports_by_switchs(switch_ids):
    """根据选择的交换机获取链路端口
    """
    print 'get_ports_by_switchs'
#     print switch_ids
#     交换机
    try:
        add_ports = []
        if switch_ids:
            switch_objs = []
            sw_ids = switch_ids.split(',')
            for sw_id in sw_ids:
                try:
                    switch = Switch.objects.get(id=int(sw_id))
                except:
                    pass
                else:
                    switch_objs.append(switch)
#             print switch_objs
            ports = []
            for switch_obj in switch_objs:
                s_ports = switch_obj.switchport_set.all()
                ports.extend(s_ports)
            links = Link.objects.filter(source__in=ports, target__in=ports)
#             print links
            for link in links:
                if link.source not in add_ports:
                    add_ports.append(link.source)
                if link.target not in add_ports:
                    add_ports.append(link.target)
#         print add_ports
        return add_ports
    except Exception, ex:
        print ex
        return []


def get_select_topology(tp_mod, switch_ids, switch_port_ids):
    """获取选择的交换机或交换机端口的拓扑信息
    """
    print 'get_select_topology'
#     交换机
    try:
        switches = []
        links = []
        switch_objs = []
        switch_ports = []
        if int(tp_mod) == 2:
            if switch_ids:
                switches_ports = {}
                ports = []
                sw_ids = switch_ids.split(',')
                for sw_id in sw_ids:
                    try:
                        switch = Switch.objects.get(id=int(sw_id))
                    except:
                        pass
                    else:
                        switch_objs.append(switch)
                        s_ports = switch.switchport_set.all()
                        ports.extend(s_ports)
                add_links = Link.objects.filter(source__in=ports, target__in=ports)
                for link in add_links:
                    if link.source not in switch_ports:
                        switch_ports.append(link.source)
                        if link.source.switch.id not in switches_ports:
                            switches_ports[link.source.switch.id] = []
                        switches_ports[link.source.switch.id].append({'name': link.source.name,
                                                                      'port': link.source.port})
                    if link.target not in switch_ports:
                        switch_ports.append(link.target)
                        if link.target.switch.id not in switches_ports:
                            switches_ports[link.target.switch.id] = []
                        switches_ports[link.target.switch.id].append({'name': link.target.name,
                                                                      'port': link.target.port})
        else:
            if switch_port_ids:
                switches_ports = {}
                sp_ids = switch_port_ids.split(',')
                for sp_id in sp_ids:
                    try:
                        switch_port = SwitchPort.objects.get(id=int(sp_id))
                    except:
                        pass
                    else:
                        switch_ports.append(switch_port)
                        if switch_port.switch not in switch_objs:
                            switch_objs.append(switch_port.switch)
                            switches_ports[switch_port.switch.id] = []
                        switches_ports[switch_port.switch.id].append({'name': switch_port.name,
                                                                      'port': switch_port.port})
#     交换机
        for switch_obj in switch_objs:
            if switch_obj.id not in switches_ports:
                switches_ports[switch_obj.id] = []
            switch = {'dpid': switch_obj.dpid,
                      'name': switch_obj.name,
                      'type': switch_obj.type(),
                      'id': switch_obj.id,
                      'ports': switches_ports[switch_obj.id]}
            switches.append(switch)
#     链接
        link_objs = Link.objects.filter(
            source__in=switch_ports, target__in=switch_ports)
        for link_obj in link_objs:
            link = {'src_switch': link_obj.source.switch.dpid,
                    'src_port_name': link_obj.source.name,
                    'src_port': link_obj.source.port,
                    'dst_switch': link_obj.target.switch.dpid,
                    'dst_port': link_obj.target.port,
                    'dst_port_name': link_obj.target.name}
            links.append(link)
        topology = {'switches': switches, 'links': links,
                    'normals': [], 'specials': [],
                    'bandwidth': [], 'maclist': []}
    except Exception, ex:
        print 1
        #import traceback
#         traceback.print_stack()
#         traceback.print_exc()
        return []
    else:
        print 2
#         print topology
        return topology


def get_edge_ports(slice_obj):
    """获取边缘端口
    result:[{'id':交换机id,
        'dpid':交换机dpid,
        'name':交换机的name,
        'ports':[{'id':port的id,'name':port的name,'port':port号, 'can_monopolize':1表示可独占、0表示否},...]},...]
    """
    print 'get_edge_ports'
    switches_edge_ports = []
    try:
        Slice.objects.get(id=slice_obj.id)
    except Exception, ex:
        raise DbError(ex)
    try:
        normal_switches = slice_obj.get_normal_switches()
        for normal_switch in normal_switches:
            edge_ports = normal_switch.get_edge_ports()
            ports = []
            for edge_port in edge_ports:
                if not slice_obj.port_added(edge_port):
                    if not edge_port.monopolized():
                        if edge_port.can_monopolize():
                            can_monopolize = 1
                        else:
                            can_monopolize = 0
                        port = {'id': edge_port.id, 'name': edge_port.name,
                                'port': edge_port.port, 'can_monopolize': can_monopolize}
                        ports.append(port)
            switch_edge_ports = {'id': normal_switch.id, 'dpid': normal_switch.dpid,
                                 'name': normal_switch.name, 'ports': ports}
            switches_edge_ports.append(switch_edge_ports)
#         print switches_edge_ports
        return switches_edge_ports
    except Exception:
        raise DbError("边缘端口获取失败！")


def slice_add_port(slice_obj, port_id, add_type):
    """slice添加外接设备接入的交换端口。
    """
    LOG.debug('slice_add_port')
    try:
        Slice.objects.get(id=slice_obj.id)
        port = SwitchPort.objects.get(id=int(port_id))
        if slice_obj.switch_added(port.switch):
            slice_ports = slice_obj.sliceport_set.filter(switch_port=port)
            if slice_ports:
                slice_port = slice_ports[0]
                if slice_port.type != int(add_type):
                    if slice_port.type == 1:
                        slice_port.ownerdevice_set.all().delete()
                    slice_port.type = int(add_type)
                    slice_port.save()
            else:
                if int(add_type) == 0:
                    if not port.can_monopolize():
                        raise DbError("端口已被占用！")
                slice_port = SlicePort.objects.create(
                    switch_port=port, slice=slice_obj, type=int(add_type))
            slice_obj.flowspace_changed(2)
            return slice_port
        else:
            raise DbError("端口添加失败！")
    except DbError:
        raise
    except Exception:
#         traceback.print_exc()
        raise DbError("端口添加失败！")



def check_macs(slice_port, mac_list):
    mix_macs = []
    base_macs = []
    slice_ports = slice_port.switch_port.sliceport_set.all()
    for slice_port_obj in slice_ports:
        if slice_port_obj.type == 1 and slice_port_obj.slice != slice_port.slice:
            owner_devices = OwnerDevice.objects.filter(slice_port=slice_port_obj)
            if slice_port_obj.slice.get_nw() == None:
                for owner_device in owner_devices:
                    macs = owner_device.mac_list.split(',')
                    for mac in macs:
                        if mac not in base_macs:
                            base_macs.append(mac)
            else:
                for owner_device in owner_devices:
                    macs = owner_device.mac_list.split(',')
                    for mac in macs:
                        if mac not in base_macs:
                            mix_macs.append(mac)
    error_macs = []
    cur_macs = mac_list.split(',')
    if slice_port.slice.get_nw() == None:
        for cur_mac in cur_macs:
            if cur_mac in base_macs:
                error_macs.append(cur_mac)
            else:
                if cur_mac in mix_macs:
                    error_macs.append(cur_mac)
    else:
        for cur_mac in cur_macs:
            if cur_mac in base_macs:
                error_macs.append(cur_mac)
    return ','.join(error_macs)


def slice_add_owner_device(slice_port, mac_list):
    """slice添加用户自接入设备。
    mac_list为字符串类型，最长1024，格式为“mac1,mac2,...”
    """
    LOG.debug('slice_add_owner_device')
    try:
        if slice_port and mac_list:
            error_macs = check_macs(slice_port, mac_list)
            if error_macs != "":
                raise DbError(u"mac地址冲突（" + error_macs + u"）！")
            owner_devices = OwnerDevice.objects.filter(slice_port=slice_port)
            if owner_devices:
                owner_device = owner_devices[0]
                if owner_device.mac_list != mac_list:
                    owner_device.mac_list = mac_list
                    owner_device.save()
            else:
                owner_device = OwnerDevice.objects.get_or_create(
                    mac_list=mac_list, slice_port=slice_port)
            return owner_device
        else:
            raise DbError("参数错误！")
    except DbError:
        raise
    except Exception:
#         traceback.print_exc()
        raise DbError("自接入设备添加失败！")


@transaction.commit_manually
def slice_add_port_device(slice_obj, port_id, add_type, mac_list=None):
    """slice添加用户自接入设备。
    mac_list为字符串类型，最长1024，格式为“mac1,mac2,...”
    """
    LOG.debug('slice_add_port_device')
    try:
        slice_port = slice_add_port(slice_obj, port_id, add_type)
        if int(add_type) == 1:
            slice_add_owner_device(slice_port, mac_list)
        transaction.commit()
    except:
        transaction.rollback()
        raise


@transaction.commit_manually
def slice_delete_port_device(slice_obj, port_id):
    """slice删除用户自接入设备端口。
    """
    LOG.debug('slice_delete_port_device')
    try:
        Slice.objects.get(id=slice_obj.id)
        switch_ports = SwitchPort.objects.filter(id=port_id)
        if switch_ports:
            switch_port = switch_ports[0]
            slice_ports = switch_port.sliceport_set.filter(slice=slice_obj)
            for slice_port in slice_ports:
                if slice_port.type == 1:
                    owner_devices = slice_port.ownerdevice_set.all()
                    owner_devices.delete()
                slice_port.delete()
                slice_obj.flowspace_changed(3)
        transaction.commit()
    except:
        transaction.rollback()
        raise
