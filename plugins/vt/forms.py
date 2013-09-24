#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename:forms.py
# Date:Mon Sep 23 13:26:45 CST 2013
# Author:Pengbo Li
# E-mail:lipengbo10054444@gmail.com
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from models import VirtualMachine


class VmForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(VmForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.add_input(Submit('submit', '创建'))

    class Meta:
        model = VirtualMachine
        fields = ("name", "flavor", "image", "server", "enable_dhcp")
        widgets = {
            "flavor": forms.Select(),
            "image": forms.Select(),
            "server": forms.Select(),
        }
