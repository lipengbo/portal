# -*- coding: UTF-8 -*-
from celery import task
from adminlog.models import log, SUCCESS, FAIL
from plugins.common.agent_client import AgentClient
from plugins.vt.models import Snapshot
import traceback

@task
def do_create_snapshot(vm, snapshot):
    print "create snapshot ", snapshot.uuid, "on ", vm.server.ip, "for vm ", vm.uuid
    try:
        result = AgentClient(vm.server.ip).create_snapshot(vm.uuid, snapshot.uuid)
        if result:
            #set_current_snapshot(snapshot.uuid, vm)
            snapshot.is_current = False
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
            set_current_snapshot(snapshot.uuid, vm)
            snapshot.is_current = True
            snapshot.save()
            vm.current_snapshot = snapshot.name
            vm.save()
            log(snapshot.owner, snapshot, u'还原备份', SUCCESS)
        else:
            raise
    except:
        traceback.print_exc()
        log(snapshot.owner, snapshot, u'还原备份', FAIL)
    finally:
        print "restore snapshot result is ", result

def set_current_snapshot(snapshot_uuid, vm):
    for s in Snapshot.objects.filter(vm=vm):
        if s.is_current:
            s.is_current = False
            s.save()


