#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename:views.py
# Date:Mon Sep 23 18:36:59 CST 2013
# Author:Pengbo Li
# E-mail:lipengbo10054444@gmail.com
import json
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from forms import VmForm
from slice.models import Slice
from plugins.vt.models import VirtualMachine
from django.core.urlresolvers import reverse
from etc.config import vnctunnel, function_test
from plugins.common.vt_manager_client import VTClient
from resources.models import Server
import logging
LOG = logging.getLogger('plugins')


def vm_list(request, sliceid):
    vms = get_object_or_404(Slice, id=sliceid).virtualmachine_set.all()
    context = {}
    context['vms'] = vms
    context['sliceid'] = sliceid
    context['slice_obj'] = Slice.objects.get(id=sliceid)
    return render(request, 'vt/vm_list.html', context)


def create_vm(request, sliceid):
    if request.method == 'POST':
        vm_form = VmForm(request.POST)
        if vm_form.is_valid():
            try:
                vm = vm_form.save(commit=False)
                slice = get_object_or_404(Slice, id=sliceid)
                vm.slice = slice
                vm.island = vm.server.island
                if not function_test:
                    hostlist = [(vm.server.id, vm.server.ip)]
                    serverid = VTClient().schedul(vm.flavor.cpu, vm.flavor.ram, vm.flavor.hdd, hostlist)
                    if not serverid:
                        raise Exception('resource not enough')
                    vm.server = Server.objects.get(id=serverid)
                vm.type = 1
                vm.save()
                return HttpResponse(json.dumps({'result': 0}))
            except Exception, e:
                return HttpResponse(json.dumps({'result': 1, 'error': str(e)}))
        return HttpResponse(json.dumps({'result': 1, 'error': 'vm invalide'}))
    else:
        vm_form = VmForm()
        slice = get_object_or_404(Slice, id=sliceid)
        servers = [(switch.virtualswitch.server.id, switch.virtualswitch.server.name) for switch in slice.get_virtual_switches_server()]
        servers.insert(0, ('', '---------'))
        vm_form.fields['server'].choices = servers
        context = {}
        context['vm_form'] = vm_form
        context['sliceid'] = sliceid
        context['slice_obj'] = Slice.objects.get(id=sliceid)
        return render(request, 'vt/create_vm.html', context)


def do_vm_action(request, vmid, action):
    operator = ('create', 'suspend', 'undefine', 'resume', 'destroy')
    if action in operator:
        try:
            vm = VirtualMachine.objects.get(id=vmid)
            if vm.do_action(action):
                return HttpResponse(json.dumps({'result': 0}))
        except Exception, e:
            return HttpResponse(json.dumps({'result': 1, 'error': str(e)}))
    return HttpResponse(json.dumps({'result': 1, 'error': 'operator failed!'}))


def vnc(request, vmid):
    vm = VirtualMachine.objects.get(id=vmid)
    host_ip = vm.server.ip
    vnc_port = vm.vnc_port
    context = {}
    context['host_ip'] = host_ip
    context['vnc_port'] = vnc_port
    context['tunnel_host'] = vnctunnel
    context['vm'] = vm
    return render(request, 'vt/vnc.html', context)


def delete_vm(request, vmid, flag):
    vm = VirtualMachine.objects.get(id=vmid)
    try:
        vm.delete()
        if flag == '1':
            return HttpResponseRedirect(reverse("vm_list", kwargs={"sliceid": vm.slice.id}))
        else:
            return HttpResponseRedirect(reverse("slice_detail", kwargs={"slice_id": vm.slice.id}))
    except Exception, ex:
        import traceback
        LOG.debug(traceback.print_exc())
    return render(request, 'slice/warning.html', {'info': str(ex)})
