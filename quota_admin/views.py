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

@login_required
def index(request):
    QUOTAS = settings.QUOTAS
    context = {}
    context['quotas'] = QUOTAS
    if request.method == 'POST':
        form = ApplyForm(request.POST)
        context['form'] = form
        if form.is_valid():
            resources = {'project': None, 'slice': None, 'vm': None, 'cpu': None, 'mem': None, 'disk': None}
            for resource in resources.keys():
                quota = form.cleaned_data.get(resource)
                resources[resource] = quota
            desc = u"申请配额：项目个数-{project}，虚网个数-{slice}，虚拟机个数-{vm}，CPU个数-{cpu}，内存-{mem}MB，磁盘容量-{disk}G。申请理由：".format(**resources)
            desc += form.cleaned_data.get('description')
            admins = User.objects.filter(is_superuser=True)
            if len(admins) > 0:
                admin = admins[0]
                notify.send(request.user, recipient=admin, verb=u'申请升级配额', action_object=request.user.get_profile(),
                    description=desc)
            return redirect('quota_admin_quota')

    return render(request, 'quota_admin/apply_expanding_quota.html', context)

@login_required
def quota(request):
    if request.user.is_superuser:
        return redirect('/')
    context = {}
    return render(request, 'quota_admin/user_quota.html', context)
