from celery import task
from models import DOMAIN_STATE_DIC

@task()
def do_vm_action(vm, action):
    print "cerlry .............", action
    try:
        action_result = vm.do_action(action)
        reset_state(vm, action, action_result)
    except:
        reset_state(vm, action, False)
    finally:
        print "---------------vm state : ", vm.state


def reset_state(vm, action, result):
    if result:
        if action == "destroy":
            vm.state = DOMAIN_STATE_DIC['shutoff']
        else:
            vm.state = DOMAIN_STATE_DIC['running']
    else:
        if action == "destroy":
            vm.state = DOMAIN_STATE_DIC['running']
        else:
            vm.state = DOMAIN_STATE_DIC['shutoff']
    vm.save()

