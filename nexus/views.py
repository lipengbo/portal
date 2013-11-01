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

from nexus.templatetags.nexus_tags import get_fields
from nexus.forms import BaseForm
from project.models import City, Island
import django_filters


@login_required
def index(request):
    context = {}
    return render(request, 'nexus/index.html', context)

@login_required
def list_objects(request, app_label, model_class):
    if request.method == 'POST':
        action_name = request.POST.get('action')
        if action_name == 'delete':
            return delete_action(request, app_label, model_class)
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
    objects = NexusFilter(request.GET, queryset=ModelClass.objects.order_by('-id'))
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
    html = ''
    for island in islands:
        html += '<option value="' + str(island.id) + '">' + island.name + '</option>'
    return HttpResponse(html)
@login_required
def add_or_edit(request, app_label, model_class, id=None):
    context = {}
    Model = get_model(app_label, model_class, False)
    context['ModelClass'] = Model
    context['app_label'] = app_label
    fields = get_fields(Model, True)
    ModelForm = modelform_factory(Model, fields=tuple(fields), form=BaseForm)
    if id:
        instance = get_object_or_404(Model, id=id)
    else:
        instance = None
    if request.method == 'GET':
        context['formset'] = ModelForm(instance=instance)
    else:
        formset = ModelForm(request.POST, instance=instance)
        if formset.is_valid():
            instances = formset.save()
            return redirect('nexus_list', app_label=app_label, model_class=model_class)
        context['formset'] = formset
    return render(request, 'nexus/add.html', context)

@login_required
def delete_action(request, app_label, model_class, id=None):
    Model = get_model(app_label, model_class, False)
    if request.method == 'POST':
        ids = request.POST.getlist('id')
        Model.objects.filter(id__in=ids).delete()
    else:
        if id:
            instance = get_object_or_404(Model, id=id)
            instance.delete()
    return redirect('nexus_list', app_label=app_label, model_class=model_class)
