#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename:views.py
# Date:Mon Sep 23 18:36:59 CST 2013
# Author:Pengbo Li
# E-mail:lipengbo10054444@gmail.com
import traceback
import json
import errno
from socket import error as socket_error
from plugins.common.exception import ResourceNotEnough
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from forms import VmForm
from slice.models import Slice
from plugins.vt.models import VirtualMachine, DOMAIN_STATE_DIC
from django.core.urlresolvers import reverse
from etc.config import function_test
from plugins.common.vt_manager_client import VTClient
from plugins.common.agent_client import AgentClient
from plugins.common.ovs_client import get_portid_by_name
from plugins.ipam.models import Subnet
from models import Image, Flavor
from resources.models import Server, SwitchPort
from plugins.vt import api
import logging
from django.utils.translation import ugettext as _
LOG = logging.getLogger('plugins')


def vm_list(request, sliceid):
    vms = get_object_or_404(Slice, id=sliceid).virtualmachine_set.all()
    context = {}
    user = request.user
    if user.is_superuser:
        context['extent_html'] = "admin_base.html"
    else:
        context['extent_html'] = "site_base.html"
    context['vms'] = vms
    context['sliceid'] = sliceid
    slice_obj = Slice.objects.get(id=sliceid)
    context['slice_obj'] = slice_obj
    context['check_vm_status'] = 0
    subnet = get_object_or_404(Subnet, owner=slice_obj.name)
    context['start_ip'] = subnet.get_ip_range()[0]
    context['end_ip'] = subnet.get_ip_range()[1]

    for vm in vms:
        if vm.state == 8:
            context['check_vm_status'] = 1
            break
    return render(request, 'vt/vm_list.html', context)


def create_vm(request, sliceid, from_link):
    """
    from_link : 记录链接跳转的入口，以便返回原来的页面。 0 为从slic详情页面转入， 1为从虚拟机列表页面转入
    """
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
                        raise ResourceNotEnough()
                    vm.server = Server.objects.get(id=serverid)
                vm.type = 1
                vm.save()
                return HttpResponse(json.dumps({'result': 0}))
            except socket_error as serr:
                if serr.errno == errno.ECONNREFUSED:
                    return HttpResponse(json.dumps({'result': 1, 'error': _("connection refused")}))
            except ResourceNotEnough, e:
                return HttpResponse(json.dumps({'result': 1, 'error': e.message}))
            except:
                return HttpResponse(json.dumps({'result': 1, 'error': _('server error')}))
        return HttpResponse(json.dumps({'result': 1, 'error': _('vm invalide')}))
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
        context['from_link'] = from_link
        return render(request, 'vt/create_vm.html', context)


def do_vm_action(request, vmid, action):
    operator = ('create', 'suspend', 'undefine', 'resume', 'destroy')
    if action in operator:
        try:
            vm = VirtualMachine.objects.get(id=vmid)
            result = api.do_vm_action(vm, action)
            if result:
                return HttpResponse(json.dumps({'result': 0}))
        except socket_error as serr:
            if serr.errno == errno.ECONNREFUSED:
                return HttpResponse(json.dumps({'result': 1, 'error': _("connection refused")}))
    return HttpResponse(json.dumps({'result': 1, 'error': _('vm operation failed')}))


def vnc(request, vmid):
    vm = VirtualMachine.objects.get(id=vmid)
    host_ip = vm.server.ip
    vnc_port = AgentClient(host_ip).get_vnc_port(vm.uuid)
    token = '%s_%s_%s_%s_%s_%s' % (host_ip, vnc_port, vm.name, vm.ip, vm.image.username, vm.image.password)
    novnc_url = 'http://%s:6080/vnc_auto.html?token=%s' % (request.META.get('HTTP_HOST').split(':')[0], token)
    #context = {}
    #context['host_ip'] = host_ip
    #context['vnc_port'] = vnc_port
    #context['tunnel_host'] = '192.168.5.9'
    #context['vm'] = vm
    #return render(request, 'vt/vnc.html', context)
    #return HttpResponseRedirect(reverse("vm_list", kwargs={"sliceid": vm.slice.id}))
    return HttpResponseRedirect(novnc_url)


def delete_vm(request, vmid, flag):
    vm = VirtualMachine.objects.get(id=vmid)
    try:
        vm.delete()
        if flag == '1':
            return HttpResponseRedirect(reverse("vm_list", kwargs={"sliceid": vm.slice.id}))
        else:
            return HttpResponse(json.dumps({'result': 0}))
#             return HttpResponseRedirect(reverse("slice_detail", kwargs={"slice_id": vm.slice.id}))
    except Exception, ex:
        LOG.debug(traceback.print_exc())
        if flag == '0':
            return HttpResponse(json.dumps({'result': 1, 'error_info': str(ex)}))
    return render(request, 'slice/warning.html', {'info': str(ex)})


def get_vms_state_by_sliceid(request, sliceid):
    slice_obj = get_object_or_404(Slice, id=sliceid)
    vms = slice_obj.virtualmachine_set.all()
    context = {}
    context['vms'] = [vm.__dict__ for vm in vms if vm.__dict__.pop('_state')]
    context['sliceid'] = sliceid
    return HttpResponse(json.dumps(context))


def get_slice_gateway_ip(request, slice_name):
    subnet = get_object_or_404(Subnet, owner=slice_name)
    return HttpResponse(json.dumps({'ipaddr': subnet.get_gateway_ip()}))


def set_domain_state(vname, state):
    try:
        vm_query = VirtualMachine.objects.filter(uuid=vname)
        switch_port = None
        if state not in [DOMAIN_STATE_DIC['building'], DOMAIN_STATE_DIC['failed'], DOMAIN_STATE_DIC['notexist']]:
            host = vm_query[0].server
            slice = vm_query[0].slice
            name = vm_query[0].name
            switch = host.virtualswitch_set.all()[0]
            port = get_portid_by_name(host.ip, vname)
            switch_port = SwitchPort(switch=switch, port=port, name=name)
            switch_port.save()
            slice.add_resource(switch_port)
    except:
        LOG.debug(traceback.print_exc())
    finally:
        vm_query.update(state=state, switch_port=switch_port)
        return True

def get_flavor_msg(request):
    name = request.POST.get("name")
    obj_id = request.POST.get("obj_id")
    if name == 'flavor':
        flavor = get_object_or_404(Flavor, id=obj_id)
        return HttpResponse(json.dumps({'cpu':flavor.cpu, 'ram':flavor.ram, 'hdd':flavor.hdd}))
    if name == 'image':
        image = get_object_or_404(Image, id=obj_id)
        print image.username, image.password
        return HttpResponse(json.dumps({'username':image.username, 'password' : image.password}))
