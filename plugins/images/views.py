#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename:views.py
# Date:四  6月 26 19:45:25 CST 2014
# Author:Pengbo Li
# E-mail:lipengbo10054444@gmail.com
"""
Views for managing images.
"""
from django.shortcuts import render
from plugins.common import glance_client_api
from plugins.images.forms import CreateImageForm
from django.http import HttpResponse
from etc import config

import json
import traceback


def create(request):
    context = {}
    context['forms'] = CreateImageForm()
    context['success'] = 1
    if request.method == 'POST':
        createImageForm = CreateImageForm(request.POST)
        if createImageForm.is_valid():
            data = createImageForm.clean()
            createImageForm.handle(request, config.glance_url(), data)
            context['success'] = 0
        else:
            print '------invalid-------'
            context['success'] = -1
    return render(request, 'create_image.html', context)



def list(request):
    print config.glance_url()
    sys_images, app_images = glance_client_api.image_list_detailed_on_type(config.glance_url())
    user = request.user
    context = {}
    if user.is_superuser:
        context['extent_html'] = 'admin_base.html'
    else:
        context['extent_html'] = 'site_base.html'
    context['sys_images'] = sys_images
    context['app_images'] = app_images
    return render(request, 'image_list.html', context)

def update(request):
    try:
        if request.method == 'POST':
            image_name = request.POST.get('name')
            image_desc = request.POST.get('desc')
            image_uuid = request.POST.get('uuid')
            image = glance_client_api.image_get(config.glance_url(), image_uuid)
            image_properties = image.properties
            if image_properties.has_key('description'):
                image_properties['description'] = image_desc
            result = glance_client_api.image_update(config.glance_url(), \
                                                    image_uuid, name=image_name, properties=image_properties)
            if result:
                return HttpResponse(json.dumps({'result': 0}))
            else:
                raise
    except:
        traceback.print_exc()
        return HttpResponse(json.dumps({'result': -1}))

def delete(request):
    try:
        if request.method == 'POST':
            image_uuid = request.POST.get('uuid')
            glance_client_api.image_delete(config.glance_url(), image_uuid)
            return HttpResponse(json.dumps({'result': 0}))
    except:
        traceback.print_exc()
        return HttpResponse(json.dumps({'result': -1}))

def upload(request):
    try:
        if request.method == 'POST':
            pass
        else:
            return render(request, 'upload_image.html')
    except:
        traceback.print_exc()
