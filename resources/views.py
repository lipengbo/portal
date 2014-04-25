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
from resources.ovs_api import get_select_topology

import json
# Create your views here.


def index(request):
    context = {}
    return render(request, 'resources/index.html', context)


def topology_select(request):
    """ajax获取选择交换机端口的拓扑。"""
    print "topology_select"
    tp_mod = request.POST.get("tp_mod")
    switch_ids = request.POST.get("switch_ids")
    switch_port_ids = request.POST.get("switch_port_ids")
    print tp_mod, switch_ids, switch_port_ids
    jsondatas = get_select_topology(tp_mod, switch_ids, switch_port_ids)
#     print jsondatas
    result = json.dumps(jsondatas)
    return HttpResponse(result, mimetype='text/plain')
