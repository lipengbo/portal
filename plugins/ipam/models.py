#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename:models.py
# Date:Fri Sep 20 18:36:12 CST 2013
# Author:Pengbo Li
# E-mail:lipengbo10054444@gmail.com
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils.translation import ugettext as _
from plugins.ipam import netaddr as na


class IPManager(models.Manager):

    def create_subnet(self, owner):
        supernet = Network.objects.get(type=1)
        all_subnets = Subnet.objects.filter(supernet=supernet)
        unused_subnets = all_subnets.filter(is_used=False)
        if all_subnets:
            if unused_subnets:
                new_subnet_addr = unused_subnets[0]
                new_subnet_addr.owner = owner
                new_subnet_addr.is_used = True
                new_subnet_addr.save()
                return new_subnet_addr.netaddr
            else:
                new_subnet_addr = all_subnets[0].get_next()
        else:
            new_subnet_addr = supernet.first_subnet()
        result = Subnet(supernet=supernet, netaddr=new_subnet_addr, owner=owner, is_used=True)
        result.save()
        return result.netaddr

    def delete_subnet(self, owner):
        subnet = Subnet.objects.get(owner=owner)
        subnet.is_used = False
        subnet.owner = None
        subnet.save()
        return True

    def allocate_ip(self, owner):
        supernet = Subnet.objects.get(owner=owner)
        all_hosts = supernet.get_hosts()
        used_hosts = self.get_used_hosts(owner)
        free_hosts = list(set(all_hosts) - set(used_hosts))
        if free_hosts:
            ipaddr = free_hosts[0]
            ip = IPUsage(supernet=supernet, ipaddr=ipaddr)
            ip.save()
            return ip

    def release_ip(self, ip):
        ip.delete()
        return True

    def get_used_hosts(self, owner):
        subnet = Subnet.objects.get(owner=owner)
        return map(lambda x: x.ipaddr, self.filter(supernet=subnet))

    def get_subnet(self, owner):
        result = Subnet.objects.get(owner=owner)
        return result.netaddr


class Network(models.Model):
    TYPE_CHOICE = ((0, _('subnet for phy')),
                  (1, _('subnet for slice')),)
    netaddr = models.GenericIPAddressField(null=False, unique=True)
    type = models.IntegerField(null=False, choices=TYPE_CHOICE)

    def __init__(self, *args, **kwargs):
        super(Network, self).__init__(*args, **kwargs)
        self.na_Network = na.Network(self.netaddr)

    def subnet(self):
        return self.na_Network.subnet(ipcount=64)

    def first_subnet(self):
        return [str(first_sub) for first_sub in self.na_Network.subnet(ipcount=64, count=1)][0]

    def __unicode__(self):
        return self.netaddr

    class Meta:
        ordering = ['-id', ]


class Subnet(models.Model):
    supernet = models.ForeignKey(Network)
    netaddr = models.IPAddressField(null=False, unique=True)
    owner = models.CharField(max_length=20, null=True, unique=True)
    is_used = models.BooleanField(default=False)

    def __init__(self, *args, **kwargs):
        super(Subnet, self).__init__(*args, **kwargs)
        self.na_IPNetwork = na.IPNetwork(self.netaddr)

    def get_netmask(self):
        return str(self.na_IPNetwork.netmask)

    def get_network(self):
        return str(self.na_IPNetwork.network)

    def get_next(self):
        next_sub = self.na_IPNetwork.next()
        if na.IPNetwork(self.supernet.netaddr) in next_sub.supernet():
            return str(next_sub)

    def get_previous(self):
        pre_sub = self.na_IPNetwork.previous()
        if self.na_IPNetwork in pre_sub.supernet():
            return str(pre_sub)

    def get_size(self):
        return self.na_IPNetwork.size

    def get_prefixlen(self):
        return self.na_IPNetwork.prefixlen

    def get_cidr(self):
        return str(self.na_IPNetwork.cidr)

    def get_broadcast(self):
        return str(self.na_IPNetwork.broadcast)

    def get_first(self):
        first_value = self.na_IPNetwork.first
        return first_value

    def get_last(self):
        last_value = self.na_IPNetwork.last
        return last_value

    def get_value(self):
        return self.na_IPNetwork.value

    def iter_hosts(self):
        return self.na_IPNetwork.iter_hosts()

    def get_hosts(self):
        hosts = [str(host) for host in self.iter_hosts()]
        return hosts

    def __unicode__(self):
        return self.netaddr

    class Meta:
        ordering = ['-id', ]


class IPUsage(models.Model):
    supernet = models.ForeignKey(Subnet)
    ipaddr = models.IPAddressField(null=False, unique=True)
    objects = IPManager()

    def __unicode__(self):
        return self.ipaddr

    class Meta:
        ordering = ['-id', ]


@receiver(post_save, sender=Network)
def create_base_subnet(sender, instance, **kwargs):
    network = instance
    if kwargs.get('created'):
        if network.type == 0:
            Subnet(supernet=network, netaddr=network.netaddr, owner=0, is_used=True).save()
