#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename:views.py
# Date:Mon Sep 23 18:36:59 CST 2013
# Author:Pengbo Li
# E-mail:lipengbo10054444@gmail.com
from django.shortcuts import render, get_object_or_404
from forms import VmForm
from models import VirtualMachine


def vm_detail(request, vmId):
    vm = get_object_or_404(VirtualMachine, id=vmId)
    context = {}
    context['vm'] = vm
    context['vmId'] = vmId
    return render(request, 'vt/vm_detail.html', context)


def create_vm(request, sliceId):
    if request.method == 'POST':
        form = VmForm(request.POST)
        form.save()
    else:
        form = VmForm()
    context = {}
    context['form'] = form
    return render(request, 'vt/create_vm.html', context)
