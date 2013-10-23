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

def index(request):
    context = {}
    return render(request, 'nexus/index.html', context)

def list_objects(request, app_label, model_class):
    context = {}
    ModelClass = get_model(app_label, model_class, False)
    objects = ModelClass.objects.order_by('-id')
    context['objects'] = objects
    context['app_label'] = app_label
    context['ModelClass'] = ModelClass
    return render(request, 'nexus/list.html', context)

def add_or_edit(request, app_label, model_class, id=None):
    context = {}
    Model = get_model(app_label, model_class, False)
    fields = get_fields(Model, True)
    print fields
    ModelForm = modelform_factory(Model, fields=tuple(fields))
    if request.method == 'GET':
        context['formset'] = ModelForm
    else:
        formset = ModelForm(request.POST)
        instances = formset.save()
        context['formset'] = formset
        return redirect('nexus_list', app_label=app_label, model_class=model_class)
    return render(request, 'nexus/add.html', context)

