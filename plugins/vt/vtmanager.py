#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename:vtmanager.py
# Date:Sun Oct 06 01:40:50 CST 2013
# Author:Pengbo Li
# E-mail:lipengbo10054444@gmail.com
from plugins.common.agent_client import AgentClient
from plugins.common.exception import ResourceNotEnough
from resources.models import Server
from etc import config
import random
import json


class Filter(object):

    def __init__(self, vcpu, mem, disk):
        self.mem = int(mem)
        self.disk = int(disk)
        self.vcpu = int(vcpu)

    def check_resource_by_monitor(self, hostid, hostip):
        #try:
        client = AgentClient(hostip)
        host_status = json.loads(client.get_host_status())
        if not config.function_test:
            if config.unique_hosts_per_alloc <= client.get_instances_count():
                raise ResourceNotEnough('too many vms on this server')

                    #return False
            if self.vcpu > int(client.get_host_info()['vcpus']):
                raise ResourceNotEnough('multi-cores could not be supported')
                    #return False
            if config.max_cpu < float(host_status['cpu']):
                raise ResourceNotEnough('cpu overload')
                    #return False
            mem_free = float(host_status['mem'][1])
            mem_total = float(host_status['mem'][0])
            if config.max_mem < (mem_total - mem_free + (self.mem << 20)) * 100 / mem_total:
                raise ResourceNotEnough('mem overload')
                    #return False
                #if config.max_disk != 0:
                    #disk_free = int(host_status['disk'].items()[0][1][2])
                    #if config.max_disk > (disk_free >> 30) - self.disk:
                        #return False
        #except:
         #   return False
        return hostid

    def check_resource_by_db(self, host):
        if not config.function_test:
            vms = host.virtualmachine_set.all()
            if config.unique_hosts_per_alloc <= len(vms):
                return False
            if self.vcpu > int(host.cpu.split()[1]):
                return False
            mem_total = float(host.mem)
            mem_used = 0
            for vm in vms:
                mem_used = mem_used + vm.ram
            if config.max_mem < (mem_used + self.mem) * 100 / mem_total:
                return False
        return host.id

    def filter(self, host_list):
        random.shuffle(host_list)
        for hostid, hostip in host_list:
            host = Server.objects.get(id=hostid)
            if config.use_vt_manager_to_schedul:
                if host.state and self.check_resource_by_monitor(hostid, hostip):
                    return hostid
            else:
                if host.state and self.check_resource_by_db(host):
                    return hostid
        #return False
