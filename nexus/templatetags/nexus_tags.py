from django.template.defaultfilters import register
from django.conf import settings

@register.filter
def get_fields(obj, only_name=False):
    fields = obj._meta.local_fields
    display_fields = []
    for field in fields:
        if isinstance(obj, type):
            clazz = obj
        else:
            clazz = obj.__class__
        try:
            excludes = list(clazz.admin_options()['exclude_fields'])
        except AttributeError:
            excludes = []
        excludes.append('id')
        if field.name not in excludes:
            if not field.editable:
                continue
            f = field
            if only_name:
                f = field.name
            display_fields.append(f)
    return display_fields

@register.filter
def get_value(obj, key):
    return getattr(obj, key)

@register.filter
def get_class_name(obj):
    name = obj.__class__.__name__
    print name.__str__()
    return name
