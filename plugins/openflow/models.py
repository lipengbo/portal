from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.db.models import F

from resources.models import ServiceResource, Resource, SwitchPort, Switch
from slice.models import Slice


class Controller(ServiceResource):
    is_root = models.BooleanField(default=False)

    def on_add_into_slice(self, slice_obj):
        self.slices.add(slice_obj)

    def is_used(self):
        return self.slices.all().count() > 0


class Flowvisor(ServiceResource):
    def on_add_into_slice(self, slice_obj):
        self.slices.add(slice_obj)


class FlowSpaceRule(Resource):
    slice = models.ForeignKey(Slice)
    switch = models.ForeignKey(Switch, null=True)
    priority = models.IntegerField()
    in_port = models.CharField(max_length=256)
    dl_vlan = models.CharField(max_length=256)
    dl_vpcp = models.CharField(max_length=256)
    dl_src = models.CharField(max_length=256)
    dl_dst = models.CharField(max_length=256)
    dl_type = models.CharField(max_length=256)
    nw_src = models.CharField(max_length=256)
    nw_dst = models.CharField(max_length=256)
    nw_proto = models.CharField(max_length=256)
    nw_tos = models.CharField(max_length=256)
    tp_src = models.CharField(max_length=256)
    tp_dst = models.CharField(max_length=256)
    is_default = models.IntegerField()
    actions = models.CharField(max_length=256)

class Link(models.Model):

    flowvisor = models.ForeignKey(Flowvisor)
    source = models.ForeignKey(SwitchPort, related_name="source_links")
    target = models.ForeignKey(SwitchPort, related_name="target_links")
