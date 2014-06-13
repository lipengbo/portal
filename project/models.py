#coding: utf-8
import datetime

from django.db import models
from django.db import IntegrityError
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save, m2m_changed, post_delete, pre_delete
from django.db.models import F
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.conf import settings
from django.core.mail import send_mail

from adminlog.models import log
from guardian.shortcuts import assign_perm, remove_perm, get_perms

from invite.models import Invitation, Application
from notifications import notify

class City(models.Model):
    name = models.CharField(max_length=128, verbose_name=_("name"), unique=True)
    description = models.TextField(verbose_name=_("description"))

    def change_desc(self, new_desc):
        self.description = new_desc
        self.save()

    def __unicode__(self):
        return self.name

    @staticmethod
    def admin_options():
        options = {
            'exclude_fields': ('name', ),
        }
        return options

    class Meta:
        verbose_name = _("City")

class Island(models.Model):
    name = models.CharField(max_length=128, verbose_name=_("name"), unique=True)
    description = models.TextField(verbose_name=_("description"))
    city = models.ForeignKey(City, verbose_name=_("City"))
    novnc_ip = models.IPAddressField(null=True, verbose_name=_("novnc_ip"))
    vpn_ip = models.IPAddressField(null=True, default='0.0.0.0', verbose_name=_("vpn_ip"))
    sflow_ip = models.IPAddressField(null=True, default='0.0.0.0', verbose_name=_("sflow_ip"))
    sflow_port = models.IntegerField(null=True, verbose_name=_('sflow_port'))

    @staticmethod
    def admin_options():
        options = {
            'exclude_fields': ('name', 'vpn_ip'),
            'form_exclude_fields': ('vpn_ip',),
        }
        return options

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _("Island")

class Category(models.Model):
    name = models.CharField(max_length=64, unique=True)
    image = models.CharField(max_length=32, default='img/cat_other.png')

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _("Category")

class ProjectManager(models.Manager):

    def get_query_set(self, *args, **kwargs):
        return super(ProjectManager, self).get_query_set(*args, **kwargs).filter(is_deleted=False)

class Project(models.Model):
    owner = models.ForeignKey(User, verbose_name=u"用户")
    name = models.CharField(max_length=255, verbose_name=_("Project Name"), help_text="学校/单位名-实验室/部门名-项目名称，如北京邮电大学-未来网络实验室-SDN项目")
    description = models.CharField(max_length=1024, verbose_name=_("Project Description"), help_text="如项目内容：研究软件定义网络的关键技术如控制器北向接口；<br />项目目标：提出创新算法，研发具有自主知识产权的未来网络核心设备及创新应用；<br />项目支持：国家自然科学基金或863、973项目支持；")
    islands = models.ManyToManyField(Island, verbose_name=_("Island"))  # Usage: project.islands.add(island)
    memberships = models.ManyToManyField(User, through="Membership",
            related_name="project_belongs", verbose_name=_("Memberships"))
    category = models.ForeignKey(Category, verbose_name=_("Category"))
    created_time = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    objects = ProjectManager()
    admin_objects = models.Manager()

    def created_date(self):
        return self.created_time

    def add_category(self, category):
        project_category, created = ProjectCategory.objects.get_or_create(category=category,
                project=self)

    def add_member(self, user, is_owner=False):
        project_membership, created = Membership.objects.get_or_create(project=self,
                user=user, defaults={'is_owner': is_owner})

    def dismiss(self, user):
        if user == self.owner:
            return
        try:
            project_membership = Membership.objects.get(project=self,
                user=user)
        except Membership.DoesNotExist:
            pass
        else:
            project_membership.delete()
            notification = notify.send(user, recipient=self.owner,
                    verb=_(' quit from'), action_object=self, target=self)
            site = Site.objects.get_current()
            notification_link =  "http://" + site.domain + reverse("notifications:all")
            subject = _("User quit from project")
            content = _("Dear user:\n User %(user)s has quit from your project %(project)s. You can click the link below to see the details.\n%(notification_link)s\n") % ({'notification_link': notification_link, 'user': user, 'project': self})
            send_mail(subject, content,
                    settings.DEFAULT_FROM_EMAIL, [self.owner.email], fail_silently=False)

    def invite(self, invitee, message):
        Invitation.objects.invite(self.owner, invitee, message, self)

    def member_ids(self):
        return self.memberships.all().values_list('id', flat=True)

    def log_info(self):
        return u"项目：{}".format(self.__unicode__())

    def delete(self, *args, **kwargs):
        try:
            if self.slice_set.all().count() > 0:
                raise Exception('slice does not deleted completely')
            super(Project, self).delete(*args, **kwargs)
        except Exception:
            if not self.is_deleted:
                self.is_deleted = True
                self.name = self.name + u' *'
                self.save()
                post_delete.send(sender=Project, instance=self)

    def force_delete(self):
        super(Project, self).delete()

    @property
    def get_content_type(self):
        project_type = ContentType.objects.get_for_model(self)
        return project_type

    def get_display_name(self):
        return self.name

    def absolute_url(self):
        if self.is_deleted:
            return ""
        else:
            return reverse('project_detail', args=(self.id, ))

    def accept(self, member):
        try:
            self.add_member(member)
        except IntegrityError, e:
            pass

    def get_slices(self):
        return self.slice_set.filter(type=0)

    @property
    def subject(self):
        return ""

    @property
    def content(self):
        return ""

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _("Project")
        unique_together = (("owner", "name"), )
        permissions = (
                ('create_slice', _("Can add Slice")),
                #('manage_project_member', _('Manage Project Member')),
                #('invite_project_member', _('Invite Project Member')),
                #('dismiss_project_member', _('Dismiss Project Member')),
                #('review_project_member', _('Riew Project')),
        )



class Membership(models.Model):
    project = models.ForeignKey(Project)
    user = models.ForeignKey(User)
    is_owner = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u"{} - {}".format(self.user, self.project)

    class Meta:
        unique_together = (("project", "user"), )
        verbose_name = _("Membership")


@receiver(post_save, sender=Project)
def create_owner_membership(sender, instance, created, **kwargs):
    if created:
        owner = instance.owner
        assign_perm('project.change_project', owner, instance)
        assign_perm('project.delete_project', owner, instance)
        assign_perm('project.create_slice', owner, instance)
        instance.add_member(instance.owner, True)
        log(owner, instance, "创建项目")


@receiver(pre_delete, sender=Membership)
def delete_permission(sender, instance, **kwargs):
    user_perms = get_perms(instance.user, instance.project)
    slices = instance.project.slice_set.filter(owner=instance.user)
    for slice in slices:
        slice.delete(user=instance.user)
    for perm in user_perms:
        if perm != 'project.add_project':
            remove_perm(perm, instance.user, instance.project)

@receiver(pre_delete, sender=Membership)
def delete_invitation(sender, instance, **kwargs):
    to_user = instance.user
    project = instance.project
    owner = project.owner
    target_type = ContentType.objects.get_for_model(project)
    Invitation.objects.filter(to_user=to_user, from_user=owner, target_id=project.id, target_type=target_type).delete()
    Application.objects.filter(to_user=owner, from_user=to_user, target_id=project.id, target_type=target_type).delete()

@receiver(pre_delete, sender=Project)
def delete_invitation_application(sender, instance, **kwargs):
    project = instance
    target_type = ContentType.objects.get_for_model(project)
    Invitation.objects.filter(target_id=project.id, target_type=target_type).delete()
    Application.objects.filter(target_id=project.id, target_type=target_type).delete()

@receiver(post_delete, sender=Project)
def log_project_delete(sender, instance, **kwargs):
    try:
        log(instance.owner, instance, "删除项目")
    except User.DoesNotExist:
        pass

@receiver(post_save, sender=Membership)
def assign_membership_permission(sender, instance, created, **kwargs):
    if created:
        if not instance.is_owner:
            assign_perm('project.create_slice', instance.user, instance.project)


#@receiver(m2m_changed, sender=Virttool.slices.through)
#@receiver(m2m_changed, sender=Controller.slices.through)
def on_add_into_slice(sender, instance, action, pk_set, model, **kwargs):
    resource = instance
    if action == 'post_add': #: only handle post_add event
        resource.on_add_into_slice()

