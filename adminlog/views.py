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
from django.db.models import Q

from django.contrib.admin.models import LogEntry
from adminlog.models import SUCCESS, FAIL
@login_required
def index(request):
    context = {}
    user = request.user
    logs = LogEntry.objects.filter(action_flag__in=(SUCCESS, FAIL))
    if not user.is_superuser:
        logs = logs.filter(user_id=user.id)
    if 'query' in request.GET:
        query = request.GET.get('query')
        if query:
            logs = logs.filter(Q(change_message__icontains=query)|Q(object_repr__icontains=query))
            context['query'] = query
    context['logs'] = logs
    return render(request, 'adminlog/index.html', context)
