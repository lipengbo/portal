#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename:sflow_proxy.py
# Date:五 12月 27 17:20:22 CST 2013
# Author:Pengbo Li
# E-mail:lipengbo10054444@gmail.com
import json
from etc.config import sFlow_service
from plugins.common import utils


class SFlow_Proxy(object):

    @staticmethod
    def has_flow_event(name):
        url = sFlow_service + 'flow/json'
        cmd = "curl " + url
        out, err = utils.execute(cmd)
        out = json.loads(out)
        return out.get(name.lower(), False)

    @staticmethod
    def set_sFlow_metric_event(dpid, ofport, maclist):
        for mac in maclist:
            #url = sFlow_service + 'flow/' + \
                #'%s_%s_%s_in' % (dpid, ofport, mac) + '/json'
            header = "\"Content-Type:application/json\""
            #data = "\"{keys:'ipsource,ipdestination',value:'bytes',filter:'macdestination=%s'}\"" % mac
            #in_cmd = "curl -H " + header + \
                #" -X PUT --data " + data + " " + url
            name = '%s_%s_%s_out' % (dpid, ofport, mac)
            if SFlow_Proxy.has_flow_event(name):
                continue
            else:
                url = sFlow_service + 'flow/' + name + '/json'
                data = "\"{keys:'ipsource,ipdestination',value:'bytes',filter:'macsource=%s'}\"" % mac
                out_cmd = "curl -H " + header + \
                    " -X PUT --data " + data + " " + url
                #utils.execute(in_cmd)
                utils.execute(out_cmd)

    @staticmethod
    def get_sFlow_metric_event(agentip, dpid, ofport, maclist):
        ifindex = SFlow_Proxy.get_ifindex_by_ofport(dpid, ofport)
        ifspeed = 0
        if_used_speed = 0
        for mac in maclist:
            #url = sFlow_service + 'metric/' + agentip + "/" + '%s_%s_%s_in' % (dpid, ofport, mac) + '/json'
            #in_cmd = "curl " + url
            #url = sFlow_service + 'metric/' + agentip + "/" + '%s_%s_%s_out' % (dpid, ofport, mac) + '/json'
            uri = '%s_%s_%s_out' % (dpid, ofport, mac)
            #key = '%s.%s' % (ifindex, uri)
            url = sFlow_service + 'metric/' + agentip + '/' + uri + '/json'
            out_cmd = "curl " + url
            out, err = utils.execute(out_cmd)
            out = json.loads(out)
            out_speed = out[0].get('metricValue', 0)
            if_used_speed = if_used_speed + out_speed
        url = sFlow_service + 'metric/' + agentip + '/json'
        out_cmd = "curl " + url
        #out, err = utils.execute(in_cmd)
        out, err = utils.execute(out_cmd)
        out = json.loads(out)
        if not ifspeed:
            ifspeed = out.get('%s.ifspeed' % ifindex, None)
        return ifspeed, if_used_speed

    @staticmethod
    def get_mac_by_switch_port(switch_port):
        pass
