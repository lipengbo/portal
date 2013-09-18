#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename:management.py
# Date:Wed Sep 18 16:29:37 CST 2013
# Author:Pengbo Li
# E-mail:lipengbo10054444@gmail.com
from django.db.models.signals import post_syncdb
from plugins.ipam import models


def init_network(sender, **kwargs):
    models.Network(netaddr='10.0.0.0/8', type=1).save()
    models.Network(netaddr='172.16.0.0/16', type=0).save()


post_syncdb.connect(init_network, sender=models)
