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

from django.contrib.admin.models import LogEntry

@login_required
def index(request):
    context = {}
    user = request.user
    logs = LogEntry.objects.all()
    if not user.is_superuser:
        logs = logs.filter(user_id=user.id)
    context['logs'] = logs
    return render(request, 'adminlog/index.html', context)
