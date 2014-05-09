# coding:utf-8
import json

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.db import transaction, IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.template import RequestContext
from django.utils.translation import ugettext, ugettext as _
from django.contrib import messages
from django.db.models import Q

from slice.slice_api import create_slice_step, start_slice_api,\
    stop_slice_api, get_slice_topology, slice_change_description,\
    get_slice_links_bandwidths, get_count_show_data, slice_edit_controller, slice_edit_gw
from project.models import Project, Island
from resources.models import Switch, SwitchPort, SlicePort, OwnerDevice
from slice.slice_exception import *
from plugins.ipam.models import IPUsage, Subnet
from plugins.common import utils
from guardian.shortcuts import assign_perm, remove_perm, get_perms
from resources.ovs_api import slice_delete_port_device

from slice.models import Slice, SliceDeleted

from plugins.vt.forms import VmForm
from plugins.vt.models import Flavor
import datetime


@login_required
def create(request, proj_id, flag):
    """创建slice。"""
    project = get_object_or_404(Project, id=proj_id)
    if not request.user.has_perm('project.create_slice', project):
        return redirect('forbidden')
    slice_count = request.user.slice_set.filter(type=0).count()
    if request.user.quotas.slice <= slice_count:
        messages.add_message(request, messages.INFO, "您的虚网个数已经超过配额")
        return redirect('quota_admin_apply')
    error_info = None
    islands = project.islands.all()
    if not islands:
        return render(request, 'slice/warning.html', {'info': '无可用节点，无法创建slice！'})
    ovs_ports = []
    for island in islands:
        switches = island.switch_set.all()
        for switch in switches:
            switch_ports = switch.switchport_set.all()
            if switch_ports:
                ovs_ports.append({'switch_type': switch.type(),
                                  'switch': switch,
                                  'switch_ports': switch_ports})
            else:
                ovs_ports.append({'switch_type': switch.type(),
                                  'switch': switch,
                                  'switch_ports': []})
    context = {}
    context['project'] = project
    context['islands'] = islands
    context['ovs_ports'] = ovs_ports
    context['error_info'] = error_info
    if int(flag) == 0:
        context['slice_type'] = "mixslice"
    else:
        context['slice_type'] = "baseslice"
    return render(request, 'slice/create_slice.html', context)


# @login_required
# def create_n(request, proj_id):
#     """创建slice。"""
#     project = get_object_or_404(Project, id=proj_id)
#     if not request.user.has_perm('project.create_slice', project):
#         return redirect('forbidden')
#     slice_count = request.user.slice_set.filter(type=0).count()
#     if request.user.quotas.slice <= slice_count:
#         messages.add_message(request, messages.INFO, "您的虚网个数已经超过配额")
#         return redirect('quota_admin_apply')
#     error_info = None
#     islands = project.islands.all()
#     if not islands:
#         return render(request, 'slice/warning.html', {'info': '无可用节点，无法创建slice！'})
#     ovs_ports = []
#     for island in islands:
#         switches = island.switch_set.all()
#         for switch in switches:
#             switch_ports = switch.switchport_set.all()
#             if switch_ports:
#                 ovs_ports.append({'switch_type': switch.type(),
#                                   'switch': switch,
#                                   'switch_ports': switch_ports})
#             else:
#                 ovs_ports.append({'switch_type': switch.type(),
#                                   'switch': switch,
#                                   'switch_ports': []})
#     vm_form = VmForm()
#     context = {}
#     context['project'] = project
#     context['islands'] = islands
#     context['ovs_ports'] = ovs_ports
#     context['error_info'] = error_info
#     return render(request, 'slice/create_slice.html', context)


# @login_required
# def create_first(request, proj_id):
#     """创建slice不含虚拟机创建。"""
#     project = get_object_or_404(Project, id=proj_id)
#     slice_count = request.user.slice_set.filter(type=0).count()
#     if request.user.quotas.slice <= slice_count:
#         messages.add_message(request, messages.INFO, "您的虚网个数已经超过配额")
#         return redirect('quota_admin_apply')
#     if request.method == 'POST':
#         try:
#             user = request.user
#             slice_uuid = request.POST.get("slice_uuid")
#             slice_name = request.POST.get("slice_name")
#             slice_description = request.POST.get("slice_description")
#             island_id = request.POST.get("island_id")
#             island = get_object_or_404(Island, id=island_id)
#             controller_type = request.POST.get("controller_type")
#             if controller_type == 'default_create':
#                 controller_sys = request.POST.get("controller_sys")
#                 controller_info = {'controller_type': controller_type,
#                                    'controller_sys': controller_sys}
#             else:
#                 controller_ip = request.POST.get("controller_ip")
#                 controller_port = request.POST.get("controller_port")
#                 controller_info = {'controller_type': controller_type,
#                                    'controller_ip': controller_ip,
#                                    'controller_port': controller_port}
#             tp_mod = request.POST.get('tp_mod')
#             if int(tp_mod) == 2:
#                 switch_ids = []
#                 switch_ids_str = request.POST.get("switch_ids")
#     #             print switch_port_ids_str
#                 switch_ids_sp = switch_ids_str.split(',')
#                 for switch_id_sp in switch_ids_sp:
#                     switch_ids.append(int(switch_id_sp))
#                 ovs_or_ports = Switch.objects.filter(id__in=switch_ids)
#             else:
#                 port_ids = []
#                 switch_port_ids_str = request.POST.get("switch_port_ids")
#     #             print switch_port_ids_str
#                 switch_port_ids = switch_port_ids_str.split(',')
#                 for switch_port_id in switch_port_ids:
#                     port_ids.append(int(switch_port_id))
#                 ovs_or_ports = SwitchPort.objects.filter(id__in=port_ids)
#             slice_nw = request.POST.get("slice_nw")
#             gw_host_id = request.POST.get("gw_host_id")
#             gw_ip = request.POST.get("gw_ip")
#             dhcp_selected = request.POST.get("dhcp_selected")
#             slice_obj = create_slice_step(project, slice_uuid, slice_name,
#                                           slice_description, island, user,
#                                           ovs_or_ports, controller_info, slice_nw,
#                                           gw_host_id, gw_ip, dhcp_selected, tp_mod)
#         except Exception, ex:
#             jsondatas = {'result': 0, 'error_info': ex.message}
#         else:
#             assign_perm("slice.change_slice", user, slice_obj)
#             assign_perm("slice.view_slice", user, slice_obj)
#             assign_perm("slice.delete_slice", user, slice_obj)
#             jsondatas = {'result': 1, 'slice_id': slice_obj.id}
#         result = json.dumps(jsondatas)
#         return HttpResponse(result, mimetype='text/plain')


@login_required
def create_first(request, proj_id):
    """创建slice不含虚拟机创建。"""
    project = get_object_or_404(Project, id=proj_id)
    slice_count = request.user.slice_set.filter(type=0).count()
    if request.user.quotas.slice <= slice_count:
        messages.add_message(request, messages.INFO, "您的虚网个数已经超过配额")
        return redirect('quota_admin_apply')
    if request.method == 'POST':
        try:
            user = request.user
            slice_uuid = request.POST.get("slice_uuid")
            slice_name = request.POST.get("slice_name")
            slice_description = request.POST.get("slice_description")
            island_id = request.POST.get("island_id")
            island = get_object_or_404(Island, id=island_id)
            tp_mod = request.POST.get('tp_mod')
            if int(tp_mod) == 2:
                switch_ids = []
                switch_ids_str = request.POST.get("switch_ids")
    #             print switch_port_ids_str
                switch_ids_sp = switch_ids_str.split(',')
                for switch_id_sp in switch_ids_sp:
                    switch_ids.append(int(switch_id_sp))
                ovs_or_ports = Switch.objects.filter(id__in=switch_ids)
            else:
                port_ids = []
                switch_port_ids_str = request.POST.get("switch_port_ids")
    #             print switch_port_ids_str
                switch_port_ids = switch_port_ids_str.split(',')
                for switch_port_id in switch_port_ids:
                    port_ids.append(int(switch_port_id))
                ovs_or_ports = SwitchPort.objects.filter(id__in=port_ids)
            slice_nw = request.POST.get("slice_nw")
            vm_num = int(request.POST.get("vm_num"))
            slice_obj = create_slice_step(project, slice_uuid, slice_name,
                                          slice_description, island, user,
                                          ovs_or_ports, slice_nw, tp_mod, vm_num)
        except Exception, ex:
            jsondatas = {'result': 0, 'error_info': ex.message}
        else:
            jsondatas = {'result': 1, 'slice_id': slice_obj.id}
        result = json.dumps(jsondatas)
        return HttpResponse(result, mimetype='text/plain')


@login_required
def create_or_edit_controller(request, slice_id):
    """创建或编辑slice控制器。"""
    print "create_or_edit_controller"
    slice_obj = get_object_or_404(Slice, id=slice_id)
    if not request.user.has_perm('slice.change_slice', slice_obj):
        return redirect('forbidden')
    controller_type = request.POST.get("controller_type")
    if controller_type == 'default_create':
        controller_sys = request.POST.get("controller_sys")
        controller_info = {'controller_type': controller_type,
                           'controller_sys': controller_sys}
    else:
        controller_ip = request.POST.get("controller_ip")
        controller_port = request.POST.get("controller_port")
        controller_info = {'controller_type': controller_type,
                           'controller_ip': controller_ip,
                           'controller_port': controller_port}
    try:
        slice_edit_controller(slice_obj, controller_info)
    except Exception, ex:
        import traceback
        traceback.print_exc()
        return HttpResponse(json.dumps({'result': 0, 'error_info': ex.message}))
    else:
        return HttpResponse(json.dumps({'result': 1}))


@login_required
def create_gw(request, slice_id):
    """创建slice网关。"""
    print "create_gw"
    slice_obj = get_object_or_404(Slice, id=slice_id)
    if not request.user.has_perm('slice.change_slice', slice_obj):
        return redirect('forbidden')
    try:
        gw_host_id = request.POST.get("gw_host_id")
        gw_ip = request.POST.get("gw_ip")
        dhcp_selected = request.POST.get("dhcp_selected")
        slice_edit_gw(slice_obj, gw_host_id, gw_ip, dhcp_selected)
    except Exception, ex:
        return HttpResponse(json.dumps({'result': 0, 'error_info': ex.message}))
    else:
        return HttpResponse(json.dumps({'result': 1}))


@login_required
def list(request, proj_id, stype):
    """显示所有slice。"""
    from common.models import Counter, FailedCounter, DeletedCounter
    user = request.user
    context = {}
    if user.is_superuser:
        context['extent_html'] = "admin_base.html"
        if int(proj_id) == 0:
            type = int(stype)
            if type == 0 or type == 1:
                slice_objs = Slice.objects.filter(type=type)
            else:
                slice_objs = SliceDeleted.objects.order_by('-id')
            context['type'] = type
            date_now = datetime.datetime.now()
            if context['type'] == 0:
                sc = Counter.objects.filter(date__year=date_now.strftime('%Y'),
                                            date__month=date_now.strftime('%m'),
                                            date__day=date_now.strftime('%d'),
                                            target=1,
                                            type=2)
                context['total_num'] = Slice.objects.filter(type=0).count
            if context['type'] == 1:
                sc = FailedCounter.objects.filter(date__year=date_now.strftime('%Y'),
                                            date__month=date_now.strftime('%m'),
                                            date__day=date_now.strftime('%d'),
                                            target=1,
                                            type=2)
                context['total_num'] = Slice.objects.filter(type=1).count
            if context['type'] == 2:
                sc = DeletedCounter.objects.filter(date__year=date_now.strftime('%Y'),
                                            date__month=date_now.strftime('%m'),
                                            date__day=date_now.strftime('%d'),
                                            target=1,
                                            type=2)
                context['total_num'] = SliceDeleted.objects.all().count
            if sc:
                num = sc[0].count
            else:
                num = 0
            context['new_num'] = num
        else:
            context['type'] = 0
            project = get_object_or_404(Project, id=proj_id)
            context['project'] = project
            slice_objs = project.slice_set.filter(type=0)
    else:
        context['type'] = 0
        context['extent_html'] = "site_base.html"
        project = get_object_or_404(Project, id=proj_id)
        context['project'] = project
        slice_objs = project.slice_set.filter(type=0)
    if 'query' in request.GET:
        query = request.GET.get('query')
        if query:
            slice_objs = slice_objs.filter(Q(show_name__icontains=query) | Q(description__icontains=query))
            context['query'] = query
    context['slices'] = slice_objs
    if request.is_ajax():
        return render(request, 'slice/list_page.html', context)
    return render(request, 'slice/slice_list.html', context)


@login_required
def edit_description(request, slice_id):
    """编辑slice描述信息。"""
    print "edit_description"
    slice_obj = get_object_or_404(Slice, id=slice_id)
    if not request.user.has_perm('slice.change_slice', slice_obj):
        return redirect('forbidden')
#     if request.method == 'POST':
    slice_description = request.POST.get("slice_description")
    try:
        slice_change_description(slice_obj, slice_description)
    except Exception, ex:
        return HttpResponse(json.dumps({'result': 0}))
    else:
        return HttpResponse(json.dumps({'result': 1}))
#             messages.add_message(request, messages.ERROR, ex)
#     return HttpResponseRedirect(
#         reverse("slice_detail", kwargs={"slice_id": slice_obj.id}))


# @login_required
# def edit_controller(request, slice_id):
#     """编辑slice控制器。"""
#     print "edit_controller"
#     slice_obj = get_object_or_404(Slice, id=slice_id)
#     if not request.user.has_perm('slice.change_slice', slice_obj):
#         return redirect('forbidden')
#     controller_type = request.POST.get("controller_type")
#     if controller_type == 'default_create':
#         controller_sys = request.POST.get("controller_sys")
#         controller_info = {'controller_type': controller_type,
#                            'controller_sys': controller_sys}
#     else:
#         controller_ip = request.POST.get("controller_ip")
#         controller_port = request.POST.get("controller_port")
#         controller_info = {'controller_type': controller_type,
#                            'controller_ip': controller_ip,
#                            'controller_port': controller_port}
#     try:
#         slice_edit_controller(slice_obj, controller_info)
#     except Exception, ex:
#         return HttpResponse(json.dumps({'result': 0, 'error_info': ex.message}))
#     else:
#         controller = slice_obj.get_controller()
#         if controller.host:
#             return HttpResponse(json.dumps({'result': 1,
#                                             'controller': {'name': controller.name, 'ip': controller.ip,
#                                                           'port': controller.port, 'server_ip': controller.host.server.ip,
#                                                           'host_state': controller.host.state, 'host_id': controller.host.id,
#                                                           'host_uuid': controller.host.uuid}}))
#         else:
#             print 2
#             return HttpResponse(json.dumps({'result': 2,
#                                             'controller': {'name': controller.name, 'ip': controller.ip,
#                                                           'port': controller.port}}))


@login_required
def detail(request, slice_id):
    """编辑slice。"""
    print "slice_detail"
#     test_cnvp()
    slice_obj = get_object_or_404(Slice, id=slice_id)
    user = request.user
    context = {}
    if user.is_superuser:
        context['extent_html'] = "admin_base.html"
    else:
        context['extent_html'] = "site_base.html"
        if slice_obj.type == 1:
            raise Http404('Slice has been deleted.')
        if user.has_perm('slice.change_slice', slice_obj):
            context['permission'] = "edit"
        else:
            if user.has_perm('project.create_slice', slice_obj.project):
                context['permission'] = "view"
            else:
                return redirect('forbidden')
    context['slice_obj'] = slice_obj
    context['island'] = slice_obj.get_island()
    controller = slice_obj.get_controller()
    gw = slice_obj.get_gw()
    vms = slice_obj.get_common_vms()
    show_vms = []
#         show_vm = {}
#         if controller.host:
#             show_vm['id'] = controller.host.id
#             show_vm['host_ip'] = controller.host.server.ip
#             show_vm['state'] = controller.host.state
#             show_vm['uuid'] = controller.host.uuid
#             show_vm['type_id'] = 2
#         else:
#             show_vm['id'] = 0
#             show_vm['host_ip'] = ""
#             show_vm['state'] = ""
#             show_vm['uuid'] = ""
#             show_vm['type_id'] = 1
#         if controller.name == 'user_define':
#             show_vm['name'] = "自定义控制器"
#         else:
#             show_vm['name'] = controller.name
#
#         show_vm['type'] = "控制器"
#         show_vm['dhcp'] = "无"
#         show_vm['ip'] = controller.ip + ":" + str(controller.port)
#         show_vms.append(show_vm)
#     if gw:
#         if gw.enable_dhcp:
#             show_vms.append({'id':gw.id, 'name':gw.name, 'uuid':gw.uuid, 'type_id':3,
#                              'type':"虚拟网关", 'ip':gw.ip, 'host_ip':gw.server.ip, 'state':gw.state, 'dhcp':"有"})
#         else:
#             show_vms.append({'id':gw.id, 'name':gw.name, 'uuid':gw.uuid, 'type_id':3,
#                              'type':"虚拟网关", 'ip':gw.ip, 'host_ip':gw.server.ip, 'state':gw.state, 'dhcp':"无"})
    for vm in vms:
        if vm.enable_dhcp:
            show_vms.append({'id':vm.id, 'name':vm.name, 'uuid':vm.uuid, 'type_id':4,
                         'type':"虚拟机(DHCP)", 'ip':vm.ip, 'host_ip':vm.server.ip, 'state':vm.state, 'dhcp':"有"})
        else:
            show_vms.append({'id':vm.id, 'name':vm.name, 'uuid':vm.uuid, 'type_id':4,
                         'type':"虚拟机", 'ip':vm.ip, 'host_ip':vm.server.ip, 'state':vm.state, 'dhcp':"无"})

    context['vms'] = show_vms
    context['flowvisor'] = slice_obj.get_flowvisor()
    context['dhcp'] = slice_obj.get_dhcp()
    context['checkband'] = 0
    context['controller'] = controller
    context['gw'] = gw
    context['devices'] = list_own_devices(slice_id)
    print "get slice subnet"
    try:
        subnet = Subnet.objects.get(owner=slice_obj.uuid)
    except:
        context['slice_type'] = "baseslice"
        context['start_ip'] = ""
        context['end_ip'] = ""
    else:
        context['slice_type'] = "mixslice"
        print "ip range == ", subnet.get_ip_range()
        context['start_ip'] = subnet.get_ip_range()[0]
        context['end_ip'] = subnet.get_ip_range()[1]
    if request.is_ajax():
        print "++++++++++++++++++++++++++ajax"
        if 'div_name' in request.GET:
            div_name = request.GET.get('div_name')
            print "++++++++++++++++++++++++++div_name", div_name
            if div_name == 'list_fw':
                return render(request, 'slice/fw_list_page.html', context)
            if div_name == 'list_vm':
                return render(request, 'slice/vm_list_page.html', context)
            if div_name == 'list_port':
                return render(request, 'slice/port_list_page.html', context)
    return render(request, 'slice/slice_detail.html', context)


@login_required
def delete(request, slice_id):
    """删除slice。"""
    slice_obj = get_object_or_404(Slice, id=slice_id)
    user = request.user
    project_id = slice_obj.project.id
    if not request.user.is_superuser:
        if not user.has_perm('slice.delete_slice', slice_obj):
            return redirect('forbidden')
    try:
        slice_obj.delete(user=request.user)
    except:
        messages.add_message(request, messages.ERROR, "虚网删除失败！")
    if 'next' in request.GET:
        if 'type' in request.GET:
            return redirect(request.GET.get('next')+"?type="+request.GET.get('type'))
        else:
            return redirect(request.GET.get('next'))
    return HttpResponseRedirect(
        reverse("project_detail", kwargs={"id": project_id}))


@login_required
def start_or_stop(request, slice_id, flag):
    """启动或停止slice。"""
    slice_obj = get_object_or_404(Slice, id=slice_id)
    if not request.user.has_perm('slice.change_slice', slice_obj):
        return redirect('forbidden')
    try:
        if int(flag) == 1:
            start_slice_api(slice_obj)
        else:
            stop_slice_api(slice_obj)
    except Exception, ex:
        return HttpResponse(json.dumps({'value': 0, 'error_info': str(ex)}))
#         messages.add_message(request, messages.ERROR, ex)
    return HttpResponse(json.dumps({'value': 1}))
#     return HttpResponseRedirect(
#         reverse("slice_detail", kwargs={"slice_id": slice_obj.id}))


def topology(request, slice_id):
    """ajax获取slice拓扑信息。"""
    slice_obj = get_object_or_404(Slice, id=slice_id)
    jsondatas = get_slice_topology(slice_obj)
    result = json.dumps(jsondatas)
    return HttpResponse(result, mimetype='text/plain')


@login_required
def check_slice_name(request):
    """
    校验用户所填slice名称是否已经存在
    return:
        value:
          slice名称已存在:value = 1
          slice名称不存在：value = 0
    """
    slice_name = request.GET.get('slice_name')
    slice_objs = Slice.objects.filter(name=slice_name)
    if slice_objs:
        return HttpResponse(json.dumps({'value': 1}))
    else:
        return HttpResponse(json.dumps({'value': 0}))


@login_required
def create_nw(request, owner, nw_num):
    """
    分配slice网段
    return:
        value:
          失败:value = 0
          成功：value = 网段（192.168.5.6/27）
    """
    print "create_nw"
    try:
        if owner == '0':
            uuid = utils.gen_uuid()
            owner = ''.join(uuid.split('-'))
            nw_objs = Subnet.objects.filter(owner=owner)
            for i in range(10):
                if nw_objs:
                    print "uuid used"
                    uuid = utils.gen_uuid()
                    owner = ''.join(uuid.split('-'))
                    nw_objs = Subnet.objects.filter(owner=owner)
                else:
                    break
            if nw_objs:
                return HttpResponse(json.dumps({'value': 1}))
        else:
            IPUsage.objects.delete_subnet(owner)
        nw = IPUsage.objects.create_subnet(owner, int(nw_num), 1800)
        if nw:
            return HttpResponse(json.dumps({'value': nw, 'owner': owner}))
        else:
            return HttpResponse(json.dumps({'value': 0}))
    except Exception, ex:
        return HttpResponse(json.dumps({'value': 0}))


@login_required
def delete_nw(request, owner):
    """
    删除slice网段
    return:
        value:
          失败:value = 0
          成功：value = 1
    """
    try:
        if IPUsage.objects.delete_subnet(owner):
            return HttpResponse(json.dumps({'value': 1}))
        else:
            return HttpResponse(json.dumps({'value': 0}))
    except:
        return HttpResponse(json.dumps({'value': 0}))


def get_show_slices(request):
    """ajax获取首页展示slice。"""
    slice_objs = Slice.objects.all()
    slices = []
    for slice_obj in slice_objs:
        slice_show = {'id': slice_obj.id, 'name': slice_obj.get_show_name()}
        slices.append(slice_show)
    return HttpResponse(json.dumps({'slices': slices}))


def topology_test(request, slice_id):
    """拓扑测试"""
    context = {}
    context['slice_id'] = slice_id
    context['width'] = 620
    context['height'] = 300
    return render(request, 'slice/slice_topology.html', context)


def topology_d3(request):
    """拓扑测试"""
    context = {}
    context['slice_id'] = request.GET.get('slice_id')
    context['width'] = request.GET.get('width')
    context['height'] = request.GET.get('height')
    context['top'] = request.GET.get('top')
    context['band'] = request.GET.get('band')
    context['own_device'] = request.GET.get("own_device")
    if int(context['slice_id']) == 0:
        context['tp_mod'] = request.GET.get('tp_mod')
        if int(context['tp_mod']) == 2:
            context['switch_ids'] = request.GET.get('switch_ids')
            context['switch_port_ids'] = ""
        else:
            context['switch_ids'] = ""
            context['switch_port_ids'] = request.GET.get('switch_port_ids')
    user = request.user
    if user and user.is_superuser:
        context['admin'] = 1
    else:
        context['admin'] = 0
    return render(request, 'slice/slice_topology.html', context)


def update_links_bandwidths(request, slice_id):
    print 'update_links_bandwidths'
    switchs_ports = []
    switch_ids = []
    ports = {}
    info = request.POST.get("info")
    maclist = request.POST.get("maclist")
    id_ports = info.split(',')
    maclist = maclist.split(',')
    for id_port in id_ports:
        idport = id_port.split('_')
        if len(idport) > 1:
            if int(idport[0]) in switch_ids:
                if idport[1] not in ports[int(idport[0])]:
                    ports[int(idport[0])].append(idport[1])
            else:
                switch_ids.append(int(idport[0]))
                ports[int(idport[0])] = [idport[1]]
    for switch_id in switch_ids:
        switchs_ports.append({'id': switch_id, 'ports': ports[switch_id]})
    ret = get_slice_links_bandwidths(switchs_ports, maclist)
    result = json.dumps({'bandwidth': ret})
    return HttpResponse(result, mimetype='text/plain')


def countiframe(request):
    print 'countiframe'
    context = {}
    context['target'] = request.GET.get('target')
    context['type'] = request.GET.get('type')
    context['stype'] = request.GET.get('stype')
    return render(request, 'slice/countiframe.html', context)


def get_count_show(request):
    print 'get_count_show'
    target = request.GET.get('target')
    type = request.GET.get('type')
    total_num = request.GET.get('total_num')
    stype = request.GET.get('stype')
    try:
        slice_count_show = get_count_show_data(target, type, total_num, stype)
    except Exception, ex:
        return HttpResponse(json.dumps({'result': 0}))
    else:
        return HttpResponse(json.dumps({'result': 1, 'show_dates': slice_count_show["show_dates"], 'show_nums': slice_count_show["show_nums"]}))


def dhcp_switch(request, slice_id, flag):
    slice_obj = get_object_or_404(Slice, id=slice_id)
    if slice_obj.set_dhcp(flag):
        return HttpResponse(json.dumps({'result': 0}))
    else:
        return HttpResponse(json.dumps({'result': 1}))


@login_required
def get_slice_state(request, slice_id):
    """
    获取slice状态
    return:
        value:
          slice状态获取失败:value = 1
          slice状态获取成功：value = 0
    """
    try:
        c_state = -1
        g_state = -1
        slice_obj = Slice.objects.get(id=int(slice_id))
        controller = slice_obj.get_controller()
        if controller and controller.host:
            c_state = controller.host.state
        gw = slice_obj.get_gw()
        if gw:
            g_state = gw.state
    except:
        print 1
        return HttpResponse(json.dumps({'value': 1}))
    else:
        print 2
        return HttpResponse(json.dumps({'value': 0, 'state': slice_obj.state,
                                        'c_state': c_state, 'g_state': g_state}))

#def list_own_devices(request, slice_id):
def list_own_devices(slice_id):
    own_devices = []
    slice_obj = get_object_or_404(Slice, id=slice_id)
    slice_ports = SlicePort.objects.filter(slice = slice_obj)
    for port in slice_ports:
        port_info = {}
        switch_port = port.switch_port
        if port.type == 0:
            port_info['port_name'] = switch_port.name
            port_info['port'] = switch_port.port
            port_info['port_id'] = switch_port.id
            port_info['port'] = switch_port.port
            port_info['is_monopo'] = 0
            port_info['mac_list'] = ''
            port_info['switch_name'] = switch_port.switch.name
            port_info['dpid'] = switch_port.switch.dpid
            own_devices.append(port_info)
        else:
            owner_device = OwnerDevice.objects.filter(slice_port = port)
            if owner_device.count() > 0:
                port_info['port_name'] = switch_port.name
                port_info['port'] = switch_port.port
                port_info['port_id'] = switch_port.id
                port_info['is_monopo'] = 1
                port_info['mac_list'] = owner_device[0].mac_list
                port_info['switch_name'] = switch_port.switch.name
                port_info['dpid'] = switch_port.switch.dpid
                own_devices.append(port_info)
    print "--------------------------->", own_devices
    return own_devices
   # return HttpResponse(json.dumps(own_devices))

def delete_switch_port(request, slice_id, portid):
    try:
        slice_obj = get_object_or_404(Slice, id=slice_id)
        slice_delete_port_device(slice_obj, portid)
        return HttpResponse(json.dumps({'result':'0'}))
    except:
        return HttpResponse(json.dumps({'result':'1'}))



def get_select_server(request, slice_id):
    print "get_select_server"
    slice_obj = get_object_or_404(Slice, id=slice_id)
    servers = []
    try:
        server_objs = slice_obj.get_servers()
        for server_obj in server_objs:
            servers.append({'id':server_obj.id, 'name':server_obj.name})
    except:
        servers = []
    return HttpResponse(json.dumps(servers))


def test_cnvp():
    from plugins.openflow.flowvisor_api import flowvisor_del_slice,\
        flowvisor_del_flowspace, flowvisor_add_flowspace,\
        flowvisor_update_slice_status, flowvisor_add_slice,\
        flowvisor_del_port, flowvisor_add_port, flowvisor_update_sice_controller,\
        flowvisor_get_switches, flowvisor_get_links, flowvisor_show_slice
    from plugins.openflow.models import Flowvisor, Controller
#     from resources.models import SwitchPort
#     from plugins.vt.models import VirtualMachine
#     vm = VirtualMachine.objects.get(mac='FA:16:0A:00:00:0A')
#     vm.state = 8
#     vm.switch_port = None
#     vm.save()
#     slice = Slice.objects.get(id=1)
#     switch_port = SwitchPort.objects.get(port=678)
#     slice.remove_resource(switch_port)
#     vm.switch_port = switch_port
#     vm.save()
#     print 'vm change ok'
#     slice.add_resource(switch_port)
    print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%test cnvp"
    flowvisor = Flowvisor.objects.all()[0]
    controller = Controller.objects.filter(ip = "172.16.0.5")[0]
    for i in range(0,125):
        try:
            flowvisor_del_slice(flowvisor, "slicet"+str(i))
        except Exception, ex:
            print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%test cnvp flowvisor_del_slice error"
            print ex
    for i in range(0,125):
        try:
            flowvisor_del_slice(flowvisor, "slicet"+str(i))
        except Exception, ex:
            print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%test cnvp flowvisor_del_slice error"
            print ex
#     try:
#         for i in range(125,130):
#             try:
#                 flowvisor_add_slice(flowvisor, "slicet"+str(i), controller, "cjx@qq.com")
#             except Exception, ex:
#                 print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%test cnvp flowvisor_add_slice error"
#                 print ex
#                 raise
#             try:
#                 flowvisor_add_port(flowvisor, "slicet"+str(i), "00:ff:00:00:00:00:00:01", "64500")
#             except Exception, ex:
#                 print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%test cnvp flowvisor_add_port error"
#                 print ex
#                 raise
#             try:
#                 flowvisor_add_port(flowvisor, "slicet"+str(i), "00:ff:00:00:00:00:00:01", "64501")
#             except Exception, ex:
#                 print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%test cnvp flowvisor_add_port error"
#                 print ex
#                 raise
#             try:
#                 flowvisor_add_flowspace(flowvisor, "flcjx", "slicet"+str(i), 4,
#                                     "cjx", "00:ff:00:00:00:00:00:01", 100, "nw_src=11.0.0."+str(i+1)+"),nw_dst=11.0.0."+str(i+1))
#             except Exception, ex:
#                 print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%test cnvp flowvisor_add_flowspace error"
#                 print ex
#                 raise
#             try:
#                 flowvisor_add_flowspace(flowvisor, "flcjx", "slicet"+str(i), 4,
#                                     "cjx", "00:ff:00:00:00:00:00:01", 100, "nw_src=12.0.0."+str(i+1)+"),nw_dst=12.0.0."+str(i+1))
#             except Exception, ex:
#                 print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%test cnvp flowvisor_add_flowspace error"
#                 print ex
#                 raise
#             try:
#                 flowvisor_add_flowspace(flowvisor, "flcjx", "slicet"+str(i), 4,
#                                     "cjx", "00:ff:00:00:00:00:00:01", 100, "nw_src=13.0.0."+str(i+1)+"),nw_dst=13.0.0."+str(i+1))
#             except Exception, ex:
#                 print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%test cnvp flowvisor_add_flowspace error"
#                 print ex
#                 raise
#             try:
#                 flowvisor_update_slice_status(flowvisor, "slicet"+str(i), True)
#             except Exception, ex:
#                 print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%test cnvp start slice error"
#                 print ex
#                 raise
# #             try:
# #                 flowvisor_update_slice_status(flowvisor, "slicet"+str(i), False)
# #             except Exception, ex:
# #                 print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%test cnvp stop slice error"
# #                 print ex
# #                 raise
#     except Exception, ex:
#         pass
#     for i in range(0,125):
#         try:
#             flowvisor_update_slice_status(flowvisor, "slicet"+str(i), True)
#         except Exception, ex:
#             print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%test cnvp stop slice error"
#             print ex
#             raise
#         try:
#             flowvisor_update_slice_status(flowvisor, "slicet"+str(i), False)
#         except Exception, ex:
#             print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%test cnvp stop slice error"
#             print ex
#             raise
#     for i in range(0,125):
#         try:
#             flowvisor_del_slice(flowvisor, "slicet"+str(i))
#         except Exception, ex:
#             print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%test cnvp flowvisor_del_slice error"
#             print ex
#     try:
#         flowvisor_show_slice(flowvisor, None)
#     except Exception, ex:
#         print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%test cnvp flowvisor_show_slice error"
#         print ex
#     controller = Controller.objects.all()[0]
#     try:
#         flowvisor_add_slice(flowvisor, "cjxcnvptest", controller, "cjx@qq.com")
#     except Exception, ex:
#         print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%test cnvp flowvisor_add_slice error"
#         print ex
#     try:
#         flowvisor_add_slice(flowvisor, "cjxcnvptest2", controller, "cjx@qq.com")
#     except Exception, ex:
#         print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%test cnvp flowvisor_add_slice error"
#         print ex
#     try:
#         flowvisor_update_slice_status(flowvisor, "cjxcnvptest", True)
#     except Exception, ex:
#         print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%test cnvp flowvisor_update_slice_status error"
#         print ex
#     try:
#         flowvisor_update_slice_status(flowvisor, "4", True)
#     except Exception, ex:
#         print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%test cnvp flowvisor_update_slice_status error"
#         print ex
#     try:
#         flowvisor_update_sice_controller(flowvisor, "cjxcnvptest", "17.17.17.17", "988")
#     except Exception, ex:
#         print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%test cnvp flowvisor_update_sice_controller error"
#         print ex
#     try:
#         flowvisor_add_port(flowvisor, "cjxcnvptest", "00:00:00:00:00:00:00:01", "2")
#     except Exception, ex:
#         print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%test cnvp flowvisor_add_port error"
#         print ex
#     try:
#         flowvisor_del_port(flowvisor, "cjxcnvptest", None, None)
#     except Exception, ex:
#         print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%test cnvp flowvisor_del_port error"
#         print ex
#     try:
#         flowvisor_add_flowspace(flowvisor, "flcjx", "cjxcnvptest4", 4,
#                             "cjx", "00:00:00:00:00:00:00:09", 100, "nw_src=10.0.0.1/24,nw_dst=10.0.0.1/24")
#     except Exception, ex:
#         print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%test cnvp flowvisor_add_flowspace error"
#         print ex
#     try:
#         flowvisor_del_flowspace(flowvisor, "cjxcnvptest", None)
#     except Exception, ex:
#         print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%test cnvp flowvisor_del_flowspace error"
#         print ex
#     try:
#         flowvisor_del_slice(flowvisor, "cjxcnvptest9")
#     except Exception, ex:
#         print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%test cnvp flowvisor_del_slice error"
#         print ex
#     try:
#         switches = flowvisor_get_switches(flowvisor)
#         print switches
#     except Exception, ex:
#         print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%test cnvp flowvisor_get_switches error"
#         print ex
#     try:
#         links = flowvisor_get_links(flowvisor)
#         print links
#     except Exception, ex:
#         print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%test cnvp flowvisor_get_links error"
#         print ex
