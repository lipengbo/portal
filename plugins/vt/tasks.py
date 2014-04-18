from celery import task
from models import DOMAIN_STATE_DIC

@task()
def do_vm_action(vm, action):
    try:
        action_result = vm.do_action(action)
        if action_result:
            if action == "destroy":
                vm.state = DOMAIN_STATE_DIC['shutoff']
            else:
                vm.state = DOMAIN_STATE_DIC['running']
            result = True
        else:
            if action == "destroy":
                vm.state = DOMAIN_STATE_DIC['shutoff']
                result = True
            else:
                result = False
        if result == True:
            vm.save()
        print "---------------vm state : ", vm.state
        #return result
    except:
        pass
