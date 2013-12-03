from django.template.defaultfilters import register
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext as _

from invite.models import Invitation, Application

@register.filter
def application_status(target, user):
    target_type = ContentType.objects.get_for_model(target)
    try:
        application = Application.objects.get(from_user=user, target_id=target.id, target_type=target_type)
    except Application.DoesNotExist:
        return {'is_apply': False, 'accepted': False}
    else:
        return {'is_apply': True, 'accepted': application.state }

@register.filter
def invitation_status(target, to_user):
    target_type = ContentType.objects.get_for_model(target)
    try:
        invitation = Invitation.objects.get(to_user=to_user, target_id=target.id, target_type=target_type)
    except Invitation.DoesNotExist:
        return {'is_invited': False, 'accepted': False}
    else:
        return {'is_invited': True, 'accepted': invitation.state }
