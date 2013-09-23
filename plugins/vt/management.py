#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename:management.py
# Date:Mon Sep 23 09:31:36 CST 2013
# Author:Pengbo Li
# E-mail:lipengbo10054444@gmail.com
from django.db.models.signals import post_syncdb
from django.dispatch import receiver
from plugins.common import glance
import models


@receiver(post_syncdb, sender=models)
def init_flavor(sender, **kwargs):
    if not models.Flavor.objects.all():
        flavor1 = models.Flavor(name='micro', cpu='1', ram='256', hdd='10')
        flavor2 = models.Flavor(name='mini', cpu='1', ram='512', hdd='20')
        flavor3 = models.Flavor(name='small', cpu='2', ram='1024', hdd='40')
        flavor4 = models.Flavor(name='medium', cpu='2', ram='2048', hdd='80')
        flavor5 = models.Flavor(name='large', cpu='4', ram='4096', hdd='160')
        flavor6 = models.Flavor(name='xlarge', cpu='6', ram='8192', hdd='320')
        flavor1.save()
        flavor2.save()
        flavor3.save()
        flavor4.save()
        flavor5.save()
        flavor6.save()


@receiver(post_syncdb, sender=models)
def init_image(sender, **kwargs):
    if not models.Image.objects.all():
        for uuid, name, url in glance.get_image_list():
            image = models.Image(uuid=uuid, name=name, url=url)
            image.save()
