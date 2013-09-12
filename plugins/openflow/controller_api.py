# coding:utf-8
from models import *
from slice.slice_exception import *
from flowvisor_api import *
from django.db import transaction
import logging
LOG = logging.getLogger("CENI")


@transaction.commit_on_success
def slice_add_controller(slice_obj, controller, island):
    """slice添加控制器
    """
    LOG.debug('slice_add_controller')
    if slice_obj and controller and island:
        flowvisor = island.flowvisor_set.all()[0]
        if controller.slices.all().count() > 0:
            raise ControllerUsedError('控制器已经被使用！')
        if slice.controller_set.all().count() == 0 and slice.flowvisor_set.all().count() == 0:
            try:
#                 flowvisor_add_slice(flowvisor, controller, slice_obj.name, slice_obj.email)
                slice_obj.add_resource(flowvisor)
                slice_obj.add_resource(controller)
            except:
                transaction.rollback()
                raise
    else:
        raise DbError("数据库异常")


@transaction.commit_on_success
def slice_change_controller(slice_obj, new_controller):
    """slice更改控制器
    """
    LOG.debug('slice_change_controller')
    from CENI.Project.slice_api import get_slice_controller
    old_controller = get_slice_controller(slice_obj)
    if old_controller and new_controller and old_controller.id != new_controller.id:
        try:
            flowvisor_controller = ceni_flowvisor_related.objects.get(
                slice_id=slice_obj.id,
                related_type=1)
            flowvisor = ceni_facility_server.objects.get(
                id=flowvisor_controller.flowvisor_id)
            flowvisor_update_sice_controller(flowvisor, new_controller, slice_obj)
            old_controller.used = 0
            old_controller.save()
            new_controller.used = 1
            new_controller.save()
            flowvisor_controller.related_id = new_controller.id
            flowvisor_controller.save()
        except:
            transaction.rollback()
            raise


def slice_remove_controller(slice_obj, flowvisor, controller):
    """slice移除控制器
    """
    LOG.debug('slice_remove_controller')
    if slice_obj and flowvisor and controller:
        try:
            controller.used = 0
            controller.save()
            flowvisor_controllers = ceni_flowvisor_related.objects.filter(
                slice_id=slice_obj.id,
                flowvisor_id=flowvisor.id,
                related_id=controller.id,
                related_type=1)
            flowvisor_controllers.delete()
        except Exception, ex:
            transaction.rollback()
            raise DbError(ex)


def is_controller_used():
    """判断控制器是否被使用
    """
    LOG.debug('is_controller_used')
