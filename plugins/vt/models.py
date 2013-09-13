from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.db.models import F
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from resources.models import ComputeResource, Server
from slice.models import Slice

class VirtualMachine(ComputeResource):
    slice = models.ForeignKey(Slice, related_name="virtual_machines")
    server = models.ForeignKey(Server)

class HostMac(models.Model):
    mac = models.CharField(max_length=32)
    content_type = models.ForeignKey(ContentType)
    host_id = models.PositiveIntegerField()
    #: the switch that the rule is applied on, can be Switch or VirtualSwitch
    host = generic.GenericForeignKey('content_type', 'host_id')


class Image(models.Model):
    uuid = models.CharField(max_length=36)
    type = models.IntegerField()
    version = models.CharField(max_length=32)

class Flavor(models.Model):
    name = models.CharField(max_length=64)
    cpu = models.IntegerField()
    ram = models.IntegerField()
    hdd = models.IntegerField()

    def __unicode__(self):
        return self.name
