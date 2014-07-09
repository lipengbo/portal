import json
import datetime

from django.template.defaultfilters import register
from django.conf import settings
from django.core.cache import cache

from plugins.common.agent_client import AgentClient
from project.models import City, Island
from resources.models import Resource
@register.simple_tag(takes_context=True)
def get_all_cities(context):
    context['cities'] = City.objects.all()
    return ''

RESOURCE_USAGES = {}

@register.simple_tag(takes_context=True)
def resource_usage(context, current_island):


    total_switch = 0
    total_server = 0
    island_switch_ratios = []
    island_server_ratios = []

    for island in Island.objects.all():
        key = 'island_{}_usage'.format(island.id)
        result = cache.get(key)
        if result:
            switch_ratios, server_ratios = result[0], result[1]
        else:
            switch_ratios, server_ratios = [], []

        total_switch += len(switch_ratios)
        total_server += len(server_ratios)
        if current_island.id == island.id:
            island_switch_ratios = switch_ratios
            island_server_ratios = server_ratios


    context['switch_ratio'] = sum(island_switch_ratios) / float(total_switch or 1)
    context['server_ratio'] = sum(island_server_ratios) / float(total_server or 1)
    return ""


@register.simple_tag()
def resource_ratio(num, total):
    if total == 0:
        total = 1
    return num / float(total) * 100

@register.simple_tag(takes_context=True)
def get_total_resources(context):
    context['total_resource'] = Resource.registry['switch'].objects.count() + \
            Resource.registry['server'].objects.count()
    return ''

@register.simple_tag(takes_context=True)
def resource_num(context, island, resource_type):
    context[resource_type + '_num'] = Resource.registry[resource_type].objects.filter(island=island).count()
    return ''

def grouped(l, n):
    # Yield successive n-sized chunks from l.
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

@register.filter
def group_by(value, arg):
    return grouped(value, arg)

@register.filter
def project_selected(island, project):
    if project.id:
        islands = project.islands.filter(id=island.id)
    else:
        islands = []
    return islands

@register.filter
def is_membership(user, project):
    memberships = project.memberships.filter(id=user.id)
    return memberships


from time import mktime
from dateutil import tz
from datetime import datetime
import time

@register.filter
def set_date_format(value):
    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('CST')
    t = time.strptime(value, "%Y-%m-%dT%H:%M:%S.%f")
    dt = datetime.fromtimestamp(mktime(t)).replace(tzinfo=from_zone)
    return dt.astimezone(to_zone)
