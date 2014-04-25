#coding: utf-8

from django.template.defaultfilters import register
from django.conf import settings
from django.core.urlresolvers import reverse

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
    if not isinstance(perm, unicode):
        perm = "{}.{}".format(perm.content_type.app_label, perm.codename)
    context['has_perm'] = user.has_perm(perm, obj)
    return ""

@register.simple_tag()
def action_url(notification):
    if notification.verb == u'调整配额':
        return reverse('quota_admin_quota')
    else:
        return notification.action_object.action_url()

