#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename:config.py
# Date:Sun Sep 22 00:30:02 CST 2013
# Author:Pengbo Li
# E-mail:lipengbo10054444@gmail.com
#[plugin-vt]
glance_host = '192.168.5.107'
glance_port = 9292


def generate_glance_url():
    """Generate the URL to glance."""
    return "http://%s:%d" % (glance_host, glance_port)


#[plugin-advance]
#高级配置项，用于配置文件锁的位置
lock_path = '/var/run/'
