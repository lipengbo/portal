from hashlib import md5

from django.db import models
from django.db.models.signals import post_save, m2m_changed, pre_save
from django.db.models import F
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.core.mail import send_mail
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site

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
    accepted = models.BooleanField(default=False)
    key = models.CharField(max_length=32, unique=True)

    target_type = models.ForeignKey(ContentType)
    target_id = models.PositiveIntegerField()
    target = generic.GenericForeignKey('target_type', 'target_id')

    objects = InvitationManager()

    def accept(self):
        self.target.accept(self.to_user)
        self.accepted = True
        self.save()

    def accept_link(self):
        link = "http://%(domain)s%(relative_link)s" % ({"domain": Site.objects.get_current(), "relative_link": reverse("invite_accept", args=(self.key, ))})
        return link

    def get_target_name(self):
        display_name_func = getattr(self.target, 'get_display_name')
        if display_name_func:
            name = display_name_func()
        else:
            name = self.target.__unicode__()
        return name

    def send(self):
        body =  "You're invited by %(inviter)s to join a project of %(project)s.\nHere is a message from %(inviter)s:\n%(message)s\nYou can click the link below to accept the invitation:%(accept_link)s" % ({"inviter": self.from_user, "project": self.get_target_name(), "message": self.message, "accept_link": self.accept_link()})
        send_mail(_("You have an invitation"), body, self.from_user.email, [self.to_user.email])

@receiver(pre_save, sender=Invitation)
def generate_key(sender, instance, **kwargs):
    if not instance.id:
        salt = "asj3r3289s9823"
        instance.key = md5("{}{}{}{}".format(instance.from_user.id, 
            instance.to_user.id,
            instance.target_id, salt)).hexdigest()

@receiver(post_save, sender=Invitation)
def send_invite(sender, instance, created, **kwargs):
    if created:
        instance.send()