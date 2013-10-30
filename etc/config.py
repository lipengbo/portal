#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename:config.py
# Date:Sun Sep 22 00:30:02 CST 2013
# Author:Pengbo Li
# E-mail:lipengbo10054444@gmail.com
#[plugin-vt]
glance_host = '192.168.5.107'
glance_port = 9292
vnctunnel = '127.0.0.1'
vt_manager_ip = '127.0.0.1'
vt_manager_port = 8891

#[agent-service]
compute_service_port = 8886
monitor_service_port = 8887
ovs_service_port = 8889


def generate_glance_url():
    """Generate the URL to glance."""
    return "http://%s:%d/v1" % (glance_host, glance_port)


#[plugin-advance]
#高级配置项，用于配置文件锁的位置
lock_path = '/var/run/'
default_flavor_id = 1
rpc_connection_timeout = 150
domain_count_infinity = 10000
#单元测试的时候使用，用于关闭一些特性，比如录入一台设备时自动获取其info信息
function_test = False
flowvisor_disable = True
