import json

from django.template.defaultfilters import register
from django.conf import settings

from plugins.common.agent_client import AgentClient
from project.models import City
from resources.models import Resource
@register.simple_tag(takes_context=True)
def get_all_cities(context):
    context['cities'] = City.objects.all()
    return ''

@register.simple_tag(takes_context=True)
def resource_usage(context, island):
    servers = island.server_set.all()
    switches = island.switch_set.all()
    print servers, switches
    server_ratios = []
    switch_ratios = []
    for server in servers:
        client = AgentClient(server.ip)
        try:
            host_status = json.loads(client.get_host_status())
        except Exception:
            pass
        else:
            ratio = host_status['mem'][2]
            server_ratios.append(ratio)

    for switch in switches:
        client = AgentClient(switch.ip)
        try:
            host_status = json.loads(client.get_host_status())
        except Exception:
            pass
        else:
            ratio = host_status['mem'][2]
            switch_ratios.append(ratio)
    context['switch_ratio'] = sum(switch_ratios) / float(len(switch_ratios) or 1)
    context['server_ratio'] = sum(server_ratios) / float(len(server_ratios) or 1)
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
