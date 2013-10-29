from django import forms
from django.forms.models import ModelForm
from django.db.models import get_model
from django.contrib.contenttypes.models import ContentType

class BaseForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(BaseForm, self).__init__(*args, **kwargs)
        if 'content_type' in self.fields:
            app_label, model_class = self._meta.model.admin_options()['ct_model']
            Model = get_model(app_label, model_class, False)
            queryset = Model.objects.all()
            self.fields['object_id'] = forms.ChoiceField(choices=((m.id, m.__unicode__()) for m in queryset), label=Model._meta.verbose_name)
            ct = ContentType.objects.get_by_natural_key(app_label, model_class)
            self.fields['content_type'].widget = forms.HiddenInput()
            self.fields['content_type'].initial = ct
