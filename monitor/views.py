# coding:utf-8
import json

from plugins.common.agent_client import AgentClient
from django.http import HttpResponse, HttpResponseRedirect,Http404
from django.shortcuts import render, get_object_or_404, redirect
from resources.models import Server

import random
def monitor_vm(request, host_id, vm_id):
    print host_id
    return render(request, "slice/monitor.html", {'host_id' : host_id})

def monitor_host(request, host_id):
    return render(request, "monitor.html", {'host_id' : host_id, "vm_id" : 0})

def monitor_ovs(request, host_id):
    return HttpResponse(json.dumps([{'br_name' : 'br0', 'ports' : ['eth0', 'eth1']}
                                    ,{'br_name' : 'br1', 'ports' : ['eth2', 'eth3'] }]))

def monitor_port(request):
    performace_port_data = {'port_recv_data' : random.randint(50,200), 'port_send_data' : random.randint(1, 100)}
    return HttpResponse(json.dumps(performace_port_data))

performace_data = {'cpu_use' : random.randint(1, 100),
                   'mem_use' : random.randint(1, 100),
                   'net_recv_data' : random.randint(1, 100),
                   'net_send_data' : random.randint(1, 100),
                   'disk_use' : random.randint(1, 100)}

def update_vm_performace_data(request):
    """
    监控虚拟机性能
    """
    pre_net_data = request.POST.get("pre_net_data").split(',')
    vm_name = request.POST.get("vm_name")
    agent_ip = request.POST.get("server_ip")
    agent = AgentClient(ip = "192.168.5.122")
    vm_perf_data = json.loads(agent.get_domain_status("4f6f91d4-2af5-481d-afc6-8217c70db938"))

    #print host_perf_data







    # vm_perf_data = {"mem": {"total": 262144, "percent": 100, "free": 0, "used": 262144},
    # "net": {"4f6f91d4": [5522, 984, 7080755, 12, 0, 0, 0, 0],
    #        "4f6f91d5": [123, 84, 0755, 12, 0, 0, 0, 0]},
    #"disk": {"total": 858993459200.0, "percent": 0.067138671875, "free": 8416742400.0, "used": 576716800.0},
    #"cpu": 0.0}
    net_data = {}
    if pre_net_data[0] == '':
        for (key, value) in host_perf_data["net"].items():
            net_data[key] = [value[0], value[1], 0, 0]
    else:
        for (key, value), bps_data in zip(host_perf_data["net"].items(), pre_net_data):
            net_data[key] = [value[0], value[1],
                           value[0] - int(bps_data.split(':')[0]),
                           value[1] - int(bps_data.split(':')[1])]
                            #200, 300]

    for (key, value) in host_perf_data["disk"].items():
        host_disk_data = {"free" : int(value[2])/8/1024/1024, "used" : int(value[1]/8/1024/1024)}
        break

    domain_disk_data = {"free" : int(vm_perf_data["disk"]["free"]/8/1024/1024), "used" : int(vm_perf_data["disk"]["used"]/8/1024/1024)}
    #print net_data
    return HttpResponse(json.dumps({'cpu_use' : vm_perf_data["cpu"],
                                    'mem_use' : vm_perf_data["mem"]["percent"],
                                    'net' : net_data,
                                    'disk_use' : host_disk_data
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
        host_disk_data = {"free" : int(value[2])/8/1024/1024, "used" : int(value[1]/8/1024/1024)}
        break

    return HttpResponse(json.dumps({'cpu_use' : host_perf_data["cpu"],
                                    'mem_use' : host_perf_data["mem"][2],
                                    'net' : net_data,
                                    'disk_use' : host_disk_data
                                    }))
