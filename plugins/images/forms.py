#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename:forms.py
# Date:四  6月 26 20:19:21 CST 2014
# Author:Pengbo Li
# E-mail:lipengbo10054444@gmail.com
"""
Views for managing images.
"""
from django import forms
from django.utils.translation import ugettext_lazy as _
from plugins.common import glance_client_api

IMAGE_TYPE_CHOIES = ((0, 'controller'), (1, 'slice'),(2, 'gateway'))


class CreateImageForm(forms.Form):
    name = forms.CharField(max_length="255", \
                           widget=forms.widgets.TextInput(attrs={'class':'form-control'}), \
                           required=True)
    description = forms.CharField(widget=forms.widgets.Textarea(attrs={'class': 'form-control'}), \
                                  required=False)

    #source_type = forms.ChoiceField(
    #    required=False,
    #    choices=((0, ''), (1, '')),
    #    widget=forms.RadioSelect())

    location = forms.CharField(max_length="255",
                               help_text=_("An external (HTTP) URL to load "
                                           "the image from."),
                               widget=forms.TextInput(attrs={
                                    'class': 'form-control radio_select_form',
                                    'disabled': 'disabled',
                                                      #'data-switch-on': 'source',
                                                      #'data-source-url': _('Image Location')
                               }),
                               required=False)
    image_file = forms.FileField(help_text=_("A local image to upload."),
                                 widget=forms.FileInput(attrs={
                                    'class': '',
                                    'onchange': 'document.getElementById(\'textfile\').value=this.value',
                                     #'data-switch-on': 'source',
                                     #'data-source-file': _('Image File')
                                 }),
                                 required=False)
    #disk_format = forms.ChoiceField(label=_('Format'),
    #                                required=True,
    #                                choices=[('qcow2', _('qcow2 format'))],
    #                                widget=forms.Select(attrs={'class':
    #                                                           'switchable'}))

    #is_public = forms.BooleanField(label=_("Public"), required=False)
    image_type = forms.ChoiceField(widget=forms.RadioSelect, choices=IMAGE_TYPE_CHOIES, \
                                   required=False)
    image_attr = forms.ChoiceField(widget=forms.Select, \
                                   choices=((0, 'sys'),(1, 'app'), (2, 'custom')),\
                                   required=False)

    def __init__(self, *args, **kwargs):
        super(CreateImageForm, self).__init__(*args, **kwargs)

    def clean(self):
        data = super(CreateImageForm, self).clean()
        return data

    def handle(self, request, glance_url, data):
        meta = {'is_public': True,
                'disk_format': 'qcow2',
                'container_format': 'ovf',
                'name': data['name'],
                'owner': request.user,
                #'container_format': 'bare',
                'properties': {}}
        meta['properties']['image_type'] = data['image_type']
        meta['properties']['image_attr'] = data['image_attr']
        if data['description']:
            meta['properties']['description'] = data['description']
        if data.get('location', None):
            meta['location'] = data['location']
        else:
            meta['data'] = request.FILES['image_file']

        try:
            image = glance_client_api.image_create(glance_url, **meta)
            return image
        except Exception:
            return False


class UpdateImageForm(forms.Form):
    image_id = forms.CharField(widget=forms.HiddenInput())
    name = forms.CharField(max_length="255", label=_("Name"))
    description = forms.CharField(widget=forms.widgets.Textarea(),
                                  label=_("Description"),
                                  required=False)
    disk_format = forms.CharField(label=_("Format"),
                                  widget=forms.TextInput(
                                      attrs={'readonly': 'readonly'}
                                  ))
    public = forms.BooleanField(label=_("Public"), required=False)

    def __init__(self, *args, **kwargs):
        super(UpdateImageForm, self).__init__(*args, **kwargs)
        self.fields['public'].widget = forms.CheckboxInput(
            attrs={'readonly': 'readonly'})

    def handle(self, glance_url, data):
        image_id = data['image_id']
        meta = {'is_public': data['public'],
                'disk_format': data['disk_format'],
                'container_format': 'bare',
                'name': data['name'],
                'properties': {'description': data['description']}}
        meta['purge_props'] = False
        try:
            image = glance_client_api.image_update(
                glance_url, image_id, **meta)
            return image
        except Exception:
            return False
