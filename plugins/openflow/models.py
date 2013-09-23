import hashlib
import json

from django.db import models
from django.db import transaction
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.db.models import F
from django.dispatch import receiver

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

class FlowvisorLinksMd5(models.Model):
    md5 = models.CharField(max_length=32)
    flowvisor = models.OneToOneField(Flowvisor)

@transaction.commit_on_success
@receiver(post_save, sender=Flowvisor)
def update_links(sender, instance, created, **kwargs):
    from communication.flowvisor_client import FlowvisorClient

    client = FlowvisorClient(instance.ip, instance.http_port, instance.password)
    try:
        links = client.get_links()
    except Exception, e:
        print e
        return
    digest = hashlib.md5(json.dumps(links)).hexdigest()
    try:
        md5_obj = instance.flowvisorlinksmd5
        if md5_obj.md5 == digest: #: if the digests are the same, then no update
            return
        else: #: or update the md5 digest and do the updates and deletions
            md5_obj.md5 = digest
            md5_obj.save()
    except FlowvisorLinksMd5.DoesNotExist:
        #: if it's the first time update, create a md5 record
        FlowvisorLinksMd5(md5=digest, flowvisor=instance).save()

    #: delete all existing links and ports
    instance.link_set.all().delete()
    for link in links:
        src_port = link['src-port']
        dst_port = link['dst-port']
        print link
        source_switch = Switch.objects.get(dpid=link['src-switch'])
        target_switch = Switch.objects.get(dpid=link['dst-switch'])
        source_port, created = SwitchPort.objects.get_or_create(switch=source_switch, port=src_port)
        target_port, created = SwitchPort.objects.get_or_create(switch=target_switch, port=dst_port)
        for slice in instance.slices.all():
            SlicePort.objects.get_or_create(slice=slice, port=source_port)
            SlicePort.objects.get_or_create(slice=slice, port=target_port)

        link_obj = Link(flowvisor=instance, source=source_port, target=target_port)
        link_obj.save()
