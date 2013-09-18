# coding:utf-8
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.db import transaction, IntegrityError
from django.http import HttpResponse, HttpResponseRedirect,Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.template import RequestContext
from django.utils.translation import ugettext, ugettext as _
from slice.slice_api import create_slice_api, start_slice_api, stop_slice_api, get_slice_topology, delete_slice_api
from plugins.openflow.controller_api import slice_add_controller
from plugins.openflow.flowvisor_api import flowvisor_add_slice
from plugins.openflow.models import Controller
from resources.ovs_api import slice_add_ovs_ports
from project.models import Project, Island
import simplejson

from slice.models import Slice
# Create your views here.


def index(request):
    context = {}
    return render(request, 'slice/index.html', context)


def create(request):
    """创建slice。"""
    context = {}
    if request.method == 'POST':
        slice_id = 1
        return HttpResponseRedirect(
            reverse('ccf.slice.views.slice_detail', args=(slice_id)))
    return render(request, 'slice/create_slice.html', context)


def edit(request, slice_id):
    """编辑slice。"""
    context = {}
    if request.method == 'POST':
        return HttpResponseRedirect(
            reverse('ccf.slice.views.slice_detail', args=(slice_id)))
    return render(request, 'slice/edit_slice.html', context)


def detail(request, slice_id):
    """编辑slice。"""
    context = {}
    if request.method == 'POST':
        return HttpResponseRedirect(
            reverse('ccf.slice.views.slice_detail', args=(slice_id)))
    return render(request, 'slice/slice_detail.html', context)


def delete(request, slice_id):
    """删除slice。"""
    try:
        slice_obj = Slice.objects.get(id=slice_id)
    except Slice.DoesNotExist:
        return HttpResponseRedirect(
            reverse("warning", kwargs={"warn_id": 2}))
    project_id = slice_obj.project.id
    try:
        delete_slice_api(slice_obj)
    except:
        return HttpResponseRedirect(
            reverse("warning", kwargs={"warn_id": 2}))
    return HttpResponseRedirect(
        reverse("project_detail", kwargs={"project_id": project_id}))


def start_or_stop(request, slice_id, flag):
    """启动或停止slice。"""
    try:
        slice_obj = Slice.objects.get(id=slice_id)
    except Slice.DoesNotExist:
        return HttpResponseRedirect(
            reverse("warning", kwargs={"warn_id": 2}))
    try:
        if int(flag) == 1:
            start_slice_api(slice_obj)
        else:
            stop_slice_api(slice_obj)
    except:
        return HttpResponseRedirect(
            reverse("warning", kwargs={"warn_id": 2}))
    else:
        return HttpResponseRedirect(
            reverse('ccf.slice.views.slice_detail', args=(slice_id, 1)))


def topology(request, slice_id):
    """ajax获取slice拓扑信息。"""
    try:
        slice_obj = Slice.objects.get(id=slice_id)
    except:
        return HttpResponseRedirect(
            reverse("warning", kwargs={"warn_id": 2}))
    jsondatas = get_slice_topology(slice_obj)
    result = simplejson.dumps(jsondatas)
    return HttpResponse(result, mimetype='text/plain')


def create_or_edit(request, slice_id):
    """创建slice。"""
    user = request.user
    context = {}
    project = Project.objects.all()[0]
    if request.method == 'GET':
        pass
    else:
        name = request.POST.get("name")
        description = request.POST.get("description")
        island_id = request.POST.get("island_id")
        island = Island.objects.get(id=int(island_id))
        controller = Controller(ip="192.168.5.41", port="8081",
                http_port="8080", username="test", password="test",
                hostname="test_contoller", island=island)
        controller.save()
        controller_type = request.POST.get("controller_type")
        if controller_type == 'default_create':
            controller = Controller.objects.all()[0]
        else:
            controller = Controller.objects.all()[0]
        ovs_ids = request.POST.getlist("ovs_ids")
        ovs_ports = []
        if ovs_ids:
            for ovs_id in ovs_ids:
                ports = request.POST.getlist("ovs" + ovs_id + "ports")
                if ports:
                    ovs = None
                    ovs_port = {'ovs': ovs, 'ports': ports}
                    ovs_ports.append(ovs_port)
        try:
            slice_obj = create_slice_api(project, name, description, island, user)
            slice_add_ovs_ports(slice_obj, ovs_ports)
            slice_add_controller(slice_obj, controller)
            flowvisor_add_slice(island.flowvisor_set.all()[0], controller, name, user.email)
        except:
            pass
#             return redirect('slice_create')
    islands = project.islands.all()
    context['islands'] = islands
    context['ovs_ports'] = [{'ovs':{'id':1, 'hostname':'ovs1'}, 'ports':[1, 2, 3]},
                            {'ovs':{'id':2, 'hostname':'ovs2'}, 'ports':[1, 2]}]
    return render(request, 'slice/create_slice.html', context)
