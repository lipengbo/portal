from django.db import models
from django.db.models.signals import post_save, m2m_changed
from django.db.models import F
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.core.mail import send_mail

# Create your models here.
class InvitationManager(models.Manager):

    def invite(self, inviter, invitee, message, target):
        invitation = Invitation(from_user=inviter, to_user=invitee,
                message=message, target=target)
        invitation.save()

class Invitation(models.Model):
    from_user = models.ForeignKey(User, related_name="from_invitations")
    to_user = models.ForeignKey(User, related_name="to_invitations")

    message = models.TextField()

    target_type = models.ForeignKey(ContentType)
    target_id = models.PositiveIntegerField()
    target = generic.GenericForeignKey('target_type', 'target_id')

    objects = InvitationManager()

    def send(self):
        send_mail("You have an invitation", self.message, self.from_user.email, [self.to_user.email])

@receiver(post_save, sender=Invitation)
def send_invite(sender, instance, created, **kwargs):
    if created:
        instance.send()

