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
from common.models import FailedCounter, DeletedCounter, Counter
import datetime
from django.db.models import F

from agora.models import ForumThread

# Create your views here.

def index(request):
    context = {}
    return render(request, 'common/index.html', context)

def close_thread(request, thread_id):
    thread = get_object_or_404(ForumThread, id=thread_id)
    thread.closed = datetime.datetime.now()
    thread.save()
    return redirect('agora_thread', thread_id)


def decrease_counter_api(sender, instance):
    if sender == "slice":
        target = 1
        obj_time = instance.date_created
    elif sender == "project":
        target = 0
        obj_time = instance.created_time
    today = datetime.date.today()
    if obj_time.strftime('%Y%m%d') == today.strftime('%Y%m%d'):
        counter, new = Counter.objects.get_or_create(target=target, date=today, type=2)
        if counter.count > 0:
            counter.count = F("count") - 1
            counter.save()
    if obj_time.strftime('%Y%m') == today.strftime('%Y%m'):
        counter_month = Counter.objects.filter(target=target,
                                                    date__year=today.strftime('%Y'),
                                                    date__month=today.strftime('%m'),
                                                    type=1)
        if counter_month and counter_month[0].count > 0:
            counter_month[0].count = counter_month[0].count - 1
            counter_month[0].save()
    if obj_time.strftime('%Y') == today.strftime('%Y'):
        counter_year = Counter.objects.filter(target=target,
                                                    date__year=today.strftime('%Y'),
                                                    type=0)
        if counter_year and counter_year[0].count > 0:
            counter_year[0].count = counter_year[0].count - 1
            counter_year[0].save()


def increase_failed_counter(sender):
    print "==========================increase_failed_counter"
    today = datetime.date.today()
    if sender == "slice":
        target = 1
    elif sender == "project":
        target = 0
    counter_year = FailedCounter.objects.filter(target=target,
                                          date__year=today.strftime('%Y'),
                                          type=0)
    if counter_year:
        counter_year[0].count = counter_year[0].count + 1
        counter_year[0].save()
    else:
        counter_year = FailedCounter(target=target, date=today, count=1, type=0)
        counter_year.save()
    counter_month = FailedCounter.objects.filter(target=target,
                                                date__year=today.strftime('%Y'),
                                                date__month=today.strftime('%m'),
                                                type=1)
    if counter_month:
        counter_month[0].count = counter_month[0].count + 1
        counter_month[0].save()
    else:
        counter_month = FailedCounter(target=target, date=today, count=1, type=1)
        counter_month.save()
    counter, new = FailedCounter.objects.get_or_create(target=target, date=today, type=2)
    counter.count = F("count") + 1
    counter.save()


def decrease_failed_counter(sender, instance):
    if sender == "slice":
        target = 1
        obj_time = instance.date_expired
    elif sender == "project":
        target = 0
        obj_time = instance.created_time
    today = datetime.date.today()
    if obj_time.strftime('%Y%m%d') == today.strftime('%Y%m%d'):
        counter, new = FailedCounter.objects.get_or_create(target=target, date=today, type=2)
        if counter.count > 0:
            counter.count = F("count") - 1
            counter.save()
    if obj_time.strftime('%Y%m') == today.strftime('%Y%m'):
        counter_month = FailedCounter.objects.filter(target=target,
                                                    date__year=today.strftime('%Y'),
                                                    date__month=today.strftime('%m'),
                                                    type=1)
        if counter_month and counter_month[0].count > 0:
            counter_month[0].count = counter_month[0].count - 1
            counter_month[0].save()
    if obj_time.strftime('%Y') == today.strftime('%Y'):
        counter_year = FailedCounter.objects.filter(target=target,
                                                    date__year=today.strftime('%Y'),
                                                    type=0)
        if counter_year and counter_year[0].count > 0:
            counter_year[0].count = counter_year[0].count - 1
            counter_year[0].save()
