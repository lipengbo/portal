#coding: utf-8

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
from django.db.models import get_model
from django.forms.models import modelform_factory
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.contrib.auth.models import Permission
from django.conf import settings



from nexus.templatetags.nexus_tags import get_fields
from nexus.forms import BaseForm
from project.models import City, Island
from profiles.forms import UserForm
from resources.models import Server
import django_filters
from notifications import notify


@login_required
@staff_member_required
def index(request):
    context = {}
    return render(request, 'nexus/index.html', context)

@login_required
@staff_member_required
def list_objects(request, app_label, model_class):
    if request.method == 'POST':
        action_name = request.POST.get('action')
        if action_name == 'delete':
            delete_action(request, app_label, model_class)
    context = {}
    ModelClass = get_model(app_label, model_class, False)
    class NexusFilter(django_filters.FilterSet):
        class Meta:
            model = ModelClass
            if model_class == 'island':
                fields = []
            elif model_class == 'user':
                fields = []
            else:
                fields = ['island__city', 'island']
    objects = ModelClass.objects.order_by('-id')
    if model_class == 'switch':
        objects = objects.exclude(dpid__istartswith='00:ff')
    if model_class == 'user':
        objects = objects.exclude(is_superuser=True).exclude(id=settings.ANONYMOUS_USER_ID)
    objects = NexusFilter(request.GET, queryset=objects.order_by('-id'))
    cities = City.objects.all()
    islands = Island.objects.all()
    context['cities'] = cities
    context['islands'] = islands
    context['objects'] = objects
    context['app_label'] = app_label
    context['ModelClass'] = ModelClass
    city_id = request.GET.get('island__city')
    island_id = request.GET.get('island')
    if island_id:
        island = Island.objects.get(id=island_id)
        context['current_island'] = island
    if city_id:
        city = City.objects.get(id=city_id)
        context['current_city'] = city
    return render(request, 'nexus/list.html', context)

def get_islands(request):
    city_id = request.GET.get('city_id')
    islands = Island.objects.filter(city__id=city_id)
    html = '<option value="">---------</option>'
    for island in islands:
        html += '<option value="' + str(island.id) + '">' + island.name + '</option>'
    return HttpResponse(html)

@login_required
@transaction.commit_on_success
@staff_member_required
def add_or_edit(request, app_label, model_class, id=None):
    context = {}
    Model = get_model(app_label, model_class, False)
    context['ModelClass'] = Model
    context['app_label'] = app_label
    fields = get_fields(Model, True)
    BaseModelForm = BaseForm
    if model_class == 'user':
        BaseModelForm = UserForm
        ModelForm = modelform_factory(Model, form=BaseModelForm)
    else:
        ModelForm = modelform_factory(Model, fields=tuple(fields), form=BaseModelForm)
    if id:
        instance = get_object_or_404(Model, id=id)
    else:
        instance = None
    if request.method == 'GET':
        defaults = {}
        for k, v in request.GET.items():
            if isinstance(v, list):
                defaults[k] = v[0]
            else:
                defaults[k] = v
        context['formset'] = ModelForm(instance=instance, initial=defaults)
    else:
        formset = ModelForm(request.POST, instance=instance)
        #: quota perm
        if model_class == 'user':
            resources = {'project': None, 'slice': None, 'vm': None, 'cpu': None, 'mem': None, 'disk': None}
            quota_changed = False
            for resource in resources.keys():
                quota = request.POST.get(resource)
                if not quota or quota == u'None':
                    quota = 0
                if int(quota) != getattr(instance.quotas, resource):
                    quota_changed = True
                    instance.user_permissions.remove(*list(Permission.objects.filter(codename__contains='quota_{}_'.format(resource))))
                    if not quota:
                        quota = settings.QUOTAS[resource][0]
                    instance.user_permissions.add(Permission.objects.get(codename='quota_{}_{}'.format(resource, quota)))
            if quota_changed:
                notify.send(request.user, recipient=instance, verb=u'调整配额', action_object=instance.get_profile())
        #: save
        if formset.is_valid():
                instances = formset.save()
                return redirect('nexus_list', app_label=app_label, model_class=model_class)
                transaction.rollback()
        context['formset'] = formset
    return render(request, 'nexus/add.html', context)

@login_required
@staff_member_required
def delete_action(request, app_label, model_class, id=None):
    Model = get_model(app_label, model_class, False)
    if request.method == 'POST':
        ids = request.POST.getlist('id')
        Model.objects.filter(id__in=ids).delete()
    else:
        if id:
            instance = get_object_or_404(Model, id=id)
            instance.delete()
    redirect_url = request.GET.get('next')
    if redirect_url:
        return redirect(redirect_url)
    return redirect('nexus_list', app_label=app_label, model_class=model_class)

def get_servers(request):
    island_id = request.GET.get('island_id')
    servers = Server.objects.filter(island__id=island_id)
    html = ''
    for server in servers:
        html += '<option value="' + str(server.id) + '">' + server.name + '</option>'
    return HttpResponse(html)
