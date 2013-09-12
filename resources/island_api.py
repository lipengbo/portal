# coding:utf-8
from models import *
import logging
LOG = logging.getLogger("CENI")


def get_island_ovss(island):
    """获取island所有交换机
    """
    LOG.debug('island_get_ovs')
    try:
        ovs_ids = []
        island_ovss = ceni_island_facility.objects.filter(
            island_id=island.id, facility_type=2)
        for island_ovs in island_ovss:
            ovs_ids.append(island_ovs.facility_id)
        ovss = ceni_facility_server.objects.filter(id__in=ovs_ids)
        return ovss
    except:
        return []
