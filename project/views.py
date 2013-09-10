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

from project.forms import ProjectForm

def index(request):
    context = {}
    return render(request, 'project/index.html', context)

@login_required
def create(request):
    user = request.user
    context = {}
    if request.method == 'GET':
        form = ProjectForm()
    else:
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = user
            project.save()
            for category in form.cleaned_data.get('categories'):
                project.add_category(category)
            return redirect('project_create')

    context['form'] = form
    return render(request, 'project/create.html', context)
