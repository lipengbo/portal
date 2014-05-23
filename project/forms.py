#coding: utf-8
from django import forms

from django.core.exceptions import ValidationError

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field, Fieldset, ButtonHolder
from crispy_forms.bootstrap import AppendedText, PrependedText, FormActions

from project.models import Project, Category

class ProjectForm(forms.ModelForm):

    #    category_name = forms.RegexField(regex=u"^[\w\u4e00-\u9fa5]+$", required=True, max_length=64)

    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        self.fields['description'].widget = forms.Textarea()

        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-1'
        self.helper.field_class = 'col-md-5'
        self.helper.help_text_inline = True
        self.helper.layout = Layout(
            Fieldset(
                "", "name", "description", "category"
            ),
            Field('islands', template="project/_create_project_islands.html"),
        )

    def clean_name(self):
        return self.cleaned_data['name'].strip()

    def clean_islands(self):
        islands = self.cleaned_data.get('islands')
        if self.instance.id:
            for island in self.instance.islands.all():
                if island not in islands and island.slice_set.filter(project=self.instance):
                    raise ValidationError(u"如果需要取消节点，请先释放该节点下所有资源")

        return islands

    class Meta:
        model = Project
        fields = ("name", "description", "category", "islands")
