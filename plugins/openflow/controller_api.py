# coding:utf-8
from slice.models import Slice
from plugins.openflow.models import Controller
from slice.slice_exception import DbError, ControllerUsedError
from flowvisor_api import flowvisor_update_sice_controller
from django.db import transaction
import logging
LOG = logging.getLogger("CENI")


@transaction.commit_on_success
def slice_add_controller(slice_obj, controller):
    """slice添加控制器
    """
    LOG.debug('slice_add_controller')
    if slice_obj and controller:
        if controller.is_used():
            raise ControllerUsedError('控制器已经被使用！')
        if not slice_obj.get_controller():
            try:
                slice_obj.add_resource(controller)
            except Exception, ex:
                transaction.rollback()
                raise DbError(ex)
    else:
        raise DbError("数据库异常")


@transaction.commit_on_success
def create_user_defined_controller(island, controller_ip, controller_port):
    """创建用户自定义控制器记录
    """
    try:
        controller = Controller(
            name='user_define',
            ip=controller_ip,
            port=controller_port,
            http_port=0,
            state=1,
            island=island)
        controller.save()
        return controller
    except Exception, ex:
        transaction.rollback()
        raise DbError(ex)


def delete_controller(controller):
    """创建用户自定义控制器记录
    """
    if controller:
        if controller.name == 'user_define' and (not controller.host):
            controller.delete()
        else:
            pass


@transaction.commit_on_success
def slice_change_controller(slice_obj, controller_ip, controller_port):
    """slice更改控制器
    """
    LOG.debug('slice_change_controller')
    try:
        Slice.objects.get(id=slice_obj.id)
    except Exception, ex:
        raise DbError(ex)
    else:
        haved_controller = slice_obj.get_controller()
        if haved_controller and (haved_controller.ip != controller_ip or haved_controller.port != int(controller_port)):
            try:
                haved_controller.ip = controller_ip
                haved_controller.port = int(controller_port)
                haved_controller.save()
                flowvisor_update_sice_controller(slice_obj.get_flowvisor(),
                    slice_obj.name, controller_ip, controller_port)
            except Exception, ex:
                transaction.rollback()
                raise DbError(ex)
