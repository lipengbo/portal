import datetime

from django.dispatch import receiver
from django.utils.translation import ugettext as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.db.models import F
from django.db.models.signals import post_save, m2m_changed, post_delete, pre_delete

from account.signals import password_changed
from account.signals import user_sign_up_attempt, user_signed_up
from account.signals import user_login_attempt, user_logged_in

from eventlog.models import log
from notifications import notify
from project.models import Project
from common.models import Counter, DeletedCounter
from slice.models import Slice, SliceDeleted
from notifications.models import Notification
from profiles.models import Profile
from invite.models import Invitation, Application
from common.views import decrease_failed_counter, decrease_counter_api

@receiver(post_save, sender=Slice)
@receiver(post_save, sender=Project)
def increase_counter(sender, instance, created, **kwargs):
    if created:
        today = datetime.date.today()
        if sender == Slice:
            target = 1
        elif sender == Project:
            target = 0
        counter_year = Counter.objects.filter(target=target,
                                              date__year=today.strftime('%Y'),
                                              type=0)
        if counter_year:
            counter_year[0].count = counter_year[0].count + 1
            counter_year[0].save()
        else:
            counter_year = Counter(target=target, date=today, count=1, type=0)
            counter_year.save()
        counter_month = Counter.objects.filter(target=target,
                                                    date__year=today.strftime('%Y'),
                                                    date__month=today.strftime('%m'),
                                                    type=1)
        if counter_month:
            counter_month[0].count = counter_month[0].count + 1
            counter_month[0].save()
        else:
            counter_month = Counter(target=target, date=today, count=1, type=1)
            counter_month.save()
        counter, new = Counter.objects.get_or_create(target=target, date=today, type=2)
        counter.count = F("count") + 1
        counter.save()


@receiver(post_delete, sender=Slice)
@receiver(post_delete, sender=Project)
def decrease_counter(sender, instance, **kwargs):
    if sender == Slice:
        tg = "slice"
    elif sender == Project:
        tg = "project"
    if instance.type == 1:
        decrease_failed_counter(tg, instance)
    else:
        decrease_counter_api(tg, instance)


@receiver(post_save, sender=SliceDeleted)
def increase_deleted_counter(sender, instance, created, **kwargs):
    print "------------------increase_deleted_counter"
    if created:
        today = datetime.date.today()
        if sender == SliceDeleted:
            target = 1
        elif sender == Project:
            target = 0
        counter_year = DeletedCounter.objects.filter(target=target,
                                              date__year=today.strftime('%Y'),
                                              type=0)
        if counter_year:
            counter_year[0].count = counter_year[0].count + 1
            counter_year[0].save()
        else:
            counter_year = DeletedCounter(target=target, date=today, count=1, type=0)
            counter_year.save()
        counter_month = DeletedCounter.objects.filter(target=target,
                                                    date__year=today.strftime('%Y'),
                                                    date__month=today.strftime('%m'),
                                                    type=1)
        if counter_month:
            counter_month[0].count = counter_month[0].count + 1
            counter_month[0].save()
        else:
            counter_month = DeletedCounter(target=target, date=today, count=1, type=1)
            counter_month.save()
        counter, new = DeletedCounter.objects.get_or_create(target=target, date=today, type=2)
        counter.count = F("count") + 1
        counter.save()


@receiver(post_delete, sender=Invitation)
@receiver(post_delete, sender=Application)
def delete_notifications(sender, instance, **kwargs):
    target_type = ContentType.objects.get_for_model(instance)
    Notification.objects.filter(action_object_content_type=target_type, action_object_object_id=instance.id).delete()

@receiver(user_logged_in)
def handle_user_logged_in(sender, **kwargs):
    log(
        user=kwargs.get("user"),
        action="USER_LOGGED_IN",
        extra={}
    )


@receiver(password_changed)
def handle_password_changed(sender, **kwargs):
    log(
        user=kwargs.get("user"),
        action="PASSWORD_CHANGED",
        extra={}
    )


@receiver(user_login_attempt)
def handle_user_login_attempt(sender, **kwargs):
    log(
        user=None,
        action="LOGIN_ATTEMPTED",
        extra={
            "username": kwargs.get("username"),
            "result": kwargs.get("result")
        }
    )


@receiver(user_sign_up_attempt)
def handle_user_sign_up_attempt(sender, **kwargs):
    log(
        user=None,
        action="SIGNUP_ATTEMPTED",
        extra={
            "username": kwargs.get("username"),
            "email": kwargs.get("email"),
            "result": kwargs.get("result")
        }
    )


@receiver(user_signed_up)
def handle_user_signed_up(sender, **kwargs):
    user = kwargs.get("user")
    log(
        user=user,
        action="USER_SIGNED_UP",
        extra={}
    )
    try:
        admin = User.objects.get(id=1, is_superuser=True)
    except User.DoesNotExist:
        pass
    else:
        profile = user.get_profile()
        notify.send(user, recipient=admin, verb=_(' signed up '), action_object=profile,
                description=_("Please review this user %s") % profile.realm)
