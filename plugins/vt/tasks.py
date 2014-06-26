# -*- coding: UTF-8 -*-
from celery import task
from models import DOMAIN_STATE_DIC
from adminlog.models import log, SUCCESS, FAIL
from plugins.common.agent_client import AgentClient
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
def do_create_snapshot(server_ip, vm, snapshot):
    print "create snapshot ", snapshot.uuid, "on ", server_ip, "for vm ", vm.uuid
    try:
        result = AgentClient(server_ip).create_snapshot(vm.uuid, snapshot.uuid)
        if result:
            snapshot.state = 1
        else:
            snapshot.state = -1
    except:
        snapshot.state = -1
        traceback.print_exc()
    finally:
        snapshot.save()
        print "result is ", result




