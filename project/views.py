from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.db import transaction, IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.contrib.contenttypes.models import ContentType

from project.models import Project
from project.forms import ProjectForm

@login_required
def index(request):
    user = request.user
    projects = Project.objects.filter(owner=user)
    context = {}
    context['projects'] = projects
    return render(request, 'project/index.html', context)

def detail(request, id):
    project = get_object_or_404(Project, id=id)
    context = {}
    context['project'] = project
    return render(request, 'project/detail.html', context)

@login_required
def create_or_edit(request, id=None):
    user = request.user
    context = {}
    instance = None
    if id:
        instance = get_object_or_404(Project, id=id)
    if request.method == 'GET':
        form = ProjectForm(instance=instance)
    else:
        form = ProjectForm(request.POST, instance=instance)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = user
            project.save()
            return redirect('project_detail', id=project.id)

    context['form'] = form
    return render(request, 'project/create.html', context)
