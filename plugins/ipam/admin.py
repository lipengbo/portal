#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename:admin.py
# Date:Fri Sep 20 16:24:06 CST 2013
# Author:Pengbo Li
# E-mail:lipengbo10054444@gmail.com
from django.contrib import admin
from models import Network, Subnet, IPUsage


admin.site.register(Network)
admin.site.register(Subnet)
admin.site.register(IPUsage)
