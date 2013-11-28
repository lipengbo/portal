# coding:utf-8
import json
import errno
from socket import error as socket_error
from django.utils.translation import ugettext as _
from plugins.common.agent_client import AgentClient
from plugins.common.ovs_client import get_bridge_list, get_bridge_port_list,get_switch_stat
from django.http import HttpResponse, HttpResponseRedirect,Http404
from django.shortcuts import render, get_object_or_404, redirect
from resources.models import Server, Switch
from plugins.vt.models import VirtualMachine




def monitor_vm(request, vm_id):
    vm = get_object_or_404(VirtualMachine, id=vm_id)
    return render(request, "monitor_host_or_vm.html",
                  {'host_id' : vm.server.id, "vm_id" : vm_id,
                   "slice_id": vm.slice.id, "project_id" : vm.slice.project.id})

def monitor_host(request, host_id):
    return render(request, "monitor_host_or_vm.html", {'host_id' : host_id, "vm_id" : 0})

def monitor_switch(request, switch_id):
    switch = get_object_or_404(Switch, id=switch_id)
    return render(request, "monitor_switch.html", {'switch_id' : switch_id,
                                                   'switch_name' : switch.name})


def get_br_info(request, switch_id):
    switch = get_object_or_404(Switch, id = switch_id)
    br_info = []
    for br in get_bridge_list(switch.ip):
        br_dict = {'br_name' : '', 'ports' : []}
        br_dict['br_name'] = br
        for port in get_bridge_port_list(switch.ip, br):
            br_dict['ports'].append(port)
        if len(br_dict['ports']) > 0:
            br_info.append(br_dict)
    return HttpResponse(json.dumps(br_info))



def update_port_performace_data(request):
    switch_id = request.POST.get("switch_id")
    br_name = request.POST.get("br")
    port_name = request.POST.get("port")
    pre_recv_data = request.POST.get("pre_recv_data")
    pre_send_data = request.POST.get("pre_send_data")
    try:
        switch = get_object_or_404(Switch, id = switch_id)
        switch_stat = get_switch_stat(switch.ip)
        for br in switch_stat:
            if br['name'] == br_name:
                for port in br['ports']:
                    if port['name'] == port_name:
                        print port_name
                        print "----------------------------"
                        print "pre_recv_data = ", pre_recv_data
                        print "pre_send_data = ", pre_send_data
                        recv_data = int(port['stats']['recv']['byte'])
                        send_data = int(port['stats']['send']['byte'])
                        print "recv_data =", recv_data
                        print "send_data =", send_data
        recv_bps = recv_data - int(pre_recv_data)
        send_bps = send_data - int(pre_send_data)
        #在不同网卡间切换的时候，得到的数据差值有可能为负，故做此处理
        if recv_bps < 0 :
            recv_bps = 0
        if send_bps < 0 :
            send_bps = 0
        performace_port_data = {'port_recv_data' : recv_data, 'port_send_data' : send_data,
                            'recv_bps' : recv_bps, 'send_bps' : send_bps}
    except socket_error as serr:
        if serr.errno == errno.ECONNREFUSED:
            return HttpResponse(json.dumps({'result': 1, 'error': _("connection refused")}))
    except:
            return HttpResponse(json.dumps({'result': 1, 'error': _("server error")}))
    return HttpResponse(json.dumps(performace_port_data))

def get_switch_port_info(request, switch_id):
    pre_port_data = None
    if request.method == 'POST':
        pre_port_data = json.loads(request.POST.get("pre_port_data"))
        print "===>", pre_port_data['eth1']

    try:
        switch = get_object_or_404(Switch, id=switch_id)
        switch_stat = get_switch_stat(switch.ip)
        #ports_info = []
        print "---------------------------"
        port_info = {}
        for br in switch_stat:
            for port in br['ports']:
                print port['name']
                recv_data = int(port['stats']['recv']['byte'])
                send_data = int(port['stats']['recv']['byte'])
                if pre_port_data:
                    print "minus===="
                    recv_bps = recv_data - int(pre_port_data[port['name']][0])
                    send_bps = send_data - int(pre_port_data[port['name']][1])
                else:
                    recv_bps = 0
                    send_bps = 0
                port_info[port['name']] = [recv_data, send_data, recv_bps, send_bps]
            #ports_info.append(port_info)
            break
        print port_info
        print "---------------------------"
    except:
        pass
    return HttpResponse(json.dumps(port_info))

def update_vm_performace_data(request):
    """
    监控虚拟机性能
    """
    pre_net_data = request.POST.get("pre_net_data").split(',')
    vm_id = request.POST.get("vm_id")
    try:
        vm = get_object_or_404(VirtualMachine, id = vm_id )
        agent_ip = vm.server.ip
        agent = AgentClient(ip = agent_ip)
        vm_perf_data = json.loads(agent.get_domain_status(vm.uuid))
        net_data = {}
        if pre_net_data[0] == '':
            for (key, value) in vm_perf_data["net"].items():
                net_data[key] = [value[0], value[1], 0, 0]
        else:
            for (key, value), bps_data in zip(vm_perf_data["net"].items(), pre_net_data):
                bps_recv = value[0] - int(bps_data.split(':')[0])
                bps_send = value[1] - int(bps_data.split(':')[1])

                if bps_recv < 0:
                    bps_recv = 0
                if bps_send < 0:
                    bps_send = 0
                net_data[key] = [value[0], value[1], bps_recv, bps_send]


        domain_disk_data = {"free" : int(vm_perf_data["disk"]["free"]),
                        "used" : int(vm_perf_data["disk"]["used"])}
    except socket_error as serr:
        if serr.errno == errno.ECONNREFUSED:
            return HttpResponse(json.dumps({'result': 1, 'error': _("connection refused")}))
    except:
            return HttpResponse(json.dumps({'result': 1, 'error': _("server error")}))

    return HttpResponse(json.dumps({'cpu_use' : vm_perf_data["cpu"],
                                    'mem_use' : vm_perf_data["mem"]["percent"],
                                    'net' : net_data,
                                    'disk_use' : domain_disk_data
                                    }))

def update_host_performace_data(request):
    host_id = request.POST.get("host_id")
    pre_net_data = request.POST.get("pre_net_data").split(',')
    try:
        server = get_object_or_404(Server, id = host_id)
        agent = AgentClient(ip = server.ip)
        host_perf_data = json.loads(agent.get_host_status())
        #print host_perf_data
        net_data = {}
        if pre_net_data[0] == '':
            for (key, value) in host_perf_data["net"].items():
                net_data[key] = [value[0], value[1], 0, 0]
        else:
            for (key, value), bps_data in zip(host_perf_data["net"].items(), pre_net_data):
                bps_recv = value[0] - int(bps_data.split(':')[0])
                bps_send = value[1] - int(bps_data.split(':')[1])

                if bps_recv < 0:
                   bps_recv = 0
                if bps_send < 0:
                    bps_send = 0
                net_data[key] = [value[0], value[1], bps_recv, bps_send]

        for (key, value) in host_perf_data["disk"].items():
            host_disk_data = {"free" : int(value[2]), "used" : int(value[1])}
            break
    except socket_error as serr:
        if serr.errno == errno.ECONNREFUSED:
            return HttpResponse(json.dumps({'result': 1, 'error': _("connection refused")}))
    except:
            return HttpResponse(json.dumps({'result': 1, 'error': _("server error")}))



    return HttpResponse(json.dumps({'cpu_use' : host_perf_data["cpu"],
                                    'mem_use' : host_perf_data["mem"][2],
                                    'net' : net_data,
                                    'disk_use' : host_disk_data
                                    }))


def update_index_performace_data(request):
    host_id = request.POST.get("host_id")
    server = get_object_or_404(Server, id = host_id)
    agent = AgentClient(ip = server.ip)
    host_perf_data = json.loads(agent.get_host_status())
    return HttpResponse(json.dumps({'cpu_use' : host_perf_data['cpu'],
                                    'mem_use' : host_perf_data['mem'][2]}))

