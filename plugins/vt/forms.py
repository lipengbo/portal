#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename:forms.py
# Date:Mon Sep 23 13:26:45 CST 2013
# Author:Pengbo Li
# E-mail:lipengbo10054444@gmail.com
from django import forms
from models import VirtualMachine, Image

class VmForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(VmForm, self).__init__(*args, **kwargs)
        #self.fields['image'].queryset = Image.objects.exclude(name__in=['gateway', 'floodlight'])
        image_choices = [("", "---------")]
        image_choices.extend(Image.objects.exclude(name__in=['gateway',
                                        'Floodlight', 'POX', 'OpenDaylight']).values_list("id", "os"))
        self.fields['image'].choices = image_choices

    class Meta:
        model = VirtualMachine
        #fields = ("name", "flavor", "image", "server", "enable_dhcp")
        #fields = ("ram", "cpu", "hdd", "image", "server", "enable_dhcp")
        fields = ("image", "server") # "enable_dhcp")
        widgets = {
            #"flavor": forms.Select(attrs={'onblur': "check_vm_select('flavor')"}),
            "image": forms.Select(attrs={'onblur': "check_vm_select('image')"}),
            "server": forms.Select(attrs={'onblur': "check_vm_select('server')"}),
        }
