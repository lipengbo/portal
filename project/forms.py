#coding: utf-8
from django import forms

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
        self.helper.label_class = 'col-md-2'
        self.helper.field_class = 'col-md-6'
        self.helper.help_text_inline = True
        self.helper.layout = Layout(
            Fieldset(
                "", "name", "description", "category", "islands",
            ),
            Field('islands', template="project/_create_project_islands.html"),
            ButtonHolder(
                Submit('submit', u'创建', css_class='btn btn-info')
            )
        )

    def clean_name(self):
        return self.cleaned_data['name'].strip()

    class Meta:
        model = Project
        fields = ("name", "description", "category", "islands")
        #widgets = {"islands": forms.SelectMultiple(attrs={"class": "hide"})}
