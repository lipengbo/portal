from django.template.defaultfilters import register
from django.conf import settings

@register.filter
def get_display_fields(obj, only_name=False):
    return _get_fields(obj, only_name, True)

def get_fields(obj, only_name=False):
    return _get_fields(obj, only_name, False)

def _get_fields(obj, only_name=False, for_display=True):
    fields = obj._meta.fields
    display_fields = []
    for field in fields:
        if isinstance(obj, type):
            clazz = obj
        else:
            clazz = obj.__class__
        if for_display:
            try:
                excludes = list(clazz.admin_options()['exclude_fields'])
            except AttributeError:
                excludes = []
        else:
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
    return name

@register.filter
def get_class_verbose_name(obj):
    name = obj._meta.verbose_name
    return name
