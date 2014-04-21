from celery import task
from slice.models import Slice
from plugins.openflow.flowvisor_api import flowvisor_update_slice_status
from slice.slice_api import update_slice_virtual_network_cnvp, update_slice_virtual_network_flowvisor
from plugins.vt.models import DOMAIN_STATE_DIC


@task()
def add(x, y):
    return x + y


@task()
def start_slice_sync(slice_id, controller_flag, gw_flag):
    flag = False
    ct_op = True
    gw_op = True
    try:
        slice_obj = Slice.objects.get(id=slice_id)
        if controller_flag:
            controller = slice_obj.get_controller()
            if controller.host:
                action_result = controller.host.do_action("create")
                if action_result:
                    controller.host.state = DOMAIN_STATE_DIC['running']
                else:
                    controller.host.state = DOMAIN_STATE_DIC['shutoff']
                    ct_op = False
                controller.host.save()
        if gw_flag:
            gw = slice_obj.get_gw()
            if gw and gw.enable_dhcp:
                action_result = gw.do_action("create")
                if action_result:
                    gw.state = DOMAIN_STATE_DIC['running']
                else:
                    gw.state = DOMAIN_STATE_DIC['shutoff']
                    gw_op = False
                gw.save()
        if ct_op and gw_op:
            flowvisor = slice_obj.get_flowvisor()
            if flowvisor.type == 1:
                flowvisor_update_slice_status(flowvisor,
                                              slice_obj.id, False)
                update_slice_virtual_network_cnvp(slice_obj)
                flowvisor_update_slice_status(flowvisor,
                                              slice_obj.id, True)
                flag = True
            else:
                flowvisor_update_slice_status(flowvisor,
                                              slice_obj.id, True)
                flag = True
                update_slice_virtual_network_flowvisor(slice_obj)
            slice_obj.start()
    except Slice.DoesNotExist:
        pass
    except:
        try:
            slice_obj.stop()
            if flag:
                flowvisor_update_slice_status(flowvisor,
                                              slice_obj.id, False)
        except:
            pass


@task()
def stop_slice_sync(slice_id):
    try:
        slice_obj = Slice.objects.get(id=slice_id)
        if slice_obj.state == 3:
            flowvisor_update_slice_status(slice_obj.get_flowvisor(),
                                                  slice_obj.id, False)
            slice_obj.stop()
    except Slice.DoesNotExist:
        pass
    except:
        slice_obj.start()
