#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename:glance.py
# Date:Tue Jul 09 02:36:49 CST 2013
# Author:Pengbo Li
# E-mail:lipengbo10054444@gmail.com
import utils
from etc import config


def get_image_list():
    glance_url = config.generate_glance_url()
    try:
        out = utils.execute(['glance', '-U', glance_url, 'index'])
    except:
        #Try it again
        out = utils.execute(['glance', '-U', glance_url, 'index'])
    for line in out.splitlines():
        if (not "----" in line) and (not "ID" in line):
            lineList = line.split()
            uuid = lineList[0].strip()
            name = lineList[1].strip()
            yield uuid, name, '%s/image/%s' % (glance_url, uuid)
