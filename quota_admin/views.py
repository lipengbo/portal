#coding:utf-8

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
from django.conf import settings

from quota_admin.forms import ApplyForm
from notifications import notify

def index(request):
    QUOATS = settings.QUOTAS
    context = {}
    context['quotas'] = QUOTAS
    if request.method == 'POST':
        form = ApplyForm(request.POST)
        if form.is_valid():
            resources = {'project': None, 'slice': None, 'vm': None, 'cpu': None, 'mem': None, 'disk': None}
            for resource in resources.keys():
                quota = form.cleaned_data.get(resource)
                resources[resource] = quota
            desc = "申请配额：项目个数-{project}，虚网个数-{slice}，虚拟机个数-{vm}，CPU个数-{cpu}，内存-{mem}MB，磁盘容量-{disk}G".format(resources)
            admins = User.objects.filter(is_superuser=True)
            if len(admins) > 0:
                admin = admins[0]
                notify.send(request.user, recipient=admin, verb='申请升级配额', action_object=request.user.get_profile(),
                    description=desc)

    return render(request, 'quota_admin/index.html', context)

