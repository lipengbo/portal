from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.db.models import F
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from project.models import Island
from slice.models import Slice


class Resource(models.Model):
    name = models.CharField(max_length=256)

    def on_create_slice(self):
        pass

    def on_delete_slice(self):
        pass

    def on_start_slice(self):
        pass

    def on_add_into_slice(self, slice_obj):
        pass

    def on_remove_from_slice(self, slice_obj):
        pass

    def __unicode__(self):
        return self.name

    class Meta:
        abstract = True


class IslandResource(Resource):
    island = models.ForeignKey(Island)

    class Meta:
        abstract = True


class ComputeResource(IslandResource):
    hostname = models.CharField(max_length=20)
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=20)
    state = models.IntegerField(null=True)
    cpu = models.CharField(max_length=256, null=True)
    memory = models.IntegerField(null=True)
    bandwidth = models.IntegerField(null=True)
    disk_size = models.IntegerField(null=True)
    os = models.CharField(max_length=256, null=True)
    ip = models.IPAddressField()
    mac = models.CharField(max_length=256, null=True)
    update_time = models.DateTimeField(auto_now_add=True)

    slices = models.ManyToManyField(Slice)

    def __unicode__(self):
        return self.hostname

    class Meta:
        abstract = True


class ServiceResource(IslandResource):
    ip = models.IPAddressField()
    port = models.IntegerField()
    http_port = models.IntegerField()
    hostname = models.CharField(max_length=20)
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=20)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    #: served on a ComputeResource like Server or VirtualMachine
    host = generic.GenericForeignKey('content_type', 'object_id')
    slices = models.ManyToManyField(Slice, blank=True)
    state = models.IntegerField()

    def __unicode__(self):
        return self.hostname

    class Meta:
        abstract = True


class Server(ComputeResource):
    pass


class SwitchResource(IslandResource):
    ip = models.IPAddressField()
    port = models.IntegerField()
    http_port = models.IntegerField()
    hostname = models.CharField(max_length=20)
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=20)
    dpid = models.CharField(max_length=256)
    has_gre_tunnel = models.BooleanField(default=False)
    slices = models.ManyToManyField(Slice, through="SliceSwitch")

    def __unicode__(self):
        return self.hostname

    class Meta:
        abstract = True


class Switch(SwitchResource):
    def on_add_into_slice(self, slice_obj):
        SliceSwitch.objects.get_or_create(
             switch=self, slice=slice_obj)


class SliceSwitch(models.Model):
    slice = models.ForeignKey(Slice)
    switch = models.ForeignKey(Switch)

    class Meta:
        unique_together = (("slice", "switch"), )


class SwitchPort(Resource):

    #: the switch that the rule is applied on, can be Switch or VirtualSwitch
    switch = models.ForeignKey(Switch)
    port = models.PositiveIntegerField()
    slices = models.ManyToManyField(Slice, through="SlicePort")

    def on_add_into_slice(self, slice_obj):
        SlicePort.objects.get_or_create(
             switch_port=self, slice=slice_obj)

    class Meta:
        unique_together = (("switch", "port"), )


class SlicePort(models.Model):
    slice = models.ForeignKey(Slice)
    switch_port = models.ForeignKey(SwitchPort)

    class Meta:
        unique_together = (("slice", "switch_port"), )


class VirtualSwitch(Switch):
    """
        A virtual switch service that created on a Physical Server
    """
    server = models.ForeignKey(Server)
