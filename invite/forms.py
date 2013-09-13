from django import forms
from django.utils.translation import ugettext as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field, Fieldset

from invite.models import Invitation

class InvitationForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(InvitationForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.add_input(Submit('submit', _('Invite')))

    class Meta:
        fields = ("to_user", "message")
        model = Invitation
