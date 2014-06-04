import re

from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django.conf import settings
from django.contrib.auth.models import Permission

import account.forms
from profiles.models import Profile
from guardian.shortcuts import assign_perm, remove_perm
from account.models import EmailAddress, EmailConfirmation
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field, Fieldset, ButtonHolder


class SignupForm(account.forms.SignupForm):
    realm = forms.CharField(max_length=1024, label=_("Realm"), widget=forms.Textarea)
    organization = forms.CharField(max_length=64, label=_("Organization"))
    #phone = forms.CharField(max_length=11, label=_("Phone"), required=False)

    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.label_class = 'col-md-2'
        self.helper.field_class = 'col-md-7'
        self.helper.layout = Layout(
            Fieldset(
                "", "username", "password", "password_confirm", "email",
            ),
            Field('realm', rows=3),
            Field(
                "organization",
            ),
        )
        self.fields['realm'].widget.attr = {"rows": 7}

    def clean_password_confirm(self):
        if "password" in self.cleaned_data and "password_confirm" in self.cleaned_data:
            if self.cleaned_data["password"] != self.cleaned_data["password_confirm"]:
                raise forms.ValidationError(_("You must type the same password each time."))
        return self.cleaned_data['password_confirm']

class RejectForm(forms.Form):
    reason = forms.CharField(widget=forms.Textarea, label=_("Reason"))
    user = forms.ModelChoiceField(queryset=User.objects.none, widget=forms.HiddenInput)

alnum_re = re.compile(r"^\w+$")
class UserForm(forms.ModelForm):
    
    can_create_project = forms.BooleanField(initial=False, required=False, label=_("Can add Project"))

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        can_create_project_field = self.fields['can_create_project']
        try:
            self.instance.user_permissions.get(codename='add_project')
            can_create_project_field.initial = True
        except Permission.DoesNotExist:
            pass
        self.fields['username'].help_text = ''

    def clean_username(self):
        if not alnum_re.search(self.cleaned_data["username"]):
            raise forms.ValidationError(_("Usernames can only contain letters, numbers and underscores."))
        return self.cleaned_data["username"]
    
    def save(self):
        can_create_project = self.cleaned_data.get('can_create_project')
        if can_create_project:
            assign_perm('project.add_project', self.instance)
        else:
            remove_perm('project.add_project', self.instance)

        ea = EmailAddress.objects.get_primary(self.instance)
        email = self.cleaned_data.get('email')
        if ea.email != email:
            EmailAddress.objects.get_or_create(user=self.instance, email=email)
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
