from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

import account.forms
from profiles.models import Profile

class SignupForm(account.forms.SignupForm):
    realm = forms.CharField(max_length=64, label=_("Realm"), widget=forms.Textarea)
    phone = forms.CharField(max_length=11, label=_("Phone"), required=False)

class RejectForm(forms.Form):
    reason = forms.CharField(widget=forms.Textarea, label=_("Reason"))
    user = forms.ModelChoiceField(queryset=User.objects.none, widget=forms.HiddenInput)
