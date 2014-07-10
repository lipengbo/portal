# -*- coding: utf-8 -*-
import json
import traceback

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Q
from plugins.vt.models import VirtualMachine, Snapshot
from plugins.common.agent_client import AgentClient
from plugins.common.utils import gen_uuid
from tasks import do_create_snapshot, do_restore_snapshot
from adminlog.models import log, SUCCESS, FAIL
from etc import config


@login_required
def list_snapshot(request):
    context = {}
    if request.user.is_superuser:
        snapshots = Snapshot.objects.filter(state=1).order_by('create_time')
        context['extent_html'] = 'admin_base.html'
    else:
        snapshots = Snapshot.objects.filter(owner=request.user, state=1).order_by('create_time')
        context['extent_html'] = 'site_base.html'

    if 'query' in request.GET:
        query = request.GET.get('query')
        if query:
            snapshots = snapshots.filter(Q(name__icontains=query) | Q(desc__icontains=query))
            context['query'] = query
    context['snapshots'] = snapshots
    return render(request, 'snapshot_list.html', context)

def create_snapshot(request):
    if request.method == 'POST':
        vm_id = request.POST.get('vm_id')
        name = request.POST.get("name")
        desc = request.POST.get("desc")
        snapshot = Snapshot()
        snapshot.owner = request.user
        vm = get_object_or_404(VirtualMachine, id=vm_id)
        snapshot.vm = vm
        snapshot.uuid = gen_uuid()
        snapshot.name = name
        snapshot.desc = desc
        snapshot.state = 0
        snapshot.save()
        do_create_snapshot.delay(vm, snapshot)
    return HttpResponse(json.dumps({'result': '0'}))

def delete_snapshot(request):
    if request.method == 'POST':
        #vm = get_object_or_404(VirtualMachine, id=request.POST.get('vm_id'))
        snapshot_uuid = request.POST.get('snapshot_uuid')
        snapshot = Snapshot.objects.get(uuid=snapshot_uuid)
        vm = snapshot.vm
        try:
            if AgentClient(vm.server.ip).delete_snapshot(vm.uuid, snapshot_uuid):
                snapshot.delete()
                return HttpResponse(json.dumps({'result': 0}))
            else:
                raise
        except:
            traceback.print_exc()
            return HttpResponse(json.dumps({'result': -1}))

def restore_snapshot(request):
    if request.method == 'POST':
        vm = get_object_or_404(VirtualMachine, id=request.POST.get('vm_id'))
        snapshot_uuid = request.POST.get('snapshot_uuid')
        snapshot = Snapshot.objects.get(uuid=snapshot_uuid)
        do_restore_snapshot.delay(vm, snapshot)
        return HttpResponse(json.dumps({'result': 0}))

def edit_snapshot(request):
    try:
        snapshot_uuid = request.POST.get('uuid')
        name = request.POST.get('name')
        desc = request.POST.get('desc')
        snapshot = Snapshot.objects.get(uuid=snapshot_uuid)
        snapshot.name = name
        snapshot.desc = desc
        snapshot.save()
        return HttpResponse(json.dumps({'result': 0}))
    except:
        traceback.print_exc()
        return HttpResponse(json.dumps({'result': -1}))

def create_image(request):
    try:
        _uuid = request.POST.get('uuid')
        name = request.POST.get('name')
        desc = request.POST.get('desc')
        username = request.POST.get('username')
        passwd = request.POST.get('passwd')
        is_public = request.POST.get('is_public')
        flag = request.POST.get('flag')
        image_meta = {'is_public': is_public, 'disk_format': 'qcow2',\
                      'container_format': 'ovf', 'name': name,\
                      'owner': request.user.username, \
                      'properties':{'description': desc, 'image_type': 1, 'image_attr': 3,\
                                    'image_username': username, 'image_passwd': passwd}}
        url = config.generate_glance_url()

        if int(flag) == 0:
            snapshot = Snapshot.objects.get(uuid=_uuid)
            vm = snapshot.vm

            result = AgentClient(vm.server.ip)\
                    .create_image_from_snapshot(vm.uuid, snapshot.uuid, url, image_meta)
            log(request.user, None, u"基于备份创建自有镜像", SUCCESS)
            print '----create_image_from_snapshot', result
        else:
            vm = VirtualMachine.objects.get(uuid=_uuid)
            result = AgentClient(vm.server.ip).create_image_from_vm(_uuid, url, image_meta)
            log(request.user, None, u"基于虚拟机创建自有镜像", SUCCESS)
            print '----create_image_from_vm', result
        return HttpResponse(json.dumps({'result': 0}))
    except:
        traceback.print_exc()
        log(request.user, None, u"创建自有镜像失败", FAIL)
        return HttpResponse(json.dumps({'result': -1}))
