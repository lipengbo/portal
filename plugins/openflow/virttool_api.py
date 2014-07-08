# coding:utf-8
import hashlib
import json
from communication.flowvisor_client import  do_updateFlowSpace, FlowvisorClient
from slice.slice_exception import VirttoolError, DbError
from communication.cnvp_http_client import CnvpClient
from etc.config import virttool_disable
#from communication.cnvp_client import CnvpClient

import logging
LOG = logging.getLogger("CENI")


def virttool_add_slice(virttool, slice_name, controller, user_email):
    """virttool上添加slice
    """
    LOG.debug('virttool_add_slice')
    try:
        slice_name = "slice" + str(slice_name)
        if virttool.type == 1:
            print "cnvp"
            if virttool and controller:
                client = CnvpClient(virttool.ip, virttool.http_port)
                client.add_slice(slice_name, controller.ip, controller.port)
            else:
                raise DbError("数据库异常")
        else:
            if virttool and controller and user_email:
                client = FlowvisorClient(virttool.ip, virttool.http_port, virttool.password)
                client.add_slice(slice_name, controller.ip, controller.port, user_email, "cdn%nf")
            else:
                raise DbError("数据库异常")
    except:
        raise


def virttool_show_slice(virttool, slice_name):
    """获取virttool上添加信息
    """
    LOG.debug('virttool_show_slice')
    try:
        slice_name = "slice" + str(slice_name)
        if virttool:
            if virttool.type == 1:
                print "cnvp"
                client = CnvpClient(virttool.ip, virttool.http_port)
                return client.show_slice(slice_name)
            else:
                client = FlowvisorClient(virttool.ip, virttool.http_port, virttool.password)
                return client.show_slice()
        else:
            raise DbError("数据库异常")
    except:
        raise


def virttool_update_sice_controller(virttool, slice_name, controller_ip, controller_port):
    """virttool上更新slice控制器
    """
    LOG.debug('virttool_update_sice_controller')
    try:
        slice_name = "slice" + str(slice_name)
        if virttool and slice_name and controller_ip and controller_port:
            if virttool.type == 1:
                print "cnvp"
                client = CnvpClient(virttool.ip, virttool.http_port)
            else:
                client = FlowvisorClient(virttool.ip, virttool.http_port, virttool.password)
            client.change_slice_controller(slice_name, controller_ip, controller_port)
        else:
            raise DbError("数据库异常!")
    except:
        raise


def virttool_update_slice_status(virttool, slice_name, status):
    """virttool上更新slice启停状态
    """
    LOG.debug('virttool_update_slice_status')
    try:
        slice_name = "slice" + str(slice_name)
        if virttool and slice_name:
            if virttool.type == 1:
                print "cnvp"
                client = CnvpClient(virttool.ip, virttool.http_port)
                if status:
                    client.start_slice(slice_name)
                else:
                    client.stop_slice(slice_name)
            else:
                client = FlowvisorClient(virttool.ip, virttool.http_port, virttool.password)
                client.start_or_stop_slice(slice_name, status)
        else:
            raise DbError("数据库异常！")
    except:
        raise


def virttool_del_slice(virttool, slice_name):
    """virttool上删除slice
    """
    print 'virttool_del_slice'
    try:
        if virttool and slice_name:
            slice_name = "slice" + str(slice_name)
            if virttool.type == 1:
                print "cnvp"
                client = CnvpClient(virttool.ip, virttool.http_port)
            else:
                client = FlowvisorClient(virttool.ip, virttool.http_port, virttool.password)
            client.delete_slice(slice_name)
        else:
            pass
    except:
        raise


def virttool_add_port(virttool, slice_name, dpid, port):
    """cnvp上添加port
    """
    LOG.debug('virttool_add_port')
    try:
        if virttool:
            slice_name = "slice" + str(slice_name)
            if virttool.type == 1:
                print "cnvp"
                client = CnvpClient(virttool.ip, virttool.http_port)
                client.add_port(slice_name, dpid, port)
        else:
            raise DbError("数据库异常")
    except:
        raise


def virttool_del_port(virttool, slice_name, dpid, port):
    """cnvp上删除port
    """
    LOG.debug('virttool_del_port')
    slice_name = "slice" + str(slice_name)
    if virttool.type == 1:
        print "cnvp"
        if virttool:
            client = CnvpClient(virttool.ip, virttool.http_port)
            try:
                client.delete_port(slice_name, dpid, port)
            except:
                raise
        else:
            raise DbError("数据库异常")


def virttool_add_flowspace(virttool, name, slice_name, slice_action,
                            pwd, dpid, priority, arg_match):
    """virttool上添加flowspace
    """
    LOG.debug('virttool_add_flowspace')
    try:
        if virttool:
            slice_name = "slice" + str(slice_name)
            if virttool.type == 1:
                print "cnvp"
                client = CnvpClient(virttool.ip, virttool.http_port)
                client.add_flowspace(slice_name, slice_action,
                    dpid, priority, arg_match)
            else:
                client = FlowvisorClient(virttool.ip, virttool.http_port, virttool.password)
                client.add_flowspace(slice_name, slice_action, pwd, name,
                    dpid, priority, arg_match)
        else:
            raise DbError("数据库异常")
    except:
        raise


def virttool_update_flowspace(virttool, flowspace_name, priority_flag,
                               arg_match_flag, priority, arg_match):
    """virttool上更新flowspace
    """
    LOG.debug('virttool_update_flowspace')
    opts = {}
    if virttool:
        if priority_flag == 1:
            opts['prio'] = priority
        if arg_match_flag == 1:
            opts['match'] = arg_match
        virttool_url = "https://" + str(virttool.ip) + ":" + str(virttool.http_port) + ""
        virttool_ps = str(virttool.password)
        args = [flowspace_name]
        upflowspace = do_updateFlowSpace(args, opts, virttool_url, virttool_ps)
        if upflowspace == 'error':
            raise VirttoolError("flowspace更新失败！")
    else:
        raise DbError("数据库异常")


def virttool_del_flowspace(virttool, slice_name, flowspace_name):
    """virttool上删除flowspace
    """
    LOG.debug('virttool_del_flowspace')
    try:
        if virttool:
            slice_name = "slice" + str(slice_name)
            if virttool.type == 1:
                print "cnvp"
                client = CnvpClient(virttool.ip, virttool.http_port)
                client.delete_flowspace(slice_name, None)
            else:
                client = FlowvisorClient(virttool.ip, virttool.http_port, virttool.password)
                client.delete_flowspace(flowspace_name)
        else:
            raise DbError("数据库异常")
    except:
        raise


def virttool_get_switches(virttool):
    """virttool上获取交换机信息
    """
    LOG.debug('virttool_get_switches')
    switches = [{'dpid':'00:00:00:00:00:00:00:06', 'ports':[{'portNumber':2,'name':'ovs128-2'},{'portNumber':1,'name':'ovs128-1'}], 'target_switch':()},
                {'dpid':'00:00:00:00:00:00:00:05', 'ports':[{'portNumber':2,'name':'ovs127-2'},{'portNumber':1,'name':'ovs127-1'}], 'target_switch':()},
                {'dpid':'00:00:00:00:00:00:00:04', 'ports':[{'portNumber':2,'name':'ovs126-2'},{'portNumber':1,'name':'ovs126-1'}], 'target_switch':()},
                {'dpid':'00:00:00:00:00:00:00:03', 'ports':[{'portNumber':2,'name':'ovs125-2'},{'portNumber':1,'name':'ovs125-1'}], 'target_switch':()},
                {'dpid':'00:ee:00:00:00:00:00:01', 'ports':[{'portNumber':90,'name':'p90'}], 'target_switch':()},
                {'dpid':'00:ff:00:00:00:00:00:02', 'ports':[{'portNumber':99,'name':'p99'}], 'target_switch':()},
                {'dpid':'00:ff:00:00:00:00:00:01', 'ports':[{'portNumber':655,'name':'p655'},{'portNumber':1,'name':'eth1'}], 'target_switch':()},
                {'dpid':'00:00:00:00:00:00:00:02', 'ports':[{'portNumber':14,'name':'et14'},{'portNumber':13,'name':'et13'},
                                                            {'portNumber':12,'name':'et12'},{'portNumber':11,'name':'et11'},
                                                            {'portNumber':10,'name':'et10'},{'portNumber':2,'name':'eth2'},
                                                            {'portNumber':1,'name':'eth1'}], 'target_switch':()}]
#     switches = [{'dpid':'00:00:a0:36:9f:02:e4:18', 'ports':[], 'target_switch':()},
#                 {'dpid':'00:00:00:00:00:00:00:06', 'ports':[{'portNumber':2,'name':'ovs128-2'},{'portNumber':1,'name':'ovs128-1'}], 'target_switch':()},
#                 {'dpid':'00:00:00:00:00:00:00:05', 'ports':[{'portNumber':2,'name':'ovs127-2'},{'portNumber':1,'name':'ovs127-1'}], 'target_switch':()},
#                 {'dpid':'00:00:00:00:00:00:00:04', 'ports':[{'portNumber':2,'name':'ovs126-2'},{'portNumber':1,'name':'ovs126-1'}], 'target_switch':()},
#                 {'dpid':'00:00:00:00:00:00:00:03', 'ports':[{'portNumber':2,'name':'ovs125-2'},{'portNumber':1,'name':'ovs125-1'}], 'target_switch':()},
#                 {'dpid':'00:ee:00:00:00:00:00:01', 'ports':[{'portNumber':90,'name':'p90'}], 'target_switch':()},
#                 {'dpid':'00:ff:00:00:00:00:00:02', 'ports':[{'portNumber':99,'name':'p99'}], 'target_switch':()},
#                 {'dpid':'00:ff:00:00:00:00:00:01', 'ports':[{'portNumber':655,'name':'p655'},{'portNumber':1,'name':'eth1'}], 'target_switch':()},
#                 {'dpid':'00:00:00:00:00:00:00:02', 'ports':[{'portNumber':14,'name':'et14'},{'portNumber':13,'name':'et13'},
#                                                             {'portNumber':12,'name':'et12'},{'portNumber':11,'name':'et11'},
#                                                             {'portNumber':10,'name':'et10'},{'portNumber':2,'name':'eth2'},
#                                                             {'portNumber':1,'name':'eth1'}], 'target_switch':()}]
    return switches
    if virttool:
        if virttool.type == 1:
            print "cnvp"
            client = CnvpClient(virttool.ip, virttool.http_port)
        else:
            client = FlowvisorClient(virttool.ip, virttool.http_port, virttool.password)
        try:
            return client.get_switches()
        except:
            raise
    else:
        raise DbError("数据库异常")


def virttool_get_links(virttool):
    """virttool上获取交换机链接信息
    """
    LOG.debug('virttool_get_links')
    links = [{'dst-port':1, 'dst-switch':'00:00:00:00:00:00:00:06', 'src-port':2, 'src-switch':'00:00:00:00:00:00:00:05'},
             {'dst-port':1, 'dst-switch':'00:00:00:00:00:00:00:05', 'src-port':2, 'src-switch':'00:00:00:00:00:00:00:04'},
             {'dst-port':1, 'dst-switch':'00:00:00:00:00:00:00:04', 'src-port':2, 'src-switch':'00:00:00:00:00:00:00:03'},
             {'dst-port':1, 'dst-switch':'00:ff:00:00:00:00:00:01', 'src-port':1, 'src-switch':'00:00:00:00:00:00:00:02'}]
#     links = [{'dst-port':1, 'dst-switch':'00:00:00:00:00:00:00:06', 'src-port':2, 'src-switch':'00:00:00:00:00:00:00:05'},
#              {'dst-port':1, 'dst-switch':'00:00:00:00:00:00:00:05', 'src-port':2, 'src-switch':'00:00:00:00:00:00:00:04'},
#              {'dst-port':1, 'dst-switch':'00:00:00:00:00:00:00:04', 'src-port':2, 'src-switch':'00:00:00:00:00:00:00:03'},
#              {'dst-port':1, 'dst-switch':'00:ff:00:00:00:00:00:01', 'src-port':1, 'src-switch':'00:00:00:00:00:00:00:02'}]
    return links
    if virttool:
        if virttool.type == 1:
            print "cnvp"
            client = CnvpClient(virttool.ip, virttool.http_port)
        else:
            client = FlowvisorClient(virttool.ip, virttool.http_port, virttool.password)
        try:
            return client.get_links()
        except:
            raise
    else:
        raise DbError("数据库异常")


def update_physic_topology(instance):
    from resources.models import Switch, SwitchPort
    from plugins.openflow.models import Link, VirttoolLinksMd5
    try:
        if virttool_disable:
            return
        port_name_dict = {}
        island_obj = instance.island
        try:
            switches = virttool_get_switches(instance)
        except:
            return
        for switch in switches:
            dpid = switch['dpid']
            port_name_dict[dpid] = {}
            for port in switch['ports']:
                port_name_dict[dpid][port['portNumber']] = port['name']
            switch_dbs = Switch.objects.filter(island=island_obj, dpid=dpid)
            if switch_dbs:
                switch_dbs[0].update_state(1)
        dpids = port_name_dict.keys()
        print dpids
        switch_dbs = Switch.objects.filter(island=island_obj, state=1)
        for switch_db in switch_dbs:
            if switch_db.dpid not in dpids:
                switch_db.update_state(0)
        try:
            links = virttool_get_links(instance)
        except:
            return
        digest = hashlib.md5(json.dumps(links)).hexdigest()
        try:
            md5_obj = instance.virttoollinksmd5
        except VirttoolLinksMd5.DoesNotExist:
            #: if it's the first time update, create a md5 record
            VirttoolLinksMd5(md5=digest, virttool=instance).save()
        else:
            if md5_obj.md5 != digest: #: update the md5 digest and do the updates and deletions
                md5_obj.md5 = digest
                md5_obj.save()
            else:
                return
        #: delete all existing links and ports
        instance.link_set.all().delete()
        for link in links:
            src_port = link['src-port']
            dst_port = link['dst-port']
            if (link['src-switch'] not in dpids) or (link['dst-switch'] not in dpids):
                continue
            try:
                source_switch = Switch.objects.get(dpid=link['src-switch'], island=island_obj)
                target_switch = Switch.objects.get(dpid=link['dst-switch'], island=island_obj)
            except Switch.DoesNotExist:
                continue
            try:
                src_port_name = port_name_dict[source_switch.dpid][int(src_port)]
            except KeyError:
                src_port_name = 'eth' + str(src_port)
            try:
                dst_port_name = port_name_dict[target_switch.dpid][int(dst_port)]
            except KeyError:
                dst_port_name = 'eth' + str(dst_port)
            source_port, created = SwitchPort.objects.get_or_create(
                    switch=source_switch,
                    port=src_port,
                    defaults={'name': src_port_name})
            source_port.name = src_port_name
            source_port.save()

            target_port, created = SwitchPort.objects.get_or_create(
                    switch=target_switch,
                    port=dst_port,
                    defaults={'name': dst_port_name})
            target_port.name = dst_port_name
            target_port.save()

            link_obj = Link(virttool=instance,
                    source=source_port,
                    target=target_port)
            link_obj.save()
    except:
        import traceback
        traceback.print_exc()
        raise
