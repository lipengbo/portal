# coding:utf-8
from celery import task
from slice.models import Slice
from plugins.openflow.virttool_api import virttool_del_slice,\
    virttool_update_slice_status, virttool_add_slice,\
    virttool_update_sice_controller
from slice.slice_api import update_slice_virtual_network_cnvp,\
    update_slice_virtual_network_virttool
from plugins.vt.models import DOMAIN_STATE_DIC
from slice.slice_exception import DbError
from adminlog.models import log, SUCCESS, FAIL
from plugins.common.agent_client import AgentClient


@task()
def add(x, y):
    return x + y


@task()
def start_slice_sync(slice_id, controller_flag, gw_flag, user):
    print "start_slice_sync"
    flag = False
    ct_op = True
    gw_op = True
    try:
        slice_obj = Slice.objects.get(id=slice_id)
        print "start controller"
        if controller_flag:
            controller = slice_obj.get_controller()
            if controller.host:
                try:
                    action_result = controller.host.do_action("create")
                except Exception:
                    controller.host.state = DOMAIN_STATE_DIC['shutoff']
                    ct_op = False
                else:
                    if action_result:
                        controller.host.state = DOMAIN_STATE_DIC['running']
                    else:
                        controller.host.state = DOMAIN_STATE_DIC['shutoff']
                        ct_op = False
                controller.host.save()
        print "start gw"
        if gw_flag:
            gw = slice_obj.get_gw()
            if gw and gw.enable_dhcp:
                try:
                    action_result = gw.do_action("create")
                except Exception:
                    gw.state = DOMAIN_STATE_DIC['shutoff']
                    gw_op = False
                else:
                    if action_result:
                        gw.state = DOMAIN_STATE_DIC['running']
                    else:
                        gw.state = DOMAIN_STATE_DIC['shutoff']
                        gw_op = False
                gw.save()
        print "stop slice, update flowspace, start slice"
        if ct_op and gw_op:
            virttool = slice_obj.get_virttool()
            if virttool:
                print "++++++++++++++++++", slice_obj.ct_change
                if slice_obj.ct_change == None:
                    virttool_add_slice(virttool, slice_obj.id,
                        slice_obj.get_controller(), slice_obj.owner.email)
                else:
                    if slice_obj.ct_change:
                        controller = slice_obj.get_controller()
                        virttool_update_sice_controller(virttool, slice_obj.id,
                                                controller.ip, controller.port)
                slice_obj.ct_change = False
                slice_obj.save()
                if virttool.type == 1:
                    print 1
                    virttool_update_slice_status(virttool,
                                                  slice_obj.id, False)
                    print 2
                    update_slice_virtual_network_cnvp(slice_obj)
                    print 3
                    virttool_update_slice_status(virttool,
                                                  slice_obj.id, True)
                    flag = True
                else:
                    virttool_update_slice_status(virttool,
                                                  slice_obj.id, True)
                    flag = True
                    update_slice_virtual_network_virttool(slice_obj)
                slice_obj.start()
            else:
                raise DbError("环境异常!")
        else:
            if not ct_op:
                raise DbError("控制器启动失败!")
            if not gw_op:
                raise DbError("网关启动失败!")
        print "start success"
    except Slice.DoesNotExist:
        pass
    except Exception, ex:
        import traceback
        traceback.print_exc()
        try:
            log(user, slice_obj, u"启动虚网", result_code=FAIL)
            slice_obj.stop()
            if flag:
                virttool_update_slice_status(virttool,
                                              slice_obj.id, False)
            if slice_obj.ct_change == None:
                virttool_del_slice(virttool, slice_obj.id)
        except:
            pass
    else:
        log(user, slice_obj, u"启动虚网", result_code=SUCCESS)


@task()
def stop_slice_sync(slice_id, user):
    print "stop_slice_sync"
    try:
        slice_obj = Slice.objects.get(id=slice_id)
        if slice_obj.state == 3:
            virttool_update_slice_status(slice_obj.get_virttool(),
                                                  slice_obj.id, False)
            slice_obj.stop()
    except Slice.DoesNotExist:
        pass
    except:
        log(user, slice_obj, u"停止虚网", result_code=FAIL)
        slice_obj.start()
    else:
        log(user, slice_obj, u"停止虚网", result_code=SUCCESS)


@task()
def start_or_stop_vpn(user, slice_obj, vpn_ip, network, gw_ip, start_or_stop):
    try:
        print user, "--------->do_action on vpn server", start_or_stop
        agent = AgentClient(vpn_ip)
        if start_or_stop == 'start':
            print "1"
            result = agent.add_route_to_vpnserver(network, gw_ip)
        else:
            print "2"
            result = agent.del_route_from_vpnserver(network, gw_ip)
        reset_state(user, slice_obj, start_or_stop, result)
    except:
        print 3
        reset_state(user, slice_obj, start_or_stop, False)
        import traceback
        traceback.print_exc()


def reset_state(user, slice_obj, start_or_stop, result):
    print "==========> reset vpn state", result
    if result:
        if start_or_stop == 'start':
            slice_obj.vpn_state = 1
            log(user, slice_obj, u"启动VPN服务", SUCCESS)
        else:
            slice_obj.vpn_state = 0
            log(user, slice_obj, u"停止VPN服务", SUCCESS)
    else:
        if start_or_stop == 'start':
            slice_obj.vpn_state = 0
            log(user, slice_obj, u"启动VPN服务", FAIL)
        else:
            slice_obj.vpn_state = 1
            log(user, slice_obj, u"停止VPN服务", FAIL)
    slice_obj.save()
