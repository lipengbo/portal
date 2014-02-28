import re

from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django.conf import settings

import account.forms
from profiles.models import Profile
from guardian.shortcuts import assign_perm, remove_perm
from account.models import EmailAddress, EmailConfirmation

class SignupForm(account.forms.SignupForm):
    realm = forms.CharField(max_length=1024, label=_("Realm"), widget=forms.Textarea)
    organization = forms.CharField(max_length=64, label=_("Organization"))
    #phone = forms.CharField(max_length=11, label=_("Phone"), required=False)

class RejectForm(forms.Form):
    reason = forms.CharField(widget=forms.Textarea, label=_("Reason"))
    user = forms.ModelChoiceField(queryset=User.objects.none, widget=forms.HiddenInput)

alnum_re = re.compile(r"^\w+$")
class UserForm(forms.ModelForm):
    
    can_create_project = forms.BooleanField(initial=False, required=False, label=_("Can add Project"))

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        can_create_project_field = self.fields['can_create_project']
        can_create_project_field.initial = self.instance.has_perm('project.add_project')
        self.fields['username'].help_text = ''

    def clean_username(self):
        if not alnum_re.search(self.cleaned_data["username"]):
            raise forms.ValidationError(_("Usernames can only contain letters, numbers and underscores."))
        return self.cleaned_data["username"]
    
    def save(self):
        can_create_project = self.cleaned_data.get('can_create_project')
        if can_create_project:
            assign_perm('project.add_project', self.instance)
        ea = EmailAddress.objects.get_primary(self.instance)
        try:
            ec = EmailConfirmation.objects.get(email_address=ea)
        except EmailConfirmation.DoesNotExist:
            ea.send_confirmation()
        profile = self.instance.get_profile()
        profile.state = 2
        profile.save()
        super(UserForm, self).save()

    class Meta:
        model = User
        fields = ['username', 'email']
