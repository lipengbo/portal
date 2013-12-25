from django.template.defaultfilters import register
from django.conf import settings

from account.models import EmailAddress, EmailConfirmation

@register.filter
def confirmation_email_sent(user):
    ea = EmailAddress.objects.get_primary(user)
    try:
        ec = EmailConfirmation.objects.get(email_address=ea)
    except EmailConfirmation.DoesNotExist:
        return False
    else:
        return True

@register.simple_tag(takes_context=True)
def has_perm(context, user, perm, obj):
    context['has_perm'] = user.has_perm("{}.{}".format(perm.content_type.app_label, perm.codename), obj)
    return ""
