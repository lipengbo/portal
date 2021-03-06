from django.template.defaultfilters import register
from django.conf import settings
from django.db.models import get_model

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
            except :
                excludes = []
            if clazz.__name__ == 'User':
                excludes.append('password')
                excludes.append('username')
                excludes.append('date_joined')
                excludes.append('first_name')
                excludes.append('last_name')
                excludes.append('is_staff')
                excludes.append('is_superuser')
                excludes.append('last_login')
                excludes.append('is_active')
        else:
            try:
                excludes = list(clazz.admin_options()['form_exclude_fields'])
            except :
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
    field = obj._meta.get_field_by_name(key)
    if field and field[0].choices:
        return getattr(obj, 'get_' + key + '_display')()
    else:
        return getattr(obj, key)

@register.filter
def get_attr(obj, key):
    return getattr(obj, key)

@register.filter
def concat(str1, str2):
    return str1 + str2

@register.filter
def get_class_name(obj):
    name = obj.__class__.__name__
    return name

@register.filter
def get_class_verbose_name(obj):
    name = obj._meta.verbose_name
    return name

@register.filter
def get_related_models(obj):
    if isinstance(obj, type):
        clazz = obj
    else:
        clazz = obj.__class__
    try:
        related_models = clazz.admin_options()['related_models']
        for model in related_models:
            ModelClass = get_model(model['app_label'], model['model'], False)
            name = ModelClass._meta.verbose_name
            model['name'] = name
        return related_models
    except :
        return []
