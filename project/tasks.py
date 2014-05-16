import json
from celery import task

from django.core.cache import cache

from project.models import Island
from plugins.common.agent_client import AgentClient

@task()
def check_resource_usage():
    islands = Island.objects.all()
    for island in islands:
        servers = island.server_set.all()
        switches = island.switch_set.all()
        server_ratios = []
        switch_ratios = []

        for server in servers:
            client = AgentClient(server.ip)
            try:
                host_status = json.loads(client.get_host_status(timeout=5))
            except Exception:
                pass
            else:
                ratio = (host_status['mem'][2] + host_status['cpu']) / 2
                server_ratios.append(ratio)

        for switch in switches:
            client = AgentClient(switch.ip)
            try:
                host_status = json.loads(client.get_host_status(timeout=5))
            except Exception:
                pass
            else:
                ratio = (host_status['mem'][2] + host_status['cpu']) / 2
                switch_ratios.append(ratio)

        print switch_ratios, server_ratios, island
        cache.set('island_{}_usage'.format(island.id), (switch_ratios, server_ratios))
        print cache.get('island_{}_usage'.format(island.id))

