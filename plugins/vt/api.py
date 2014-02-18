#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename:api.py
# Date:Sat Oct 05 00:10:59 CST 2013
# Author:Pengbo Li
# E-mail:lipengbo10054444@gmail.com
from plugins.vt.models import VirtualMachine, Image, Flavor, DOMAIN_STATE_DIC
from plugins.ipam.models import IPUsage, Subnet
from etc.config import default_flavor_id
from plugins.common.vt_manager_client import VTClient
from plugins.common.exception import ResourceNotEnough, ConnectionRefused, FailedToAllocateResources
from resources.models import Server
from etc.config import function_test
import errno, traceback, logging
from socket import error as socket_error
LOG = logging.getLogger("plugins")

def create_vm_for_controller(island_obj, slice_obj, image_name):
    try:
        ip_obj = IPUsage.objects.allocate_ip_for_controller(island=island_obj)
        vm = VirtualMachine(slice=slice_obj, island=island_obj, ip=ip_obj)
        vm.name = image_name
        images = Image.objects.filter(name=image_name)
        if images:
            vm.image = images[0]
        vm.flavor = Flavor.objects.get(id=default_flavor_id)
        if function_test:
            hostlist = Server.objects.filter(island=island_obj)
            vm.server = hostlist[0]
        else:
            hostlist = [(server.id, server.ip) for server in Server.objects.filter(island=island_obj)]
            serverid = VTClient().schedul(vm.flavor.cpu, vm.flavor.ram, vm.flavor.hdd, hostlist)
            if not serverid:
                raise ResourceNotEnough()
            vm.server = Server.objects.get(id=serverid)
        vm.type = 0
        vm.save()
    except socket_error as serr:
        if ip_obj:
            IPUsage.objects.release_ip(ip_obj)
        if serr.errno == errno.ECONNREFUSED or serr.errno == errno.EHOSTUNREACH:
            raise ConnectionRefused()
    except ResourceNotEnough:
        if ip_obj:
            IPUsage.objects.release_ip(ip_obj)
        raise ResourceNotEnough()
    except:
        if ip_obj:
            IPUsage.objects.release_ip(ip_obj)
        raise FailedToAllocateResources()
    finally:
        LOG.error(traceback.print_exc())
    return vm, str(ip_obj)


def delete_vm_for_controller(vm):
    vm.delete()

def create_vm_for_gateway(island_obj, slice_obj, server_id, image_name='gateway', enable_dhcp=True):
    try:
        ip_obj = IPUsage.objects.allocate_ip(slice_obj.uuid)
        gateway_public_ip_obj = IPUsage.objects.allocate_ip_for_gw(island=island_obj)
        vm = VirtualMachine(slice=slice_obj, island=island_obj, gateway_public_ip=gateway_public_ip_obj, ip=ip_obj)
        vm.name = image_name
        vm.enable_dhcp = enable_dhcp
        images = Image.objects.filter(name=image_name)
        if images:
            vm.image = images[0]
        vm.flavor = Flavor.objects.get(id=default_flavor_id)
        host_server = Server.objects.get(id=server_id)
        if function_test:
            vm.server = host_server
        else:
            hostlist = [(host_server.id, host_server.ip)]
            serverid = VTClient().schedul(vm.flavor.cpu, vm.flavor.ram, vm.flavor.hdd, hostlist)
            if not serverid:
                raise ResourceNotEnough()
            vm.server = Server.objects.get(id=serverid)
        vm.type = 2
        vm.save()
    except socket_error as serr:
        if ip_obj:
            IPUsage.objects.release_ip(ip_obj)
        if serr.errno == errno.ECONNREFUSED or serr.errno == errno.EHOSTUNREACH:
            raise ConnectionRefused()
    except ResourceNotEnough:
        if ip_obj:
            IPUsage.objects.release_ip(ip_obj)
        raise ResourceNotEnough()
    except:
        if ip_obj:
            IPUsage.objects.release_ip(ip_obj)
        raise FailedToAllocateResources()
    finally:
        LOG.error(traceback.print_exc())
    return vm


def delete_vm_for_gateway(vm):
    vm.delete()


def do_vm_action(vm, action):
    action_result = vm.do_action(action)
    if action_result:
        if action == "destroy":
            vm.state = DOMAIN_STATE_DIC['shutoff']
        else:
            vm.state = DOMAIN_STATE_DIC['running']
        result = True
    else:
        if action == "destroy":
            vm.state = DOMAIN_STATE_DIC['shutoff']
            result = True
        else:
            result = False
    if result = True:
        vm.save()
    return result


def get_slice_gw_mac(slice):
    gw_vm = VirtualMachine.objects.get(slice=slice, type=2)
    return gw_vm.get_gw_mac()


def get_slice_gw_ip(slice):
    gw_vm = VirtualMachine.objects.get(slice=slice, type=2)
    return gw_vm.gateway_public_ip


def get_phydata_gw_mac(island):
    owner = 'island_%s_2' % island.id
    net = Subnet.objects.get(owner=owner)
    return net.get_gateway_mac()


def get_phydata_gw_ip(island):
    owner = 'island_%s_2' % island.id
    net = Subnet.objects.get(owner=owner)
    return net.get_gateway_ip()


def try_start_gw_and_ctr(vm):
    if vm.type != 1:
        try:
            return do_vm_action(vm, 'create')
        except:
            return False
