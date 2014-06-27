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


def create(request):
    if request.method == 'POST':
        createImageForm = CreateImageForm(request.POST)
        if createImageForm.is_valid():
            print request.FILES['image_file']
            data = createImageForm.clean()
            print data
            url = 'http://192.168.5.111:9292'
            createImageForm.handle(request, url, data)
        return HttpResponse(0)
    else:
        context = {}
        context['forms'] = CreateImageForm()
        return render(request, 'images/create.html', context)


def list(request):
    url = 'http://192.168.5.111:9292'
    images = glance_client_api.image_list_detailed(url)
    context = {}
    context['images'] = images
    return render(request, 'images/list.html', context)
