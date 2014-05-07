# coding:utf-8
from communication.flowvisor_client import  do_updateFlowSpace, FlowvisorClient
from slice.slice_exception import FlowvisorError, DbError
#from communication.cnvp_http_client import CnvpClient
from communication.cnvp_client import CnvpClient

import logging
LOG = logging.getLogger("CENI")


def flowvisor_add_slice(flowvisor, slice_name, controller, user_email):
    """flowvisor上添加slice
    """
    LOG.debug('flowvisor_add_slice')
    try:
        slice_name = "slice" + str(slice_name)
        if flowvisor.type == 1:
            print "cnvp"
            if flowvisor and controller:
                client = CnvpClient(flowvisor.ip, flowvisor.http_port)
                client.add_slice(slice_name, controller.ip, controller.port)
            else:
                raise DbError("数据库异常")
        else:
            if flowvisor and controller and user_email:
                client = FlowvisorClient(flowvisor.ip, flowvisor.http_port, flowvisor.password)
                client.add_slice(slice_name, controller.ip, controller.port, user_email, "cdn%nf")
            else:
                raise DbError("数据库异常")
    except:
        raise


def flowvisor_show_slice(flowvisor, slice_name):
    """获取flowvisor上添加信息
    """
    LOG.debug('flowvisor_show_slice')
    try:
        slice_name = "slice" + str(slice_name)
        if flowvisor:
            if flowvisor.type == 1:
                print "cnvp"
                client = CnvpClient(flowvisor.ip, flowvisor.http_port)
                return client.show_slice(slice_name)
            else:
                client = FlowvisorClient(flowvisor.ip, flowvisor.http_port, flowvisor.password)
                return client.show_slice()
        else:
            raise DbError("数据库异常")
    except:
        raise


def flowvisor_update_sice_controller(flowvisor, slice_name, controller_ip, controller_port):
    """flowvisor上更新slice控制器
    """
    LOG.debug('flowvisor_update_sice_controller')
    try:
        slice_name = "slice" + str(slice_name)
        if flowvisor and slice_name and controller_ip and controller_port:
            if flowvisor.type == 1:
                print "cnvp"
                client = CnvpClient(flowvisor.ip, flowvisor.http_port)
            else:
                client = FlowvisorClient(flowvisor.ip, flowvisor.http_port, flowvisor.password)
            client.change_slice_controller(slice_name, controller_ip, controller_port)
        else:
            raise DbError("数据库异常!")
    except:
        raise


def flowvisor_update_slice_status(flowvisor, slice_name, status):
    """flowvisor上更新slice启停状态
    """
    LOG.debug('flowvisor_update_slice_status')
    try:
        slice_name = "slice" + str(slice_name)
        if flowvisor and slice_name:
            if flowvisor.type == 1:
                print "cnvp"
                client = CnvpClient(flowvisor.ip, flowvisor.http_port)
                if status:
                    client.start_slice(slice_name)
                else:
                    client.stop_slice(slice_name)
            else:
                client = FlowvisorClient(flowvisor.ip, flowvisor.http_port, flowvisor.password)
                client.start_or_stop_slice(slice_name, status)
        else:
            raise DbError("数据库异常！")
    except:
        raise


def flowvisor_del_slice(flowvisor, slice_name):
    """flowvisor上删除slice
    """
    print 'flowvisor_del_slice'
    try:
        if flowvisor and slice_name:
            slice_name = "slice" + str(slice_name)
            if flowvisor.type == 1:
                print "cnvp"
                client = CnvpClient(flowvisor.ip, flowvisor.http_port)
            else:
                client = FlowvisorClient(flowvisor.ip, flowvisor.http_port, flowvisor.password)
            client.delete_slice(slice_name)
        else:
            raise DbError("数据库异常！")
    except:
        raise


def flowvisor_add_port(flowvisor, slice_name, dpid, port):
    """cnvp上添加port
    """
    LOG.debug('flowvisor_add_port')
    try:
        if flowvisor:
            slice_name = "slice" + str(slice_name)
            if flowvisor.type == 1:
                print "cnvp"
                client = CnvpClient(flowvisor.ip, flowvisor.http_port)
                client.add_port(slice_name, dpid, port)
        else:
            raise DbError("数据库异常")
    except:
        raise


def flowvisor_del_port(flowvisor, slice_name, dpid, port):
    """cnvp上删除port
    """
    LOG.debug('flowvisor_del_port')
    slice_name = "slice" + str(slice_name)
    if flowvisor.type == 1:
        print "cnvp"
        if flowvisor:
            client = CnvpClient(flowvisor.ip, flowvisor.http_port)
            try:
                client.delete_port(slice_name, dpid, port)
            except:
                raise
        else:
            raise DbError("数据库异常")


def flowvisor_add_flowspace(flowvisor, name, slice_name, slice_action,
                            pwd, dpid, priority, arg_match):
    """flowvisor上添加flowspace
    """
    LOG.debug('flowvisor_add_flowspace')
    try:
        if flowvisor:
            slice_name = "slice" + str(slice_name)
            if flowvisor.type == 1:
                print "cnvp"
                client = CnvpClient(flowvisor.ip, flowvisor.http_port)
                client.add_flowspace(slice_name, slice_action,
                    dpid, priority, arg_match)
            else:
                client = FlowvisorClient(flowvisor.ip, flowvisor.http_port, flowvisor.password)
                client.add_flowspace(slice_name, slice_action, pwd, name,
                    dpid, priority, arg_match)
        else:
            raise DbError("数据库异常")
    except:
        raise


def flowvisor_update_flowspace(flowvisor, flowspace_name, priority_flag,
                               arg_match_flag, priority, arg_match):
    """flowvisor上更新flowspace
    """
    LOG.debug('flowvisor_update_flowspace')
    opts = {}
    if flowvisor:
        if priority_flag == 1:
            opts['prio'] = priority
        if arg_match_flag == 1:
            opts['match'] = arg_match
        flowvisor_url = "https://" + str(flowvisor.ip) + ":" + str(flowvisor.http_port) + ""
        flowvisor_ps = str(flowvisor.password)
        args = [flowspace_name]
        upflowspace = do_updateFlowSpace(args, opts, flowvisor_url, flowvisor_ps)
        if upflowspace == 'error':
            raise FlowvisorError("flowvisor上更新flowspace失败！")
    else:
        raise DbError("数据库异常")


def flowvisor_del_flowspace(flowvisor, slice_name, flowspace_name):
    """flowvisor上删除flowspace
    """
    LOG.debug('flowvisor_del_flowspace')
    try:
        if flowvisor:
            slice_name = "slice" + str(slice_name)
            if flowvisor.type == 1:
                print "cnvp"
                client = CnvpClient(flowvisor.ip, flowvisor.http_port)
                client.delete_flowspace(slice_name, None)
            else:
                client = FlowvisorClient(flowvisor.ip, flowvisor.http_port, flowvisor.password)
                client.delete_flowspace(flowspace_name)
        else:
            raise DbError("数据库异常")
    except:
        raise


def flowvisor_get_switches(flowvisor):
    """flowvisor上获取交换机信息
    """
    LOG.debug('flowvisor_get_switches')
    if flowvisor:
        if flowvisor.type == 1:
            print "cnvp"
            client = CnvpClient(flowvisor.ip, flowvisor.http_port)
        else:
            client = FlowvisorClient(flowvisor.ip, flowvisor.http_port, flowvisor.password)
        try:
            return client.get_switches()
        except:
            raise
    else:
        raise DbError("数据库异常")


def flowvisor_get_links(flowvisor):
    """flowvisor上获取交换机链接信息
    """
    LOG.debug('flowvisor_get_links')
    if flowvisor:
        if flowvisor.type == 1:
            print "cnvp"
            client = CnvpClient(flowvisor.ip, flowvisor.http_port)
        else:
            client = FlowvisorClient(flowvisor.ip, flowvisor.http_port, flowvisor.password)
        try:
            return client.get_links()
        except:
            raise
    else:
        raise DbError("数据库异常")
