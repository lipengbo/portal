from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import F
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType

# Create your models here.
from idios.models import ProfileBase
from notifications.models import Notification


class Profile(ProfileBase):
    realm = models.CharField(max_length=1024, null=True, verbose_name=_("realm"))
    organization = models.CharField(max_length=64, null=True, verbose_name=_("Organization"))
    phone = models.CharField(max_length=11, null=True, blank=True, verbose_name=_("Phone"))
    state = models.IntegerField(default=0, choices=((1, 'reject'), (2, 'accept')))

    #def __unicode__(self):
    #    return self.realm and (self.realm[:10] + "...") or ""

    def action_url(self):
        return reverse('nexus_edit', args=('auth', 'user', self.user.id))

    def actions(self):
        if self.state != 0:
            return []
        return [
                {
                    'action_level': 'success',
                    'action_url': reverse('profiles_confirmation', args=(self.user.id,)),
                    'action_title': _('Accept')
                },
                {
                    'action_level': 'error',
                    'action_url': reverse('profiles_reject', args=(self.user.id, )),
                    'action_title': _('Reject')
                },
        ]


@receiver(post_delete, sender=Profile)
def delete_notifications(sender, instance, **kwargs):
    target_type = ContentType.objects.get_for_model(instance)
    Notification.objects.filter(action_object_content_type=target_type, action_object_object_id=instance.id).delete()
