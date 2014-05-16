# -*- coding: UTF-8 -*-
from celery import task
from models import DOMAIN_STATE_DIC
from adminlog.models import log, SUCCESS, FAIL

@task()
def do_vm_action(user, vm, action):
    print "cerlry .............", action
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
            log(user, vm, u"虚拟机停止成功", SUCCESS)
        else:
            vm.state = DOMAIN_STATE_DIC['running']
            log(user, vm, u"虚拟机启动成功", SUCCESS)
    else:
        if action == "destroy":
            #if is_except:
            vm.state = DOMAIN_STATE_DIC['running']
            log(user, vm, u"虚拟机停止失败", FAIL)
        else:
            #if is_except:
            vm.state = DOMAIN_STATE_DIC['shutoff']
            log(user, vm, u"虚拟机启动失败", FAIL)
    vm.save()

