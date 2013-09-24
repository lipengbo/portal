#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename:views.py
# Date:Mon Sep 23 18:36:59 CST 2013
# Author:Pengbo Li
# E-mail:lipengbo10054444@gmail.com
from django.shortcuts import render, get_object_or_404
from forms import VmForm
from models import VirtualMachine
from resources.models import Server


def vm_detail(request, vmId):
    vm = get_object_or_404(VirtualMachine, id=vmId)
    context = {}
    context['vm'] = vm
    context['vmId'] = vmId
    return render(request, 'vt/vm_detail.html', context)


def create_vm(request, sliceId):
    if request.method == 'POST':
        vm_form = VmForm(request.POST)
        if vm_form.is_valid():
            vm_form.save()
    else:
        vm_form = VmForm()
        vm_form.fields['server'].queryset = Server.objects.filter(id=3)
    context = {}
    context['vmform'] = vm_form
    return render(request, 'slice/create_slice.html', context)
