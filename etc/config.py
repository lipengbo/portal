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
function_test = True
flowvisor_disable = True
use_vt_manager_to_schedul = False
#[scheduler]只有在use_vt_manager_to_schedul = False时才生效
#单台机器最多允许创建的虚拟机的数量
unique_hosts_per_alloc = 10
#可以创建虚拟机的主机，cpu、mem的最大负载，取值为百分必的形式，如下代表百分之80
max_cpu = 80
max_mem = 80
#可以创建虚拟机的主机，至少要有10G的磁盘剩余
max_disk = 10
