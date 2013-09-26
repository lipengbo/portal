#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename:views.py
# Date:Mon Sep 23 18:36:59 CST 2013
# Author:Pengbo Li
# E-mail:lipengbo10054444@gmail.com
import json
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from forms import VmForm
from resources.models import Server
from slice.models import Slice


def vm_list(request, sliceid):
    vms = get_object_or_404(Slice, id=sliceid).virtualmavhine_set.all()
    context = {}
    context['vms'] = vms
    return render(request, 'vt/vm_list.html', context)


def create_vm(request, sliceid):
    print "start to create vm "
    print 'sliceid=%s' % sliceid
    print request.POST
    print request.GET
    if request.method == 'POST':
        vm_form = VmForm(request.POST)
        if vm_form.is_valid():
            vm = vm_form.save(commit=False)
            print 'vm= %s ' % repr(vm)
            #vm.slice = get_object_or_404(Slice, id=sliceid)
            #vm.save()
            return HttpResponse(json.dumps({'value': 1}))
        else:
            return HttpResponse(json.dumps({'value': 0}))
    else:
        vm_form = VmForm()
        vm_form.fields['server'].queryset = Server.objects.filter(id=3)
        context = {}
        context['vm_form'] = vm_form
        context['sliceid'] = sliceid
        return render(request, 'vt/create_vm.html', context)
