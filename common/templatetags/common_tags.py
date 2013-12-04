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

