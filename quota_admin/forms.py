#coding: utf-8

from django import forms
from django.conf import settings

class ApplyForm(forms.Form):

    project = forms.ChoiceField(choices=())
    slice = forms.ChoiceField(choices=())
    vm = forms.ChoiceField(choices=())
    cpu = forms.ChoiceField(choices=())
    mem = forms.ChoiceField(choices=())
    disk = forms.ChoiceField(choices=())

    description = forms.CharField(max_length=1024)

    def __init__(self, *args, **kwargs):
        super(ApplyForm, self).__init__(*args, **kwargs)
        cpu_quotas = settings.QUOTAS['cpu']
        project_quotas = settings.QUOTAS['project']
        vm_quotas = settings.QUOTAS['vm']
        slice_quotas = settings.QUOTAS['slice']
        mem_quotas = settings.QUOTAS['mem']
        disk_quotas = settings.QUOTAS['disk']

        self.fields['cpu'].choices = tuple([(quota, quota) for quota in cpu_quotas])
        self.fields['project'].choices = tuple([(quota, quota) for quota in project_quotas])
        self.fields['vm'].choices = tuple([(quota, quota) for quota in vm_quotas])
        self.fields['slice'].choices = tuple([(quota, quota) for quota in slice_quotas])
        self.fields['mem'].choices = tuple([(quota, quota) for quota in mem_quotas])
        self.fields['disk'].choices = tuple([(quota, quota) for quota in disk_quotas])

