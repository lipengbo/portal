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

from slice.models import Slice
# Create your views here.

def index(request):
    context = {}
    return render(request, 'slice/index.html', context)


def create(request):
    user = request.user
    context = {}
    if request.method == 'GET':
        pass
    else:
        pass
#             return redirect('slice_create')

    context['islands'] = [{'id':1,'name':'南京'},{'id':2,'name':'北京'}]
    context['ovs_ports'] = [{'ovs':{'id':1, 'hostname':'ovs1'}, 'ports':[1,2,3]},
                            {'ovs':{'id':2, 'hostname':'ovs2'}, 'ports':[1,2]}]
    return render(request, 'slice/create.html', context)