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
    get_slice_links_bandwidths, get_count_show_data, slice_edit_controller,\
    slice_edit_gw, get_slice_topology_edit, slice_edit_topology, get_island_topology
from slice.models import Slice, SliceDeleted
from project.models import Project, Island
from resources.models import Switch, SwitchPort, SlicePort, OwnerDevice
from resources.ovs_api import slice_delete_port_device
from plugins.ipam.models import IPUsage, Subnet
from plugins.common import utils
from plugins.vt.models import VirtualMachine, Flavor
from plugins.common import glance
from etc.config import function_test
from adminlog.models import log, SUCCESS, FAIL
from slice.slice_exception import DeleteSwitchError

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
    if not project.check_project_slice_quota():
        print "fail+++++++++++++++++++++++++++++"
        messages.add_message(request, messages.INFO, "您的虚网个数已经超过配额")
        return HttpResponseRedirect(
                                    reverse("project_detail", kwargs={"id": project.id}))
    error_info = None
    islands = project.islands.all()
    if not islands:
        return render(request, 'slice/warning.html',
                      {'info': '无可用节点，无法创建slice！'})
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
    context['slice_type'] = "mixslice"
    return render(request, 'slice/create_slice.html', context)


@login_required
def create_first(request, proj_id):
    """创建slice不含虚拟机创建。"""
    project = get_object_or_404(Project, id=proj_id)
    user = request.user
    slice_count = request.user.slice_set.filter(type=0).count()
    if request.user.quotas.slice <= slice_count:
        messages.add_message(request, messages.INFO, "您的虚网个数已经超过配额")
        return redirect('quota_admin_apply')
    if not project.check_project_slice_quota():
        print "fail+++++++++++++++++++++++++++++"
        log(user,  None, "创建虚网", result_code=FAIL)
        jsondatas = {'result': 0, 'error_info': "您的虚网个数已经超过配额！"}
        result = json.dumps(jsondatas)
        return HttpResponse(result, mimetype='text/plain')
    if request.method == 'POST':
        try:
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
                                          ovs_or_ports, slice_nw, tp_mod,
                                          vm_num)
        except Exception, ex:
            log(user,  None, "创建虚网", result_code=FAIL)
            jsondatas = {'result': 0, 'error_info': ex.message}
        else:
            log(user,  slice_obj, u"创建虚网", result_code=SUCCESS)
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
    if slice_obj.state != 0:
        return HttpResponse(json.dumps({'result': 3, 'error_info': u"请确保虚网已停止！"}))
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
    if slice_obj.get_controller():
        op = "edit"
    else:
        op = "create"
    try:
        slice_edit_controller(slice_obj, controller_info)
    except Exception, ex:
#         import traceback
#         traceback.print_exc()
        if op == "edit":
            pass
#             log(request.user, slice_obj.get_controller(), u"编辑控制器", result_code=FAIL)
        else:
            log(request.user, None, u"创建控制器", result_code=FAIL)
        return HttpResponse(json.dumps({'result': 0, 'error_info': ex.message}))
    else:
        if op == "edit":
            pass
#             log(request.user, slice_obj.get_controller(), u"编辑控制器", result_code=SUCCESS)
        else:
            log(request.user, slice_obj.get_controller(), u"创建控制器", result_code=SUCCESS)
        return HttpResponse(json.dumps({'result': 1}))


@login_required
def create_gw(request, slice_id):
    """创建slice网关。"""
    print "create_gw"
    slice_obj = get_object_or_404(Slice, id=slice_id)
    if not request.user.has_perm('slice.change_slice', slice_obj):
        return redirect('forbidden')
    if slice_obj.state != 0:
        return HttpResponse(json.dumps({'result': 3, 'error_info': u"请确保虚网已停止！"}))
    try:
        gw_host_id = request.POST.get("gw_host_id")
        gw_ip = request.POST.get("gw_ip")
        dhcp_selected = request.POST.get("dhcp_selected")
        slice_edit_gw(slice_obj, gw_host_id, gw_ip, dhcp_selected)
    except Exception, ex:
        #import traceback
        #traceback.print_exc()
        log(request.user, None, u"创建网关", result_code=FAIL)
        return HttpResponse(json.dumps({'result': 0, 'error_info': ex.message}))
    else:
        log(request.user, slice_obj.get_gw(), u"创建网关", result_code=SUCCESS)
        return HttpResponse(json.dumps({'result': 1}))


@login_required
def slice_list(request, proj_id, stype):
    """显示所有slice。"""
    from common.models import Counter, FailedCounter, DeletedCounter
    user = request.user
    context = {}
    if user.is_superuser:
        context['extent_html'] = "admin_base.html"
        if int(proj_id) == 0:
            ct_type = int(stype)
            if ct_type == 0 or ct_type == 1:
                slice_objs = Slice.objects.filter(type=ct_type)
            else:
                slice_objs = SliceDeleted.objects.order_by('-id')
            context['type'] = ct_type
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
        context['isajax'] = 1
        return render(request, 'slice/list_page.html', context)
    context['isajax'] = 0
    return render(request, 'slice/slice_list.html', context)


@login_required
def edit_description(request, slice_id):
    """编辑slice描述信息。"""
    print "edit_description"
    slice_obj = get_object_or_404(Slice, id=slice_id)
    if not request.user.has_perm('slice.change_slice', slice_obj):
        return redirect('forbidden')
    slice_description = request.POST.get("slice_description")
    try:
        slice_change_description(slice_obj, slice_description)
    except Exception, ex:
#         log(request.user,  slice_obj, u"编辑虚网", result_code=FAIL)
        return HttpResponse(json.dumps({'result': 0}))
    else:
#         log(request.user,  slice_obj, u"编辑虚网", result_code=SUCCESS)
        return HttpResponse(json.dumps({'result': 1}))


@login_required
def edit_slice(request, slice_id):
    """编辑slice。"""
    print "edit_slice"
    slice_obj = get_object_or_404(Slice, id=slice_id)
    if not request.user.has_perm('slice.change_slice', slice_obj):
        return redirect('forbidden')
    if request.method == 'POST':
        slice_description = request.POST.get("slice_description")
        switch_dpids = request.POST.get("switch_dpids")
        island = slice_obj.get_island()
        switch_dpids_list = switch_dpids.split(",")
        switches = []
        for switch_dpid in switch_dpids_list:
            switch_obj = Switch.objects.filter(dpid=switch_dpid, island=island)
            if switch_obj and (switch_obj[0] not in switches):
                switches.append(switch_obj[0])
        try:
            slice_change_description(slice_obj, slice_description)
            slice_edit_topology(slice_obj, switches)
        except DeleteSwitchError, ex:
            print 1
            return HttpResponse(json.dumps({'result': 2, 'error_info': str(ex)}))
        except Exception, ex:
            print 2
            return HttpResponse(json.dumps({'result': 0, 'error_info': str(ex)}))
        else:
            print 3
            return HttpResponse(json.dumps({'result': 1}))
    else:
        context = {}
        context['slice_obj'] = slice_obj
        try:
            Subnet.objects.get(owner=slice_obj.uuid)
        except:
            context['slice_type'] = "baseslice"
        else:
            context['slice_type'] = "mixslice"
        return render(request, 'slice/edit_slice.html', context)


@login_required
def detail(request, slice_id, div_name=None):
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
    for vm in vms:
        if vm.enable_dhcp:
            show_vms.append({'id': vm.id, 'name': vm.name, 'uuid': vm.uuid,
                             'type_id': 4, 'type': "虚拟机(DHCP)", 'ip': vm.ip,
                             'host_ip': vm.server.ip, 'state': vm.state,
                             'dhcp': "有"})
        else:
            show_vms.append({'id': vm.id, 'name': vm.name, 'uuid': vm.uuid,
                             'type_id': 4, 'type': "虚拟机", 'ip': vm.ip,
                             'host_ip': vm.server.ip, 'state': vm.state,
                             'dhcp': "无"})
    ct_sys_names = []
    ct_syss, has_more = glance.image_list_detailed()
    for ct_sys in ct_syss:
        image_type = ct_sys.properties['image_type']
        if image_type == '0':
            ct_sys_names.append(ct_sys.name)
    if ct_sys_names == []:
        context['ct_sys_names'] = ['---------']
    else:
        context['ct_sys_names'] = ct_sys_names
    context['vms'] = show_vms
    context['flavors'] = Flavor.objects.all()
    context['flowvisor'] = slice_obj.get_virttool()
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
        ip_range = subnet.get_ip_range(slice_obj.vm_num)
        context['vm_start_ip'] = ip_range[0]
        context['vm_end_ip'] = ip_range[1]
        context['device_start_ip'] = ip_range[2]
        context['device_end_ip'] = ip_range[3]
        context['start_ip'] = ip_range[4]
        context['end_ip'] = ip_range[5]
    context['div_name'] = 'list_fw'
    if div_name != None:
        if int(div_name) == 0:
            context['div_name'] = 'list_fw'
        if int(div_name) == 1:
            context['div_name'] = 'list_vm'
        if int(div_name) == 2:
            context['div_name'] = 'list_port'
    if request.is_ajax():
        if 'div_name' in request.GET:
            div_name_a = request.GET.get('div_name')
            if div_name_a == 'list_fw':
                return render(request, 'slice/fw_list_page.html', context)
            if div_name_a == 'list_vm':
                return render(request, 'slice/vm_list_page.html', context)
            if div_name_a == 'list_port':
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
        ret = slice_obj.delete(user=request.user)
    except:
        ret = False
        log(user, slice_obj, u"删除虚网", result_code=FAIL)
        messages.add_message(request, messages.ERROR, "虚网删除失败！")
    else:
        if request.user.is_superuser and not ret:
            log(user, slice_obj, u"删除虚网", result_code=FAIL)
        else:
            log(user, slice_obj, u"删除虚网", result_code=SUCCESS)
#     if ret:
#         log(user, slice_obj, u"删除虚网", result_code=SUCCESS)
#     else:
#         log(user, slice_obj, u"删除虚网", result_code=FAIL)
#     log(user, slice_obj, u"删除虚网", result_code=SUCCESS)
    if 'next' in request.GET:
        if 'type' in request.GET:
            return redirect(request.GET.get('next') + "?type=" + request.GET.get('type'))
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
            start_slice_api(slice_obj, request.user)
        else:
            stop_slice_api(slice_obj, request.user)
    except Exception, ex:
        return HttpResponse(json.dumps({'value': 0, 'error_info': str(ex)}))
    return HttpResponse(json.dumps({'value': 1}))


def topology(request, slice_id):
    """ajax获取slice拓扑信息。"""
    slice_obj = get_object_or_404(Slice, id=slice_id)
    jsondatas = get_slice_topology(slice_obj)
    result = json.dumps(jsondatas)
    return HttpResponse(result, mimetype='text/plain')


def topology_edit(request, slice_id):
    """ajax获取slice拓扑信息。"""
    if int(slice_id) != 0:
        slice_obj = get_object_or_404(Slice, id=slice_id)
        jsondatas = get_slice_topology_edit(slice_obj)
    else:
        island_id = request.GET.get('island_id')
        island_obj = get_object_or_404(Island, id=island_id)
        jsondatas = get_island_topology(island_obj)
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
        print nw_num
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
    except Exception:
        import traceback
        traceback.print_exc()
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


def topology_d3_edit(request):
    """拓扑测试"""
    context = {}
    context['slice_id'] = request.GET.get('slice_id')
    context['island_id'] = request.GET.get('island_id')
    context['height'] = request.GET.get('height')
    return render(request, 'slice/slice_topology_edit.html', context)


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
    ct_type = request.GET.get('type')
    total_num = request.GET.get('total_num')
    stype = request.GET.get('stype')
    try:
        slice_count_show = get_count_show_data(target, ct_type, total_num, stype)
    except Exception:
        return HttpResponse(json.dumps({'result': 0}))
    else:
        return HttpResponse(json.dumps({'result': 1,
                            'show_dates': slice_count_show["show_dates"],
                            'show_nums': slice_count_show["show_nums"]}))


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
        try:
            subnet = Subnet.objects.get(owner=slice_obj.uuid)
        except:
            if controller:
                c_state = 1
            g_state = 1
        else:
            if controller and controller.host:
                c_state = controller.host.state
            else:
                if controller:
                    c_state = 1
            gw = slice_obj.get_gw()
            if gw:
                g_state = gw.state
            else:
                g_state = 1
    except:
        return HttpResponse(json.dumps({'value': 1}))
    else:
        return HttpResponse(json.dumps({'value': 0, 'state': slice_obj.state,
                            'c_state': c_state, 'g_state': g_state}))


def get_vpn_state(request, slice_id):
    slice_obj = get_object_or_404(Slice, id=slice_id)
    return HttpResponse(json.dumps({'vpn_state': slice_obj.vpn_state}))


def list_own_devices(slice_id):
    own_devices = []
    slice_obj = get_object_or_404(Slice, id=slice_id)
    slice_ports = SlicePort.objects.filter(slice=slice_obj)
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
            owner_device = OwnerDevice.objects.filter(slice_port=port)
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


def delete_switch_port(request, slice_id, portid):
    try:
        slice_obj = get_object_or_404(Slice, id=slice_id)
        switch_port = SwitchPort.objects.get(id=portid)
        slice_delete_port_device(slice_obj, portid)
        log(request.user, switch_port, u"删除端口", SUCCESS)
        return HttpResponse(json.dumps({'result':'0'}))
    except:
        log(request.user, switch_port, u"删除端口", FAIL)
        return HttpResponse(json.dumps({'result':'1'}))


def get_select_server(request, slice_id):
    print "get_select_server"
    slice_obj = get_object_or_404(Slice, id=slice_id)
    servers = []
    try:
        server_objs = slice_obj.get_servers()
        for server_obj in server_objs:
            servers.append({'id': server_obj.id, 'name': server_obj.name})
    except:
        servers = []
    return HttpResponse(json.dumps(servers))


def start_or_stop_vpn(request, slice_id, island_id, flag):
    vm = None
    try:
        slice_obj = get_object_or_404(Slice, id=slice_id)
        island = get_object_or_404(Island, id=island_id)
        vm = VirtualMachine.objects.get(slice=slice_obj, type=2)
        gw_ip = vm.gateway_public_ip.ipaddr
        subnet = Subnet.objects.get(owner=slice_obj.uuid)
        print flag, "=============:", subnet.netaddr
        from slice.tasks import start_or_stop_vpn
        if int(flag) == 0:
            if function_test:
                slice_obj.vpn_state = 0
                slice_obj.save()
            else:
                slice_obj.vpn_state = 3
                slice_obj.save()
                start_or_stop_vpn.delay(request.user, slice_obj, island.vpn_ip,
                                        subnet.netaddr, gw_ip, 'stop')
        else:
            if function_test:
                slice_obj.vpn_state = 1
                slice_obj.save()
            else:
                slice_obj.vpn_state = 4
                slice_obj.save()
                start_or_stop_vpn.delay(request.user, slice_obj, island.vpn_ip,
                                        subnet.netaddr, gw_ip, 'start')
        return HttpResponse(json.dumps({'result': 0}))
    except:
        if vm == None:
            return HttpResponse(json.dumps({'result': 1,
                                            'error_info': u'请先添加网关！'}))
        return HttpResponse(json.dumps({'result': 1}))


@login_required
def edit_unicom(request, slice_id):
    """编辑虚网间通信关系。"""
    print "edit_unicom"
    slice_obj = get_object_or_404(Slice, id=slice_id)
    if not request.user.has_perm('slice.change_slice', slice_obj):
        return redirect('forbidden')
    unicom_slices = slice_obj.get_unicom_slices()
    if request.method == 'POST':
        add_errors = []
        del_errors = []
        try:
            unicom_slice_ids = request.POST.get("unicom_slice_ids")
            if unicom_slice_ids != "":
                new_unicom_slice_ids = unicom_slice_ids.split(",")
                new_unicom_slices = Slice.objects.filter(id__in=new_unicom_slice_ids)
            else:
                new_unicom_slices = []
            for new_unicom_slice in new_unicom_slices:
                if new_unicom_slice not in unicom_slices:
                    if not slice_obj.add_unicom_slice(new_unicom_slice):
                        add_errors.append(new_unicom_slice)
            for unicom_slice in unicom_slices:
                if unicom_slice not in new_unicom_slices:
                    if not slice_obj.del_unicom_slice(unicom_slice):
                        del_errors.append(unicom_slice)
        except Exception, ex:
#             import traceback
#             traceback.print_exc()
            return HttpResponse(json.dumps({'result': 0, 'error_info': str(ex)}))
        else:
            if add_errors != [] or del_errors != []:
                error_str = ""
                add_error_names = []
                if add_errors:
                    for add_error in add_errors:
                        add_error_names.append(add_error.show_name)
                    error_str = error_str + u"添加虚网（" + ",".join(add_error_names) + u"）通信关系失败！"
                del_error_names = []
                if del_errors:
                    for del_error in del_errors:
                        del_error_names.append(del_error.show_name)
                    error_str = error_str + u"删除虚网（" + ",".join(del_error_names) + u"）通信关系失败！"
                return HttpResponse(json.dumps({'result': 2, 'error_info': error_str}))
            else:
                return HttpResponse(json.dumps({'result': 1}))
    else:
        context = {}
        context['slice_obj'] = slice_obj
        context['can_unicom_slices'] = slice_obj.get_can_unicom_slices()
        context['unicom_slices'] = unicom_slices
        return render(request, 'slice/edit_unicom.html', context)


@login_required
def can_edit_unicom(request, slice_id):
    """编辑虚网间通信关系。"""
    print "can_edit_unicom"
    slice_obj = get_object_or_404(Slice, id=slice_id)
    if not request.user.has_perm('slice.change_slice', slice_obj):
        return redirect('forbidden')
    try:
        if slice_obj.can_edit_unicom():
            return HttpResponse(json.dumps({'result': 1}))
        else:
            return HttpResponse(json.dumps({'result': 2}))
    except:
        return HttpResponse(json.dumps({'result': 0}))
