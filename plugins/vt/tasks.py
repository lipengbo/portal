# -*- coding: UTF-8 -*-
from celery import task
from models import DOMAIN_STATE_DIC
from adminlog.models import log, SUCCESS, FAIL
from plugins.common.agent_client import AgentClient
from plugins.vt.models import Snapshot
import traceback

VM_TYPE = ((0, u'控制器'),(1, u'虚拟机'),(2, u'网关'))

@task()
def do_vm_action(user, vm, action):
    print "action .. vm uuid...........", action, vm.uuid
    try:
        action_result = vm.do_action(action)
        reset_state(user, vm, action, action_result, False)
    except:
        reset_state(user, vm, action, False, True)
    finally:
        print "---------------vm state : ", vm.state


def reset_state(user, vm, action, result, is_except):
    print "********vm action", vm.state, result, action
    print "******** is_except:", is_except
    if result:
        if action == "destroy":
            vm.state = DOMAIN_STATE_DIC['shutoff']
            vm.save()
            log(user, vm, u"停止"+VM_TYPE[vm.type][1], SUCCESS)
        else:
            vm.state = DOMAIN_STATE_DIC['running']
            vm.save()
            log(user, vm, u"启动"+ VM_TYPE[vm.type][1], SUCCESS)
    else:
        if action == "destroy":
            vm.state = DOMAIN_STATE_DIC['running']
            vm.save()
            log(user, vm, u"停止" + VM_TYPE[vm.type][1], FAIL)
        else:
            vm.state = DOMAIN_STATE_DIC['shutoff']
            vm.save()
            log(user, vm, u"启动" + VM_TYPE[vm.type][1], FAIL)

@task
def do_create_snapshot(vm, snapshot):
    print "create snapshot ", snapshot.uuid, "on ", vm.server.ip, "for vm ", vm.uuid
    try:
        result = AgentClient(vm.server.ip).create_snapshot(vm.uuid, snapshot.uuid)
        if result:
            set_current_snapshot(snapshot.uuid)
            snapshot.is_current = True
            snapshot.state = 1
            log(snapshot.owner, snapshot, u'创建备份', SUCCESS)
        else:
            raise
    except:
        snapshot.state = -1
        traceback.print_exc()
        log(snapshot.owner, snapshot, '创建备份', FAIL)
    finally:
        snapshot.save()
        print "create snapshot result is ", result

@task
def do_restore_snapshot(vm, snapshot):
    print "restore snapshot ", snapshot.uuid
    try:
        result = AgentClient(vm.server.ip).revert_to_snapshot(vm.uuid, snapshot.uuid)
        if result:
            set_current_snapshot(snapshot.uuid)
            snapshot.is_current = True
            snapshot.save()
            log(snapshot.owner, snapshot, u'还原备份', SUCCESS)
        else:
            raise
    except:
        traceback.print_exc()
        log(snapshot.owner, snapshot, u'还原备份', FAIL)
    finally:
        print "restore snapshot result is ", result

def set_current_snapshot(snapshot_uuid):
    for s in Snapshot.objects.exclude(uuid=snapshot_uuid):
        if s.is_current:
            s.is_current = False
            s.save()


