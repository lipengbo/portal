#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename:views.py
# Date:Mon Sep 23 18:36:59 CST 2013
# Author:Pengbo Li
# E-mail:lipengbo10054444@gmail.com
import traceback
import json
import time
import errno
from socket import error as socket_error
from plugins.common.exception import ResourceNotEnough
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from forms import VmForm
from slice.models import Slice
from plugins.vt.models import VirtualMachine, DOMAIN_STATE_DIC
from django.core.urlresolvers import reverse
from etc.config import function_test
from plugins.common.vt_manager_client import VTClient
from plugins.common.agent_client import AgentClient
from plugins.common.aes import *
#from plugins.common.ovs_client import get_portid_by_name
from plugins.ipam.models import Subnet
from models import Image, Flavor, SSHKey
from resources.models import Server, SwitchPort
from resources.ovs_api import get_edge_ports, slice_add_port_device
from plugins.vt import api
from project.models import Island
import logging
from django.utils.translation import ugettext as _
from adminlog.models import log, SUCCESS, FAIL
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


def create_vm(request, sliceid):
    user = request.user
    vm_count = VirtualMachine.objects.total_vms(user)
    if request.method == 'POST':
        if user.quotas.vm <= vm_count:
            return redirect('forbidden')
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

                #: test ram quota
                if user.quotas.mem < (int(vm.ram) + VirtualMachine.objects.user_stat_sum(user, 'ram')):
                    message = "您已分配的内存大小已经超过配额"
                    return HttpResponse(json.dumps({'result': -1, 'error': message}))

                #: test cpu quota
                if user.quotas.cpu < (int(vm.cpu) + VirtualMachine.objects.user_stat_sum(user, 'cpu')):
                    return HttpResponse(json.dumps({'result': -1, 'error': "您的CPU数量已经超过配额"}))

                #: test disk quota
                if user.quotas.disk < (int(vm.hdd) + VirtualMachine.objects.user_stat_sum(user, 'hdd')):
                    message = "您的磁盘容量已经超过配额"
                    return HttpResponse(json.dumps({'result': -1, 'error': message}))

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
                #if serr.errno == errno.ECONNREFUSED:
                log(user, vm, u"创建虚拟机", FAIL)
                return HttpResponse(json.dumps({'result': 1, 'error': _("connection refused")}))
            except ResourceNotEnough, e:
                log(user, vm, u"创建虚拟机", FAIL)
                vm.state = 11
                vm.type =1
                try:
                    vm.save()
                    return HttpResponse(json.dumps({'result': 1, 'error': e.message}))
                except:
                    raise
            except StopIteration, e:
                log(user, vm, u"创建虚拟机", FAIL)
                return HttpResponse(json.dumps({'result': 1, 'error': e.message}))
            except:
                log(user, vm, u"创建虚拟机", FAIL)
                import traceback
                traceback.print_exc()
                return HttpResponse(json.dumps({'result' : 1, 'error': _('server error')}))
        else:
            log(user, vm, u"创建虚拟机", FAIL)
            return HttpResponse(json.dumps({'result': 1, 'error': _('vm invalide')}))
    else:
        if user.quotas.vm <= vm_count:
            messages.add_message(request, messages.INFO, "您的虚拟机数量已经超过配额")
            return redirect("quota_admin_apply")
        #: test ram quota
        if user.quotas.mem <= VirtualMachine.objects.user_stat_sum(user, 'ram'):
            messages.add_message(request, messages.INFO, "您已分配的内存大小已经超过配额")
            return redirect("quota_admin_apply")

        #: test cpu quota
        if user.quotas.cpu <= VirtualMachine.objects.user_stat_sum(user, 'cpu'):
            messages.add_message(request, messages.INFO, "您的CPU数量已经超过配额")
            return redirect("quota_admin_apply")

        #: test disk quota
        if user.quotas.disk <= VirtualMachine.objects.user_stat_sum(user, 'hdd'):
            messages.add_message(request, messages.INFO, "您的磁盘容量已经超过配额")
            return redirect("quota_admin_apply")

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
        return render(request, 'vt/create_vm.html', context)


def create_device(request, sliceid):
    if request.method == 'POST':
        try:
            ports_data = json.loads(request.POST.get('ports_data'))
            slice_obj = Slice.objects.get(id=sliceid)
            for port in ports_data:
                print port[0], "===", port[1]
                switch_port = SwitchPort.objects.get(id=port[0])
                slice_add_port_device(slice_obj, port[0], port[1], port[2])
                print "-------", port[2]
                log(request.user, switch_port, u"添加端口", SUCCESS)

            return HttpResponse(json.dumps({'result':0}))
        except Exception, e:
            traceback.print_exc()
            log(request.user, switch_port, u"添加端口", FAIL)
            return HttpResponse(json.dumps({'result':1, 'error': e.message}))
    else:
        context = {}
        context['slice_obj'] = Slice.objects.get(id=sliceid)
        return render(request, 'vt/custom_device.html', context)

def get_switch_port(request, sliceid):
    port_info = get_edge_ports(Slice.objects.get(id=sliceid))
    print "-------------------------------------------"
    print port_info
    print "-------------------------------------------"
    #return HttpResponse(json.dumps([{"id": 1, "name": "ovs-113", "dpid": "00:00:a0:36:9f:02:e4:18", \
    #                                 "ports": [{"id": 40, "name": "eth1", "port": 1, "type": 0}, \
    #                                        {"id": 41, "name": "eht2", "port": 2, "type": 1}]},\
    #                               {"id": 2, "name": "vovs-113", "dpid": "00:ee:00:00:00:00:01:13",\
    #                                 "ports": [{"id": 42, "name": "eht3", "port": 3, "type": 1},\
    return HttpResponse(json.dumps(port_info))



def do_vm_action(request, vmid, action):
    operator = ('create', 'suspend', 'undefine', 'resume', 'destroy')
    if action in operator:
        try:
            vm = VirtualMachine.objects.get(id=vmid)
            if action == 'create' and vm.state not in (DOMAIN_STATE_DIC['starting'], \
                                                       DOMAIN_STATE_DIC['running']):
                vm.state = DOMAIN_STATE_DIC['starting']
            elif action == 'destroy' and vm.state not in (DOMAIN_STATE_DIC['stopping'],\
                                                          DOMAIN_STATE_DIC['shutoff']):
                vm.state = DOMAIN_STATE_DIC['stopping']
            print ">>>>>>>>>>>>>>>>vm state:", vm.state
            vm.save()
            api.do_vm_action(request.user, vm, action)
            return HttpResponse(json.dumps({'result': 0}))
        except socket_error as serr:
            if action == 'create':
                log(request.user, vm, u"启动虚拟机", FAIL)
            elif action == 'destroy':
                log(request.user, vm, u"停止虚拟机", FAIL)
            else:
                log(request.user, vm, u"操作虚拟机", FAIL)
            if serr.errno == errno.ECONNREFUSED:
                return HttpResponse(json.dumps({'result': 1, 'error': _("connection refused")}))
    return HttpResponse(json.dumps({'result': 1, 'error': _('vm operation failed')}))


def vnc(request, vmid, island_id):
    vm = VirtualMachine.objects.get(id=vmid)
    island = get_object_or_404(Island, id=island_id)
    host_ip = vm.server.ip
    vnc_port = AgentClient(host_ip).get_vnc_port(vm.uuid)
    print "-----------vnc_port-----------", vnc_port
    private_msg = '%s_%s_%s' % (host_ip, vnc_port, time.time())
    vm_msg = '%s_%s_%s_%s' % (vm.name, vm.ip, vm.image.username, vm.image.password)
    mycrypt_tool = mycrypt()
    token = vm_msg + "_" + mycrypt_tool.encrypt(private_msg)
    novnc_url = 'http://%s:6080/vnc_auto.html?token=%s' \
                         %(island.novnc_ip, token)
            #            % (request.META.get('HTTP_HOST').split(':')[0], token)
    return HttpResponseRedirect(novnc_url)


def delete_vm(request, vmid, flag):
    vm = VirtualMachine.objects.get(id=vmid)
    try:
        vm.delete()
        #if flag == '1':
            #return HttpResponseRedirect(reverse("vm_list", kwargs={"sliceid": vm.slice.id}))
        #else:
        vm.slice.flowspace_changed(3)
        log(request.user, vm,  u"删除虚拟机", SUCCESS)
        return HttpResponse(json.dumps({'result': 0}))
    except Exception:
        LOG.debug(traceback.print_exc())
        log(request.user, vm, u"删除虚拟机", FAIL)
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

def log_vm_type(type):
    if type == 0:
        return u'创建控制器'
    elif type == 1:
        return u'创建虚拟机'
    else:
        return u'创建网关'

def set_domain_state(vname, state):
    try:
        result = 1
        vm_query = VirtualMachine.objects.filter(uuid=vname)
        vm = vm_query[0]
        user = vm.slice.owner
        if state == 0:
            log(user, vm, log_vm_type(vm.type), SUCCESS)
        elif state == 9:
            log(user, vm, log_vm_type(vm.type), FAIL)
        switch_port = None
        if vm.type != 0 and state not in [DOMAIN_STATE_DIC['building'], DOMAIN_STATE_DIC['failed'], DOMAIN_STATE_DIC['notexist']]:
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
        vm_query.update(state=state, switch_port=switch_port)
        #if not api.try_start_gw_and_ctr(vm):
            #LOG.error('try to start gw and controller failed')
        return result


def get_flavor_msg(request):
    if request.method == 'GET':
        print "===========flavor objects============="
        cpus = Flavor.objects.values_list('cpu', flat=True).distinct()
        rams = Flavor.objects.values_list('ram', flat=True).distinct()
        print list(cpus)
        try:
            print json.dumps({'cpus': list(cpus), 'rams': list(rams)})
        except:
            import traceback
            traceback.print_exc()
            pass
        return HttpResponse(json.dumps({'cpus': list(cpus), 'rams': list(rams)}))
    else:
        name = request.POST.get("name")
        obj_id = request.POST.get("obj_id")
        if name == 'flavor':
            flavor = get_object_or_404(Flavor, id=obj_id)
            return HttpResponse(json.dumps({'cpu':flavor.cpu, 'ram':flavor.ram, 'hdd':flavor.hdd}))
        if name == 'image':
            image = get_object_or_404(Image, id=obj_id)
            print image.username, image.password
            return HttpResponse(json.dumps({'username':image.username, 'password' : image.password}))

def download_keypair(request):
    slice_obj = get_object_or_404(Slice, id=request.POST.get("slice_id"))
    sshkey = SSHKey.objects.get(slice=slice_obj)
    response = HttpResponse(sshkey.private_key, content_type='plain/text')
    response['Content-Disposition'] = 'attachment; filename="id_rsa"'
    return response

def can_create_vm(request, sliceid):
    slice = get_object_or_404(Slice, id=sliceid)
    vms_num = slice.get_common_vms().count()
    if vms_num < slice.vm_num:
        return HttpResponse(json.dumps({'result': '0'}))
    else:
        return HttpResponse(json.dumps({'result': '1'}))
