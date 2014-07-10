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
            createImageForm.handle(request, config.generate_glance_url(), data)
            context['success'] = 0
        else:
            context['success'] = -1
    return render(request, 'create_image.html', context)



def list(request, image_type=None):
    print "list++++++++++++++++++++"
    sys_images, app_images, pri_images = glance_client_api\
            .image_list_detailed_on_type(request.user.username, config.generate_glance_url())
    user = request.user
    context = {}
    if user.is_superuser:
        context['extent_html'] = 'admin_base.html'
    else:
        context['extent_html'] = 'site_base.html'
    context['sys_images'] = sys_images
    context['app_images'] = app_images
    context['pri_images'] = pri_images
    context['owner'] = user.username
    context['div_name'] = 'list_sys'
    context['type'] = 0
    if image_type != None:
        if int(image_type) == 0:
            context['div_name'] = 'list_sys'
        if int(image_type) == 1:
            context['div_name'] = 'list_app'
        if int(image_type) == 2:
            context['div_name'] = 'list_pri'
        context['type'] = image_type
    print "________________________"
    print context['div_name'], context['type']
    if request.is_ajax():
        if 'div_name' in request.GET:
            div_name_a = request.GET.get('div_name')
            if div_name_a == 'list_sys':
                return render(request, 'sys_list.html', context)
            if div_name_a == 'list_app':
                return render(request, 'app_list.html', context)
            if div_name_a == 'list_pri':
                return render(request, 'pri_list.html', context)
    return render(request, 'image_list.html', context)

def update(request):
    try:
        if request.method == 'POST':
            image_name = request.POST.get('name')
            image_desc = request.POST.get('desc')
            image_uuid = request.POST.get('uuid')
            is_public = request.POST.get('is_public')
            if is_public == 'true':
                _is_public = True
            else:
                _is_public = False

            print "---------image uuid", image_uuid
            image = glance_client_api.image_get(config.generate_glance_url(), image_uuid)
            image_properties = image.properties
            if image_properties.has_key('description'):
                image_properties['description'] = image_desc
            result = glance_client_api.image_update(config.generate_glance_url(), \
                                                   image_uuid, is_public=_is_public, name=image_name, properties=image_properties)
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
            glance_client_api.image_delete(config.generate_glance_url(), image_uuid)
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
