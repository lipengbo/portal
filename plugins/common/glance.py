#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename:glance.py
# Date:Tue Jul 09 02:36:49 CST 2013
# Author:Pengbo Li
# E-mail:lipengbo10054444@gmail.com
from etc.config import generate_glance_url
from plugins.common import glance_client_api


def image_delete(image_id):
    return glance_client_api.image_delete(generate_glance_url(), image_id)


def image_get(image_id):
    return glance_client_api.image_get(generate_glance_url(), image_id)


def image_list_detailed(marker=None, filters=None, paginate=False):
    return glance_client_api.image_list_detailed(generate_glance_url(), marker=marker, filters=filters, paginate=paginate)


def image_update(image_id, **kwargs):
    return glance_client_api.image_update(generate_glance_url(), image_id, **kwargs)


def image_create(**kwargs):
    return glance_client_api.image_create(generate_glance_url(), **kwargs)
