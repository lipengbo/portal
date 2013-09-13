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
from django.contrib.contenttypes import generic
from django.contrib import messages

from invite.models import Invitation
from invite.forms import InvitationForm

@login_required
def invite(request, target_type_id, target_id):
    user = request.user

    target_type = ContentType.objects.get_for_id(target_type_id)
    target = target_type.get_object_for_this_type(id=target_id)

    if request.method == 'GET':
        form = InvitationForm()
    else:
        form = InvitationForm(request.POST)
        if form.is_valid():
            invitation = form.save(commit=False)
            invitation.from_user = user
            invitation.target = target
            invitation.save()
            messages.add_message(request, messages.INFO, _("Invitation completed."))
    context = {}
    context['target'] = target
    context['form'] = form
    return render(request, "invite/invite.html", context)
