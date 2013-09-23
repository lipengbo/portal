#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename:management.py
# Date:Mon Sep 23 09:31:36 CST 2013
# Author:Pengbo Li
# E-mail:lipengbo10054444@gmail.com
from django.db.models.signals import post_syncdb
from django.dispatch import receiver
import models


@receiver(post_syncdb, sender=models)
def init_network_for_slice(sender, **kwargs):
    if not models.Network.objects.filter(type=1):
        net_for_slice = models.Network(netaddr='10.0.0.0/8', type=1)
        net_for_slice.save()


@receiver(post_syncdb, sender=models)
def init_network_for_phy(sender, **kwargs):
    if not models.Network.objects.filter(type=0):
        net_for_phy = models.Network(netaddr='172.16.0.0/16', type=0)
        net_for_phy.save()
