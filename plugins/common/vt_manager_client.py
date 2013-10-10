#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename:agentclient.py
# Date:Sat Oct 05 18:13:35 CST 2013
# Author:Pengbo Li
# E-mail:lipengbo10054444@gmail.com
from xmlrpcclient import get_rpc_client
from etc import config


class VTClient(object):
    def __init__(self, ip=config.vt_manager_ip):
        self.client = get_rpc_client(ip, config.vt_manager_port)

    def schedul(self, vcpu, mem, disk, hostlist):
        return self.client.schedul(vcpu, mem, disk, hostlist)

    def do_domain_action(self, hostip, vname, action):
        return self.client.do_domain_action(hostip, vname, action)

    def create_vm(self, hostip, vmInfo, netInfo):
        """
        vmInfo:
            {
                'name': name,
                'mem': mem,
                'cpus': cpus,
                'img': imageUUID,
                'mac': mac,
                'hdd': imageSize 2G,
                'dhcp': 1 or 0,
                'glanceURL': glanceURL,
                'type':0/1/2 0 controller 1 slice 2 gateway
            }
        netInfo:
            {
                'ip': address,
                'netmask': netmask,
                'broadcast': broadcast,
                'gateway': gateway,
                'dns': dns,
            }
        """
        return self.client.create_vm(hostip, vmInfo, netInfo)

    def delete_vm(self, hostip, vname):
        return self.client.delete_vm(hostip, vname)

    def get_host_info(self, hostip):
        return self.client.get_host_info(hostip)
