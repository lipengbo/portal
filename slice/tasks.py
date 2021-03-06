from celery import task
from slice.models import Slice
from plugins.openflow.flowvisor_api import flowvisor_update_slice_status
from slice.slice_api import update_slice_virtual_network_cnvp, update_slice_virtual_network_flowvisor


@task()
def add(x, y):
    return x + y


@task()
def start_slice_sync(slice_id):
    flag = False
    try:
        slice_obj = Slice.objects.get(id=slice_id)
        if slice_obj.state == 4:
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
