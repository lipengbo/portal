# coding:utf-8
import json

from plugins.common.agent_client import AgentClient
from plugins.common.ovs_client import get_bridge_list, get_bridge_port_list,get_switch_stat
from django.http import HttpResponse, HttpResponseRedirect,Http404
from django.shortcuts import render, get_object_or_404, redirect
from resources.models import Server, Switch
from plugins.vt.models import VirtualMachine




def monitor_vm(request, vm_id):
    vm = get_object_or_404(VirtualMachine, id=vm_id)
    return render(request, "monitor_host_or_vm.html",
                  {'host_id' : vm.server.id, "vm_id" : vm_id})

def monitor_host(request, host_id):
    return render(request, "monitor_host_or_vm.html", {'host_id' : host_id, "vm_id" : 0})

def monitor_switch(request, switch_id):
    return render(request, "monitor_switch.html", {'switch_id' : switch_id})


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

    switch = get_object_or_404(Switch, id = switch_id)
    switch_stat = get_switch_stat(switch.ip)
    recv_data = 0
    send_data = 0
    for br in switch_stat:
        if br['name'] == br_name:
            for port in br['ports']:
                if port['name'] == port_name:
                    recv_data = int(port['stats']['recv']['byte'])
                    send_data = int(port['stats']['send']['byte'])
    performace_port_data = {'port_recv_data' : recv_data, 'port_send_data' : send_data,
                            'recv_bps' : recv_data - int(pre_recv_data), 'send_bps' : send_data - int(pre_send_data)}
    return HttpResponse(json.dumps(performace_port_data))


def update_vm_performace_data(request):
    """
    监控虚拟机性能
    """
    pre_net_data = request.POST.get("pre_net_data").split(',')
    vm_id = request.POST.get("vm_id")
    vm = get_object_or_404(VirtualMachine, id = vm_id )
    agent_ip = vm.server.ip
    agent = AgentClient(ip = agent_ip)
    vm_perf_data = json.loads(agent.get_domain_status(vm.uuid))








    # vm_perf_data = {"mem": {"total": 262144, "percent": 100, "free": 0, "used": 262144},
    # "net": {"4f6f91d4": [5522, 984, 7080755, 12, 0, 0, 0, 0],
    #        "4f6f91d5": [123, 84, 0755, 12, 0, 0, 0, 0]},
    #"disk": {"total": 858993459200.0, "percent": 0.067138671875, "free": 8416742400.0, "used": 576716800.0},
    #"cpu": 0.0}
    net_data = {}
    if pre_net_data[0] == '':
        for (key, value) in vm_perf_data["net"].items():
            net_data[key] = [value[0], value[1], 0, 0]
    else:
        for (key, value), bps_data in zip(vm_perf_data["net"].items(), pre_net_data):
            net_data[key] = [value[0], value[1],
                           value[0] - int(bps_data.split(':')[0]),
                           value[1] - int(bps_data.split(':')[1])]
                            #200, 300]


    domain_disk_data = {"free" : int(vm_perf_data["disk"]["free"]),
                        "used" : int(vm_perf_data["disk"]["used"])}
    #print net_data
    return HttpResponse(json.dumps({'cpu_use' : vm_perf_data["cpu"],
                                    'mem_use' : vm_perf_data["mem"]["percent"],
                                    'net' : net_data,
                                    'disk_use' : domain_disk_data
                                    }))

def update_host_performace_data(request):
    host_id = request.POST.get("host_id")
    pre_net_data = request.POST.get("pre_net_data").split(',')
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
            net_data[key] = [value[0], value[1],
                           value[0] - int(bps_data.split(':')[0]),
                           value[1] - int(bps_data.split(':')[1])]

    for (key, value) in host_perf_data["disk"].items():
        host_disk_data = {"free" : int(value[2]), "used" : int(value[1])}
        break

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
