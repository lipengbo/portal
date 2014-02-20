# coding:utf-8
from communication.flowvisor_client import do_addSlice, do_updateSlice,\
    do_removeSlice, do_addFlowSpace, do_updateFlowSpace, do_removeFlowSpace,\
    do_listSlices, FlowvisorClient
from slice.slice_exception import FlowvisorError, DbError
from etc.config import flowvisor_or_cnvp
from communication.cnvp_client import CnvpClient

import logging
LOG = logging.getLogger("CENI")


def flowvisor_add_slice(flowvisor, slice_name, controller, user_email):
    """flowvisor上添加slice
    """
    LOG.debug('flowvisor_add_slice')
    slice_name = "slice" + str(slice_name)
    if flowvisor_or_cnvp == "cnvp":
        print "cnvp"
        if flowvisor and controller:
            client = CnvpClient(flowvisor.ip, flowvisor.http_port)
            try:
                client.add_slice(slice_name, controller.ip, controller.port)
            except:
                raise
        else:
            raise DbError("数据库异常")
    else:
        if flowvisor and controller and user_email:
            controllerAdd = 'tcp:' + str(controller.ip) + ':' + str(controller.port) + ''
            args = [str(slice_name), controllerAdd, user_email]
            pwd = "cdn%nf"
            flowvisor_url = "https://" + str(flowvisor.ip) + ":" + str(flowvisor.http_port) + ""
            flowvisor_ps = str(flowvisor.password)
            adslice = do_addSlice(args, pwd, False, flowvisor_url, flowvisor_ps)
            if adslice == 'error':
                raise FlowvisorError("虚网创建失败!")
        else:
            raise DbError("数据库异常")


def flowvisor_show_slice(flowvisor, slice_name):
    """获取flowvisor上添加信息
    """
    LOG.debug('flowvisor_show_slice')
    slice_name = "slice" + str(slice_name)
    if flowvisor_or_cnvp == "cnvp":
        print "cnvp"
        if flowvisor:
            print 1
            client = CnvpClient(flowvisor.ip, flowvisor.http_port)
            print 2
            try:
                return client.show_slice(slice_name)
            except:
                raise
        else:
            raise DbError("数据库异常")
    else:
        if flowvisor:
            flowvisor_url = "https://" + str(flowvisor.ip) + ":" + str(flowvisor.http_port) + ""
            flowvisor_ps = str(flowvisor.password)
            lislice = do_listSlices(flowvisor_url, flowvisor_ps)
            if lislice == 'error':
                raise FlowvisorError("获取虚网信息失败!")
        else:
            raise DbError("数据库异常")


def flowvisor_update_sice_controller(flowvisor, slice_name, controller_ip, controller_port):
    """flowvisor上更新slice控制器
    """
    LOG.debug('flowvisor_update_sice_controller')
    slice_name = "slice" + str(slice_name)
    if flowvisor_or_cnvp == "cnvp":
        print "cnvp"
        if flowvisor and slice_name and controller_ip and controller_port:
            client = CnvpClient(flowvisor.ip, flowvisor.http_port)
            try:
                client.change_slice_controller(slice_name, controller_ip, controller_port)
            except:
                raise
        else:
            raise DbError("数据库异常")
    else:
        if flowvisor and slice_name and controller_ip and controller_port:
            args = [str(slice_name)]
            opts = {'chost': str(controller_ip), 'cport': int(controller_port)}
            print opts
            flowvisor_url = "https://" + str(flowvisor.ip) + ":" + str(flowvisor.http_port) + ""
            flowvisor_ps = str(flowvisor.password)
            upslice = do_updateSlice(args, opts, flowvisor_url, flowvisor_ps)
            if upslice == 'error':
                raise FlowvisorError("控制器更新失败!")
        else:
            raise DbError("数据库异常!")


def flowvisor_update_slice_status(flowvisor, slice_name, status):
    """flowvisor上更新slice启停状态
    """
    LOG.debug('flowvisor_update_slice_status')
    slice_name = "slice" + str(slice_name)
    if flowvisor_or_cnvp == "cnvp":
        print "cnvp"
        if flowvisor and slice_name:
            client = CnvpClient(flowvisor.ip, flowvisor.http_port)
            try:
                if status:
                    client.start_slice(slice_name)
                else:
                    client.stop_slice(slice_name)
            except:
                raise
        else:
            raise DbError("数据库异常")
    else:
        if flowvisor and slice_name:
            args = [str(slice_name)]
            opts = {'status': status}
            flowvisor_url = "https://" + str(flowvisor.ip) + ":" + str(flowvisor.http_port) + ""
            flowvisor_ps = str(flowvisor.password)
            upslice = do_updateSlice(args, opts, flowvisor_url, flowvisor_ps)
            if upslice == 'error':
                raise FlowvisorError("虚网状态更新失败!")
        else:
            raise DbError("数据库异常！")


def flowvisor_del_slice(flowvisor, slice_name):
    """flowvisor上删除slice
    """
    print 'flowvisor_del_slice'
    slice_name = "slice" + str(slice_name)
    if flowvisor_or_cnvp == "cnvp":
        print "cnvp"
        if flowvisor and slice_name:
            client = CnvpClient(flowvisor.ip, flowvisor.http_port)
            try:
                client.delete_slice(slice_name)
            except:
                raise
        else:
            pass
    else:
        if flowvisor and slice_name:
    #         print "in delete"
            args = [str(slice_name)]
            flowvisor_url = "https://" + str(flowvisor.ip) + ":" + str(flowvisor.http_port) + ""
            flowvisor_ps = str(flowvisor.password)
            rm_slice = do_removeSlice(args, flowvisor_url, flowvisor_ps)
            if rm_slice == 'error':
                raise FlowvisorError("虚网删除失败!")
        else:
            pass
#         raise DbError("数据库异常!")


def flowvisor_add_port(flowvisor, slice_name, dpid, port):
    """cnvp上添加port
    """
    LOG.debug('flowvisor_add_port')
    slice_name = "slice" + str(slice_name)
    if flowvisor_or_cnvp == "cnvp":
        print "cnvp"
        if flowvisor:
            client = CnvpClient(flowvisor.ip, flowvisor.http_port)
            try:
                client.add_port(slice_name, dpid, port)
            except:
                raise
        else:
            raise DbError("数据库异常")


def flowvisor_del_port(flowvisor, slice_name, dpid, port):
    """cnvp上删除port
    """
    LOG.debug('flowvisor_del_port')
    slice_name = "slice" + str(slice_name)
    if flowvisor_or_cnvp == "cnvp":
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
    slice_name = "slice" + str(slice_name)
    if flowvisor_or_cnvp == "cnvp":
        print "cnvp"
        if flowvisor:
            client = CnvpClient(flowvisor.ip, flowvisor.http_port)
            try:
                client.add_flowspace(slice_name, slice_action,
                    dpid, priority, arg_match)
            except:
                raise
        else:
            raise DbError("数据库异常")
    else:
        if flowvisor:
            fsaction = '' + str(slice_name) + '=' + str(slice_action) + ''
            pwd = str(pwd)
            flowvisor_url = "https://" + str(flowvisor.ip) + ":" + str(flowvisor.http_port) + ""
            flowvisor_ps = str(flowvisor.password)
            dpid = str(dpid)
            name = str(name)
            priority = str(priority)
            arg_match = str(arg_match)
            args = [name, dpid, priority, arg_match, fsaction]
            adflowspace = do_addFlowSpace(args, pwd, flowvisor_url, flowvisor_ps)
            if adflowspace == 'error':
                raise FlowvisorError("flowvisor上添加flowspace失败！")
        else:
            raise DbError("数据库异常")


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
    slice_name = "slice" + str(slice_name)
    if flowvisor_or_cnvp == "cnvp":
        print "cnvp"
        if flowvisor:
            client = CnvpClient(flowvisor.ip, flowvisor.http_port)
            try:
                client.delete_flowspace(slice_name, None)
            except:
                raise
        else:
            raise DbError("数据库异常")
    else:
        if flowvisor:
            args = [flowspace_name]
            flowvisor_url = "https://" + str(flowvisor.ip) + ":" + str(flowvisor.http_port) + ""
            flowvisor_ps = str(flowvisor.password)
            do_removeFlowSpace(args, flowvisor_url, flowvisor_ps)
        else:
            raise DbError("数据库异常")


def flowvisor_get_switches(flowvisor):
    """flowvisor上获取交换机信息
    """
    LOG.debug('flowvisor_get_switches')
    if flowvisor:
        if flowvisor_or_cnvp == "cnvp":
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
        if flowvisor_or_cnvp == "cnvp":
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
