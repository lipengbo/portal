#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename:__init__.py
# Date:Fri Sep 13 14:50:28 CST 2013
# Author:Pengbo Li
# E-mail:lipengbo10054444@gmail.com
from netaddr.core import AddrConversionError, AddrFormatError, \
    NotRegisteredError, ZEROFILL, Z, INET_PTON, P, NOHOST, N

from netaddr.ip import IPAddress, IPNetwork, IPRange, all_matching_cidrs, \
    cidr_abbrev_to_verbose, cidr_exclude, cidr_merge, iprange_to_cidrs, \
    iter_iprange, iter_unique_ips, largest_matching_cidr, \
    smallest_matching_cidr, spanning_cidr

from netaddr.ip.sets import IPSet

from netaddr.ip.glob import IPGlob, cidr_to_glob, glob_to_cidrs, \
    glob_to_iprange, glob_to_iptuple, iprange_to_globs, valid_glob

from netaddr.ip.nmap import valid_nmap_range, iter_nmap_range

from netaddr.ip.rfc1924 import base85_to_ipv6, ipv6_to_base85

from netaddr.eui import EUI, IAB, OUI

from netaddr.strategy.ipv4 import valid_str as valid_ipv4

from netaddr.strategy.ipv6 import valid_str as valid_ipv6, ipv6_compact, \
    ipv6_full, ipv6_verbose

from netaddr.strategy.eui48 import mac_eui48, mac_unix, mac_cisco, \
    mac_bare, mac_pgsql, valid_str as valid_mac

__all__ = [
    #   Constants.
    'ZEROFILL', 'Z', 'INET_PTON', 'P', 'NOHOST', 'N',

    #   Custom Exceptions.
    'AddrConversionError', 'AddrFormatError', 'NotRegisteredError',

    #   IP classes.
    'IPAddress', 'IPNetwork', 'IPRange', 'IPSet',

    #   IPv6 dialect classes.
    'ipv6_compact', 'ipv6_full', 'ipv6_verbose',

    #   IP functions and generators.
    'all_matching_cidrs', 'cidr_abbrev_to_verbose', 'cidr_exclude',
    'cidr_merge', 'iprange_to_cidrs', 'iter_iprange', 'iter_unique_ips',
    'largest_matching_cidr', 'smallest_matching_cidr', 'spanning_cidr',

    #   IP globbing class.
    'IPGlob',

    #   IP globbing functions.
    'cidr_to_glob', 'glob_to_cidrs', 'glob_to_iprange', 'glob_to_iptuple',
    'iprange_to_globs',

    #   IEEE EUI classes.
    'EUI', 'IAB', 'OUI',

    #   EUI-48 (MAC) dialect classes.
    'mac_bare', 'mac_cisco', 'mac_eui48', 'mac_pgsql', 'mac_unix',

    #   Validation functions.
    'valid_ipv4', 'valid_ipv6', 'valid_glob', 'valid_mac',

    #   nmap-style range functions.
    'valid_nmap_range', 'iter_nmap_range',

    #   RFC 1924 functions.
    'base85_to_ipv6', 'ipv6_to_base85',
]


class Network(object):

    def __init__(self, ipaddr):
        """
        ipaddr : must use cidr format,such as '10.0.0.0/8'
        """
        self.netaddr = IPNetwork(ipaddr)
        self.sub64_prefix = 26
        self.sub32_prefix = 27
        self.sub16_prefix = 28
        self.sub8_prefix = 29

    def subnet(self, ipcount):
        function = '_sub_net_%s' % ipcount
        return getattr(self, function)()

    def _sub_net_64(self):
        for sub64_net in self.netaddr.subnet(self.sub64_prefix):
            yield sub64_net

    def _sub_net_32(self):
        for sub32_net in self.netaddr.subnet(self.sub32_prefix):
            yield sub32_net

    def _sub_net_16(self):
        for sub16_net in self.netaddr.subnet(self.sub16_prefix):
            yield sub16_net

    def _sub_net_8(self):
        for sub8_net in self.netaddr.subnet(self.sub8_prefix):
            yield sub8_net
