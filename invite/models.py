#coding: utf-8

from hashlib import md5

from django.db import models
from django.db.models.signals import post_save, m2m_changed, pre_save
from django.db.models import F
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.core.mail import send_mail
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.conf import settings

from notifications import notify
from notifications.models import Notification

# Create your models here.
class InvitationManager(models.Manager):

    def invite(self, inviter, invitee, message, target):
        invitation = Invitation(from_user=inviter, to_user=invitee,
                message=message, target=target)
        invitation.save()

class Connection(models.Model):
    from_user = models.ForeignKey(User, related_name="%(app_label)s_%(class)s_from_invitations")
    to_user = models.ForeignKey(User, related_name="%(app_label)s_%(class)s_to_invitations", verbose_name=_("Invitee"))

    message = models.TextField(verbose_name=_("Message"))
    state = models.IntegerField(default=0, choices=((0, _("created")),(1, _("Accepted")), (2, _("Rejected"))))
    key = models.CharField(max_length=32, unique=True)

    target_type = models.ForeignKey(ContentType)
    target_id = models.PositiveIntegerField()
    target = generic.GenericForeignKey('target_type', 'target_id')

    created_time = models.DateTimeField(auto_now_add=True)


    def get_target_name(self):
        display_name_func = getattr(self.target, 'get_display_name')
        if display_name_func:
            name = display_name_func()
        else:
            name = self.target.__unicode__()
        return name

    def reject(self):
        self.state = 2
        self.save()

    def actions(self):
        if self.state != 0:
            return

        return [
                {
                    'action_level': 'success',
                    'action_url': reverse('invite_accept', args=(self.get_kind(), self.key)),
                    'action_title': _('Accept')
                },
                {
                    'action_level': 'danger',
                    'action_url': reverse('invite_reject', args=(self.get_kind(), self.key)),
                    'action_title': _('Reject')
                },
        ]

    class Meta:

        abstract = True

class Invitation(Connection):

    objects = InvitationManager()

    @property
    def subject(self):
        return _("Project Invitation")

    @property
    def content(self):
        body = _("You're invited by %(inviter)s to join a project of %(project)s.\nHere is a message from %(inviter)s:\n%(message)s\nYou can click the link below to accept the invitation:\n%(accept_link)s") % ({"inviter": self.from_user, "project": self.get_target_name(), "message": self.message, "accept_link": self.accept_link()})
        return body

    def get_kind(self):
        return "invite"

    def accept(self):
        self.target.accept(self.to_user)
        self.state = 1
        self.save()

    def accept_link(self):
        link = "http://%(domain)s%(relative_link)s" % ({"domain": Site.objects.get_current(), "relative_link": reverse("notifications:all")})
        return link

    def send(self):
        notify.send(self.from_user, recipient=self.to_user, verb=_('invited you to join in'), action_object=self,
                description=self.message, target=self.target)

    @property
    def action_url(self):
        return reverse('project_detail', args=(self.target.id, ))

    class Meta:
        verbose_name = _("Invitation")

class Application(Connection):

    def get_kind(self):
        return "apply"

    def accept(self):
        self.target.accept(self.from_user)
        self.state = 1
        self.save()
        notify.send(self.to_user, recipient=self.from_user, verb=_('approved your application to join'), action_object=self,
                target=self.target)

    def reject(self):
        super(Application, self).reject()
        notify.send(self.to_user, recipient=self.from_user, verb=_('rejected your application to join'), action_object=self,
                target=self.target)

    @property
    def subject(self):
        return _("Project Application")

    @property
    def content(self):
        body = _("%(applicant)s wants to join in %(project)s.\nHere is a message from %(applicant)s:\n%(message)s\nYou can click the link below to accept the application:\n%(accept_link)s") % ({"applicant": self.from_user, "project": self.get_target_name(), "message": self.message, "accept_link": self.accept_link()})
        return body

    def accept_link(self):
        link = "http://%(domain)s%(relative_link)s" % ({"domain": Site.objects.get_current(), "relative_link": reverse("notifications:all")})
        return link

    def send(self):
        notify.send(self.from_user, recipient=self.to_user, verb=_('applied to join in'), action_object=self,
                description=self.message, target=self.target)

    @property
    def action_url(self):
        if self.state == 0:
            return reverse('project_detail', args=(self.target.id, )) + "?application={}".format(self.id)
        else:
            return ""

    class Meta:
        verbose_name = _("Application")

@receiver(pre_save, sender=Invitation)
@receiver(pre_save, sender=Application)
def generate_key(sender, instance, **kwargs):
    if not instance.id:
        salt = "asj3r3289s9823"
        instance.key = md5("{}{}{}{}".format(instance.from_user.id, 
            instance.to_user.id,
            instance.target_id, salt)).hexdigest()


@receiver(post_save, sender=Invitation)
@receiver(post_save, sender=Application)
def send_invite(sender, instance, created, **kwargs):
    if created:
        instance.send()

@receiver(post_save, sender=Notification)
def send_notification_email(sender, instance, created, **kwargs):
    if not created:
        return
    site = Site.objects.get_current()
    notice_link= "http://" + site.domain + reverse("notifications:all")
    content = render_to_string('notifications/notice.txt', {'notice': instance,
        'notification_link': "http://" + site.domain + reverse("notifications:all")})
    site_name = site.name
    subject = ''
    has_state = hasattr(instance.action_object, 'state')
    if hasattr(instance.action_object, 'subject') and ((has_state and instance.action_object.state == 0) or not has_state):
        subject = site_name + instance.action_object.subject
        content = instance.action_object.content
    else:
        subject = _('[%(site_name)s] You have new notification messages') % {'site_name': site_name}
    if instance.verb == u'调整配额':
        subject = u'SDN创新实验平台用户配额调整通知'
        content = u"亲爱的用户，您好：\n\t您在SDN创新实验平台中的配额已经调整，您可以单击以下链接查看详情。\n" + notice_link + u"SDN创新实验平台"
    if instance.verb == u'虚网过期删除':
        subject = u'SDN创新实验平台虚网过期删除通知'
        content = u"亲爱的用户，您好：\n您创建的虚网“" + instance.action_object.show_name + u"”超过有效期已经被删除，您可以单击以下链接查看详情。\n" + notice_link
    if content:
        send_mail(subject, content,
                  settings.DEFAULT_FROM_EMAIL, [instance.recipient.email], fail_silently=False)
