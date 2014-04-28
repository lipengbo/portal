from celery import task
from models import DOMAIN_STATE_DIC

@task()
def do_vm_action(vm, action):
    try:
        print "cerlry .............", action
        action_result = vm.do_action(action)
        if action_result:
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
        print "---------------vm state : ", vm.state
        #return result
    except:
        pass
