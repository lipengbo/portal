# coding:utf-8
from slice.models import Slice
from resources.models import Switch, VirtualSwitch, OVS_TYPE, SwitchPort
from slice.slice_exception import DbError
from plugins.openflow.flowspace_api import flowspace_gw_add, flowspace_gw_del
from django.db import transaction
from plugins.openflow.models import Link
import logging
LOG = logging.getLogger("CENI")
OVS_TYPE = {'NOMAL': 1, 'EXTERNAL': 2, 'RELATED': 3}


def slice_add_ovs_ports(slice_obj, ovs_ports):
    """slice添加交换端口
    """
    LOG.debug('slice_add_ovs_ports')
    try:
        Slice.objects.get(id=slice_obj.id)
        for ovs_port in ovs_ports:
            slice_obj.add_resource(ovs_port)
            if ovs_port.switch.type() == OVS_TYPE['EXTERNAL']:
                try:
                    ovs_port.switch.virtualswitch
                except VirtualSwitch.DoesNotExist:
                    pass
                else:
                    flowspace_gw_add(slice_obj, ovs_port.switch.virtualswitch.server.mac)
    except Exception, ex:
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


def get_select_topology(switch_port_ids):
    """获取选择的交换机端口拓扑信息
    """
    print 'get_select_topology'
#     交换机
    try:
        switches = []
        links = []
        if switch_port_ids:
            switch_ids = []
            switch_objs = []
            dpids = []
            switch_ports = []
            switches_ports = {}
            sp_ids = switch_port_ids.split(',')
            for sp_id in sp_ids:
                try:
                    switch_port = SwitchPort.objects.get(id=int(sp_id))
                except:
                    pass
                else:
                    switch_ports.append(switch_port)
                    if switch_port.switch.id not in switch_ids:
                        switch_ids.append(switch_port.switch.id)
                        switch_objs.append(switch_port.switch)
                        dpids.append(switch_port.switch.dpid)
                        switches_ports[switch_port.switch.id] = []
                    switches_ports[switch_port.switch.id].append({'name': switch_port.name,
                                                                  'port': switch_port.port})
            for switch_obj in switch_objs:
                switch = {'dpid': switch_obj.dpid,
                          'name': switch_obj.name,
                          'type': switch_obj.type(),
                          'id': switch_obj.id,
                          'ports': switches_ports[switch_obj.id]}
                switches.append(switch)
#     链接
            switch_ids = []
            link_objs = Link.objects.filter(
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
#                     if link_obj.source.switch.id in switch_ids:
#                         if link_obj.source.port not in ports[link_obj.source.switch.id]:
#                             ports[link_obj.source.switch.id].append(link_obj.source.port)
#                     else:
#                         switch_ids.append(link_obj.source.switch.id)
#                         ports[link_obj.source.switch.id] = [link_obj.source.port]
#                     if link_obj.target.switch.id in switch_ids:
#                         if link_obj.target.port not in ports[link_obj.target.switch.id]:
#                             ports[link_obj.target.switch.id].append(link_obj.target.port)
#                     else:
#                         switch_ids.append(link_obj.target.switch.id)
#                         ports[link_obj.target.switch.id] = [link_obj.target.port]
#             for switch_id in switch_ids:
#                 try:
#                     switch = Switch.objects.get(id=switch_id)
#                 except:
#                     pass
#                 else:
#                     for port in ports[switch_id]:
#                         bandwidth.append({'id': (str(switch_id) + '_' + str(port)),
#                                     'cur_bd': 0, 'total_bd': 0})

        topology = {'switches': switches, 'links': links,
                    'normals': [], 'specials': [],
                    'bandwidth': [], 'maclist': []}
    except Exception, ex:
        print 1
        print ex
        return []
    else:
        print 2
        return topology
