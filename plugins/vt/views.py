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
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from forms import VmForm
from slice.models import Slice
from plugins.vt.models import VirtualMachine, DOMAIN_STATE_DIC
from django.core.urlresolvers import reverse
from etc.config import function_test
from plugins.common.vt_manager_client import VTClient
from plugins.common.agent_client import AgentClient
#from plugins.common.ovs_client import get_portid_by_name
from plugins.ipam.models import Subnet
from models import Flavor, SSHKey
from resources.models import Server, SwitchPort
from plugins.vt import api
#from plugins.common import glance
import logging
from django.utils.translation import ugettext as _
LOG = logging.getLogger('plugins')


def vm_list(request, sliceid):
    slice_obj = get_object_or_404(Slice, id=sliceid)
    vms = slice_obj.get_common_vms()
    context = {}
    user = request.user
    if user.is_superuser:
        context['extent_html'] = "admin_base.html"
    else:
        context['extent_html'] = "site_base.html"
        if user.has_perm('slice.change_slice', slice_obj):
            context['permission'] = "edit"
        else:
            if user.has_perm('project.create_slice', slice_obj.project):
                context['permission'] = "view"
            else:
                return redirect('forbidden')
    context['vms'] = vms
    context['sliceid'] = sliceid
    slice_obj = Slice.objects.get(id=sliceid)
    context['slice_obj'] = slice_obj
    context['check_vm_status'] = 0
    subnet = get_object_or_404(Subnet, owner=slice_obj.uuid)
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
                vm.ram = request.POST.get("ram")
                vm.cpu = request.POST.get("cpu")
                vm.hdd = request.POST.get("hdd")
                if request.POST.get("enable_dhcp") == '0':
                    vm.enable_dhcp = False
                else:
                    vm.enable_dhcp = True
                flavor = Flavor.objects.filter(id=request.POST.get("flavor"))
                if flavor.count() == 0:
                    vm.flavor = None
                else:
                    vm.flavor = flavor[0]

                if not function_test:
                    hostlist = [(vm.server.id, vm.server.ip)]
                    serverid = VTClient().schedul(vm.cpu, vm.ram, vm.hdd, hostlist)
                    #if not serverid:
                    #raise ResourceNotEnough('resource not enough')
                    vm.server = Server.objects.get(id=serverid)
                vm.type = 1
                vm.save()
                vm.slice.flowspace_changed(2)
                return HttpResponse(json.dumps({'result': 0}))
            except socket_error as serr:
                if serr.errno == errno.ECONNREFUSED:
                    return HttpResponse(json.dumps({'result': 1, 'error': _("connection refused")}))
            except ResourceNotEnough, e:
                vm.state = 11
                vm.type =1
                vm.save()
                return HttpResponse(json.dumps({'result': 1, 'error': e.message}))
            except StopIteration, e:
                return HttpResponse(json.dumps({'result': 1, 'error': e.message}))
        return HttpResponse(json.dumps({'result': 1, 'error': _('vm invalide')}))
    else:
        vm_form = VmForm()
        slice = get_object_or_404(Slice, id=sliceid)
        servers = [(switch.virtualswitch.server.id, switch.virtualswitch.server.name) for switch in slice.get_virtual_switches_server()]
        servers.insert(0, ('', '---------'))
        vm_form.fields['server'].choices = servers
        context = {}
        context['vm_form'] = vm_form
        context['flavors'] = Flavor.objects.all()
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
    #image = glance.image_get(vm.image)
    #token = '%s_%s_%s_%s_%s_%s' % (host_ip, vnc_port, vm.name, vm.ip, image.properties['username'], image.properties['password'])
    token = '%s_%s_%s_%s_%s_%s' % (host_ip, vnc_port, vm.name, vm.ip, 'root', '123')
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
        #if flag == '1':
            #return HttpResponseRedirect(reverse("vm_list", kwargs={"sliceid": vm.slice.id}))
        #else:
        vm.slice.flowspace_changed(3)
        return HttpResponse(json.dumps({'result': 0}))
    except Exception:
        LOG.debug(traceback.print_exc())
        #if flag == '0':
        return HttpResponse(json.dumps({'result': 1, 'error_info': _('failed to delete vm')}))
    #return render(request, 'slice/warning.html', {'info': _('failed to delete vm')})


def get_vms_state_by_sliceid(request, sliceid):
    slice_obj = get_object_or_404(Slice, id=sliceid)
    vms = slice_obj.virtualmachine_set.all()
    context = {}
#     context['vms'] = [vm.__dict__ for vm in vms if vm.__dict__.pop('_state')]
    context['vms'] = []
    for vm in vms:
        if vm.switch_port:
            info = {'id': vm.id, 'state': vm.state,
                'switch_id': vm.switch_port.switch.id,
                'port': vm.switch_port.port, 'port_name':vm.switch_port.name}
        else:
            info = {'id': vm.id, 'state': vm.state}
        context['vms'].append(info)
    context['sliceid'] = sliceid
    return HttpResponse(json.dumps(context))


def get_slice_gateway_ip(request, slice_name):
    subnet = get_object_or_404(Subnet, owner=slice_name)
    return HttpResponse(json.dumps({'ipaddr': subnet.get_gateway_ip()}))


def set_domain_state(vname, state):
    try:
        result = 1
        vm_query = VirtualMachine.objects.filter(uuid=vname)
        switch_port = None
        vm = vm_query[0]
        if vm.type != 0 and state == DOMAIN_STATE_DIC['nostate']:
            host = vm.server
            slice = vm.slice
            name = vm.name
            switch = host.virtualswitch_set.all()[0]
            used_ofport_list = [port.port for port in SwitchPort.objects.filter(switch=switch)]
            free_ofport = list(set(range(64500, 65000)) - set(used_ofport_list))[0]
            #port = get_portid_by_name(host.ip, vname)
            switch_port = SwitchPort(switch=switch, port=free_ofport, name=name)
            switch_port.save()
            slice.add_resource(switch_port)
    except IndexError:
        result = 0
    except:
        LOG.debug(traceback.print_exc())
    finally:
        if switch_port:
            vm_query.update(state=state, switch_port=switch_port)
        else:
            vm_query.update(state=state)
        #if not api.try_start_gw_and_ctr(vm):
            #LOG.error('try to start gw and controller failed')
        return result


def get_flavor_msg(request):
    name = request.POST.get("name")
    obj_id = request.POST.get("obj_id")
    if name == 'flavor':
        flavor = get_object_or_404(Flavor, id=obj_id)
        return HttpResponse(json.dumps({'cpu':flavor.cpu, 'ram':flavor.ram, 'hdd':flavor.hdd}))
    if name == 'image':
        #image = get_object_or_404(Image, id=obj_id)
        #print image.username, image.password
        #return HttpResponse(json.dumps({'username':image.username, 'password' : image.password}))
        return HttpResponse(json.dumps({'username': 'root', 'password': '123'}))

def download_keypair(request):
    slice_obj = get_object_or_404(Slice, id=request.POST.get("slice_id"))
    sshkey = SSHKey.objects.get(slice=slice_obj)
    response = HttpResponse(sshkey.private_key, content_type='plain/text')
    response['Content-Disposition'] = 'attachment; filename="id_rsa"'
    return response
