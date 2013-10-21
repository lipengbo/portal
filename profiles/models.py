from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import F
from django.utils.translation import ugettext as _

# Create your models here.
from idios.models import ProfileBase


class Profile(ProfileBase):
    organization = models.CharField(max_length=64, null=True, verbose_name=_("Organization"))
    phone = models.CharField(max_length=11, null=True)
