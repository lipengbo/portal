#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename:tests.py
# Date:Sat Sep 21 21:51:43 CST 2013
# Author:Pengbo Li
# E-mail:lipengbo10054444@gmail.com
from django.test import TestCase
from plugins.ipam.models import IPUsage
from plugins.ipam.models import Subnet
from plugins.common.utils import timefunc


class Slice_subnet_test(TestCase):

    def setUp(self):
        print "------set up--------"
        for i in xrange(1, 300):
            result = IPUsage.objects.create_subnet(owner=i)
            print result
            self.assertTrue(result)
            for j in xrange(1, 63):
                ip = IPUsage.objects.allocate_ip(owner=i)
                self.assertTrue('255.255.255.192' == ip.supernet.get_netmask())
                self.assertTrue(26 == ip.supernet.get_prefixlen())

    @timefunc
    def create_subnet(self, owner):
        result = IPUsage.objects.create_subnet(owner=owner)
        self.assertTrue(result)

    @timefunc
    def allocate_ip(self, owner):
        ip = IPUsage.objects.allocate_ip(owner=owner)
        self.assertTrue('255.255.255.192' == ip.supernet.get_netmask())
        self.assertTrue(26 == ip.supernet.get_prefixlen())
        return ip

    @timefunc
    def release_ip(self, ip):
        print "release ip = %s" % ip
        result = IPUsage.objects.release_ip(ip=ip)
        self.assertTrue(result)

    @timefunc
    def delete_subnet(self, owner):
        result = IPUsage.objects.delete_subnet(owner=owner)
        print "delete subnet = %s " % result
        self.assertTrue(result)

    def test_networkflow(self):
        self.create_subnet(owner=300)
        ip = self.allocate_ip(owner=300)
        self.release_ip(ip)
        self.delete_subnet(owner=299)

    def tearDown(self):
        print "------tear down--------"


class Phy_subnet_test(TestCase):

    def setUp(self):
        print "------set up--------"
        self.subnet = Subnet.objects.get(owner=0)
        print self.subnet
        self.assertTrue(self.subnet)

    @timefunc
    def allocate_ip(self, owner):
        ip = IPUsage.objects.allocate_ip(owner=owner)
        self.assertTrue('255.255.0.0' == ip.supernet.get_netmask())
        self.assertTrue(16 == ip.supernet.get_prefixlen())
        return ip

    @timefunc
    def release_ip(self, ip):
        print "release ip = %s" % ip
        result = IPUsage.objects.release_ip(ip=ip)
        self.assertTrue(result)

    def test_networkflow(self):
        for i in xrange(1, 3000):
            self.allocate_ip(owner=0)
            ip = self.allocate_ip(owner=0)
            self.release_ip(ip)

    def tearDown(self):
        print "------tear down--------"
