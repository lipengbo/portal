from django import forms
from django.utils.translation import ugettext as _

import account.forms
from profiles.models import Profile

class SignupForm(account.forms.SignupForm):
    organization = forms.CharField(max_length=64, label=_("Organization"))
    phone = forms.CharField(max_length=11, label=_("Phone"))
