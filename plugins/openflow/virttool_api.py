# coding:utf-8
from communication.flowvisor_client import  do_updateFlowSpace, FlowvisorClient
from slice.slice_exception import VirttoolError, DbError
from communication.cnvp_http_client import CnvpClient
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
        print virttool, slice_name
        if virttool and slice_name:
            slice_name = "slice" + str(slice_name)
            if virttool.type == 1:
                print "cnvp"
                client = CnvpClient(virttool.ip, virttool.http_port)
            else:
                client = FlowvisorClient(virttool.ip, virttool.http_port, virttool.password)
            client.delete_slice(slice_name)
        else:
            raise DbError("数据库异常！")
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
