from django.template.defaultfilters import register
from django.conf import settings

from plugins.vt.models import VirtualMachine

@register.simple_tag
def divide(value, arg):
    if not arg:
        return 0
    return float(value) * 100 / float(arg)

@register.simple_tag(takes_context=True)
def quotas(context):
    context['quotas'] = settings.QUOTAS
    return ''

@register.filter
def user_project_count(user):
    project_count = user.project_set.all().count()
    return project_count

@register.filter
def user_slice_count(user):
    count = user.slice_set.all().count()
    return count

@register.filter
def user_vm_count(user):
    count = VirtualMachine.objects.total_vms(user)
    return count

@register.filter
def user_cpu_count(user):
    count = VirtualMachine.objects.user_stat_sum(user, 'cpu')
    return count

@register.filter
def user_mem_count(user):
    count = VirtualMachine.objects.user_stat_sum(user, 'ram')
    return count

@register.filter
def user_disk_count(user):
    count = VirtualMachine.objects.user_stat_sum(user, 'hdd')
    return count
