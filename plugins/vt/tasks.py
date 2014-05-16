from celery import task
from models import DOMAIN_STATE_DIC

@task()
def do_vm_action(vm, action):
    print "cerlry .............", action
    try:
        action_result = vm.do_action(action)
        reset_state(vm, action, action_result, False)
    except:
        reset_state(vm, action, False, True)
    finally:
        print "---------------vm state : ", vm.state


def reset_state(vm, action, result, is_except):
    print "********vm action", vm.state, result, action
    print "******** is_except:", is_except
    if result:
        if action == "destroy":
            vm.state = DOMAIN_STATE_DIC['shutoff']
        else:
            vm.state = DOMAIN_STATE_DIC['running']
    else:
        if action == "destroy":
#             if is_except:
            vm.state = DOMAIN_STATE_DIC['running']
        else:
#             if is_except:
            vm.state = DOMAIN_STATE_DIC['shutoff']
    vm.save()

