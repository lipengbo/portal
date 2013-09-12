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
from slice_api import create_slice_api
from plugins.openflow.controller_api import slice_add_controller
from plugins.openflow.models import Controller
from project.models import Project, Island

from slice.models import Slice
# Create your views here.

def index(request):
    context = {}
    return render(request, 'slice/index.html', context)


def create_or_edit(request):
    user = request.user
    context = {}
    if request.method == 'GET':
        pass
    else:
        project = Project.objects.all()[0]
        name = request.POST.get("name")
        description = request.POST.get("description")
        island_id = request.POST.get("island_id")
        island = Island.objects.get(id=int(island_id))
        controller_type = request.POST.get("controller_type")
        if controller_type == 'default_create':
            controller = Controller.objects.all()[0]
        ovs_ids = request.POST.getlist("ovs_ids")
        ovs_ports = []
        if ovs_ids:
            for ovs_id in ovs_ids:
                ports = request.POST.getlist("ovs"+ovs_id+"ports")
                if ports:
                    ovs_port = {'ovs_id':int(ovs_id), 'ports':ports}
                    ovs_ports.append(ovs_port)
        slice_obj = create_slice_api(project, name, description, island, user)
        slice_add_controller(slice_obj, controller, island)
#             return redirect('slice_create')

    context['islands'] = [{'id':1,'name':'南京'},{'id':2,'name':'北京'}]
    context['ovs_ports'] = [{'ovs':{'id':1, 'hostname':'ovs1'}, 'ports':[1,2,3]},
                            {'ovs':{'id':2, 'hostname':'ovs2'}, 'ports':[1,2]}]
    return render(request, 'slice/create.html', context)