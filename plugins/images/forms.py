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

IMAGE_TYPE_CHOIES = ((1, 'sys'),(2, 'app'))


class CreateImageForm(forms.Form):
    name = forms.CharField(max_length="255", label=_("Name"), required=True)
    description = forms.CharField(widget=forms.widgets.Textarea(
        attrs={'class': 'modal-body-fixed-width'}),
        label=_("Description"),
        required=False)

    source_type = forms.ChoiceField(
        label=_('Image Source'),
        required=False,
        choices=[('url', _('Image Location')),
                 ('file', _('Image File'))],
        widget=forms.Select(attrs={
            'class': 'switchable',
            'data-slug': 'source'}))

    location = forms.CharField(max_length="255",
                               label=_("Image Location"),
                               help_text=_("An external (HTTP) URL to load "
                                           "the image from."),
                               widget=forms.TextInput(attrs={
                                                      'class': 'switched',
                                                      'data-switch-on': 'source',
                                                      'data-source-url': _('Image Location')}),
                               required=False)
    image_file = forms.FileField(label=_("Image File"),
                                 help_text=_("A local image to upload."),
                                 widget=forms.FileInput(attrs={
                                     'class': 'switched',
                                     'data-switch-on': 'source',
                                     'data-source-file': _('Image File')}),
                                 required=False)
    disk_format = forms.ChoiceField(label=_('Format'),
                                    required=True,
                                    choices=[('qcow2', _('qcow2 format'))],
                                    widget=forms.Select(attrs={'class':
                                                               'switchable'}))
    is_public = forms.BooleanField(label=_("Public"), required=False)
    image_type = forms.ChoiceField(widget=forms.RadioSelect, choices=IMAGE_TYPE_CHOIES)

    def __init__(self, *args, **kwargs):
        super(CreateImageForm, self).__init__(*args, **kwargs)

    def clean(self):
        data = super(CreateImageForm, self).clean()
        return data

    def handle(self, request, glance_url, data):
        meta = {'is_public': data['is_public'],
                'disk_format': data['disk_format'],
                'container_format': 'bare',
                'name': data['name'],
                'owner': request.user,
                'container_format': 'ovf',
                'properties': {}}
        meta['properties']['image_type'] = data['image_type']
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
