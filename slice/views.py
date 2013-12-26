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
    get_slice_links_bandwidths, get_count_show_data
from plugins.openflow.controller_api import slice_change_controller
from project.models import Project, Island
from resources.models import SwitchPort
from slice.slice_exception import *
from plugins.ipam.models import IPUsage, Subnet
from plugins.common import utils
from guardian.shortcuts import assign_perm, remove_perm, get_perms

from slice.models import Slice, SliceDeleted

from plugins.vt.forms import VmForm
import datetime


@login_required
def create(request, proj_id):
    """创建slice。"""
    project = get_object_or_404(Project, id=proj_id)
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
    vm_form = VmForm()
    context = {}
    context['project'] = project
    context['islands'] = islands
    context['ovs_ports'] = ovs_ports
    context['error_info'] = error_info
    context['vm_form'] = vm_form
#     uuid = utils.gen_uuid()
#     context['uuid'] = ''.join(uuid.split('-'))
    return render(request, 'slice/create_slice.html', context)


@login_required
def create_first(request, proj_id):
    """创建slice不含虚拟机创建。"""
    project = get_object_or_404(Project, id=proj_id)
    if request.method == 'POST':
        try:
            user = request.user
            slice_uuid = request.POST.get("slice_uuid")
            slice_name = request.POST.get("slice_name")
            slice_description = request.POST.get("slice_description")
            island_id = request.POST.get("island_id")
            island = get_object_or_404(Island, id=island_id)
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
            port_ids = []
            switch_port_ids_str = request.POST.get("switch_port_ids")
#             print switch_port_ids_str
            switch_port_ids = switch_port_ids_str.split(',')
            for switch_port_id in switch_port_ids:
                port_ids.append(int(switch_port_id))
            ovs_ports = SwitchPort.objects.filter(id__in=port_ids)
            slice_nw = request.POST.get("slice_nw")
            gw_host_id = request.POST.get("gw_host_id")
            gw_ip = request.POST.get("gw_ip")
            dhcp_selected = request.POST.get("dhcp_selected")
            slice_obj = create_slice_step(project, slice_uuid, slice_name,
                                          slice_description, island, user,
                                          ovs_ports, controller_info, slice_nw,
                                          gw_host_id, gw_ip, dhcp_selected)
        except Exception, ex:
            jsondatas = {'result': 0, 'error_info': ex.message}
        else:
            assign_perm("slice.change_slice", user, slice_obj)
            assign_perm("slice.view_slice", user, slice_obj)
            assign_perm("slice.delete_slice", user, slice_obj)
            jsondatas = {'result': 1, 'slice_id': slice_obj.id}
        result = json.dumps(jsondatas)
        return HttpResponse(result, mimetype='text/plain')


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
                slice_objs = SliceDeleted.objects.all()
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
    slice_obj = get_object_or_404(Slice, id=slice_id)
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


@login_required
def edit_controller(request, slice_id):
    """编辑slice控制器。"""
    print "edit_controller"
    slice_obj = get_object_or_404(Slice, id=slice_id)
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
        slice_change_controller(slice_obj, controller_info)
    except Exception, ex:
        return HttpResponse(json.dumps({'result': 0, 'error_info': ex.message}))
    else:
        controller = slice_obj.get_controller()
        if controller.host:
            return HttpResponse(json.dumps({'result': 1,
                                            'controller': {'name': controller.name, 'ip': controller.ip,
                                                          'port': controller.port, 'server_ip': controller.host.server.ip,
                                                          'host_state': controller.host.state, 'host_id': controller.host.id,
                                                          'host_uuid': controller.host.uuid}}))
        else:
            return HttpResponse(json.dumps({'result': 2,
                                            'controller': {'name': controller.name, 'ip': controller.ip,
                                                          'port': controller.port}}))
#             messages.add_message(request, messages.ERROR, ex)
#     return HttpResponseRedirect(
#         reverse("slice_detail", kwargs={"slice_id": slice_obj.id}))


@login_required
def detail(request, slice_id):
    """编辑slice。"""
    print "slice_detail"
    slice_obj = get_object_or_404(Slice, id=slice_id)
    user = request.user
    context = {}
    if user.is_superuser:
        context['extent_html'] = "admin_base.html"
    else:
        context['extent_html'] = "site_base.html"
        if user.has_perm('slice.change_slice', slice_obj):
            context['permission'] = "edit"
        else:
            if user.has_perm('slice.view_slice', slice_obj):
                context['permission'] = "view"
            else:
                return redirect('forbidden')
    context['slice_obj'] = slice_obj
    context['island'] = slice_obj.get_island()
    context['controller'] = slice_obj.get_controller()
    context['flowvisor'] = slice_obj.get_flowvisor()
    context['gw'] = slice_obj.get_gw()
    context['dhcp'] = slice_obj.get_dhcp()
    context['vms'] = slice_obj.get_common_vms()
    print "get slice subnet"
    subnet = get_object_or_404(Subnet, owner=slice_obj.uuid)
    context['start_ip'] = subnet.get_ip_range()[0]
    context['end_ip'] = subnet.get_ip_range()[1]
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
        slice_deleted = SliceDeleted(name = slice_obj.name,
            show_name = slice_obj.show_name,
            owner_name = slice_obj.owner.username,
            description = slice_obj.description,
            project_name = slice_obj.project.name,
            date_created = slice_obj.date_created,
            date_expired = slice_obj.date_expired)
        if request.user.is_superuser:
            slice_deleted.type = 1
        else:
            slice_deleted.type = 0
        slice_obj.delete()
    except Exception, ex:
        pass
#             if request.user.is_superuser:
#                 messages.add_message(request, messages.ERROR, ex)
    else:
        slice_deleted.save()
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
        nw_objs = Subnet.objects.filter(owner=owner)
        if owner == '0':
            for i in range(10):
                if nw_objs:
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
    if int(context['slice_id']) == 0:
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
    print "------------------------------------========================================="
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
