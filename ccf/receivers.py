from django.dispatch import receiver
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User

from account.signals import password_changed
from account.signals import user_sign_up_attempt, user_signed_up
from account.signals import user_login_attempt, user_logged_in

from eventlog.models import log
from notifications import notify


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
        notify.send(user, recipient=admin, verb=_(' signed up '), action_object=user.get_profile(),
                description=_("Please review this user"), target=user.get_profile())
