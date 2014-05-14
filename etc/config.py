#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename:config.py
# Date:Sun Sep 22 00:30:02 CST 2013
# Author:Pengbo Li
# E-mail:lipengbo10054444@gmail.com
#[plugin-vt]
glance_host = '192.168.5.111'
glance_port = 9292
sFlow_service = 'http://192.168.5.24:8008/'

#[agent-service]
compute_service_port = 8886
monitor_service_port = 8887
ovs_service_port = 8889
vpn_service_port = 8890


def generate_glance_url():
    """Generate the URL to glance."""
    return "http://%s:%d/v1" % (glance_host, glance_port)


#[plugin-advance]
#高级配置项，用于配置文件锁的位置
lock_path = '/var/run/'
#控制器和网关模板
controller_flavor_id = 1
gateway_flavor_id = 1
rpc_connection_timeout = 150
domain_count_infinity = 10000
#配置slice的网关与物理网关的通信方式，True表示通过slice控制器控制（下相应flowspace），False表示不通过控制器控制。
gw_controller = False
#slice的过期时间，以天为单位（正整数），若输入格式错误，默认为30天
slice_expiration_days = 5
#单元测试的时候使用，当系统发布的时候该值必须为False
function_test = False
#配置系统是否使用flowvisor，当系统发布的时候该值必须为False
flowvisor_disable = True
#直接调度底层资源判断，发布时设置为True
#[scheduler]只有在use_vt_manager_to_schedul = False时才生效
use_vt_manager_to_schedul = True
#单台机器最多允许创建的虚拟机的数量
unique_hosts_per_alloc = 100
#可以创建虚拟机的主机，cpu、mem的最大负载，取值为百分必的形式，如下代表百分之80
max_cpu = 100
max_mem = 100
#可以创建虚拟机的主机，至少要有10G的磁盘剩余
max_disk = 0
#[vt_manager]只有在use_vt_manager_to_schedul = True时才生效
vt_manager_ip = '127.0.0.1'
vt_manager_port = 8891
#aes字符长度必须为16位
aes_key = 'fnic123456789012'
try:
    from etc.local_config import *
except ImportError:
    pass
