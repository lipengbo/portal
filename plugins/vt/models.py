from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.db.models import F
from resources.models import *
# Create your models here.
class VirtualMachine(ComputeResource):
    slice = models.ForeignKey(Slice, related_name="virtual_machines")
    server = models.ForeignKey(Server)

class HostMac(models.Model):
    mac = models.CharField(max_length=32)
    content_type = models.ForeignKey(ContentType)
    host_id = models.PositiveIntegerField()
    #: the switch that the rule is applied on, can be Switch or VirtualSwitch
    host = generic.GenericForeignKey('content_type', 'host_id')


class ImageMembers(models.Model):
    id = models.IntegerField(primary_key=True)
    image_id = models.CharField(max_length=36)
    member = models.CharField(max_length=255)
    can_share = models.BooleanField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted = models.BooleanField()
    class Meta:
        db_table = u'image_members'

class ImageProperties(models.Model):
    id = models.IntegerField(primary_key=True)
    image_id = models.CharField(max_length=36)
    name = models.CharField(max_length=255)
    value = models.TextField(blank=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted = models.BooleanField()
    class Meta:
        db_table = u'image_properties'

class Images(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    name = models.CharField(max_length=255, blank=True)
    size = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=30)
    is_public = models.BooleanField()
    location = models.TextField(blank=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted = models.BooleanField()
    disk_format = models.CharField(max_length=20, blank=True)
    container_format = models.CharField(max_length=20, blank=True)
    checksum = models.CharField(max_length=32, blank=True)
    owner = models.CharField(max_length=255, blank=True)
    min_disk = models.IntegerField()
    min_ram = models.IntegerField()
    protected = models.NullBooleanField(null=True, blank=True)
    class Meta:
        db_table = u'images'

class MigrateVersion(models.Model):
    repository_id = models.CharField(max_length=250, primary_key=True)
    repository_path = models.TextField(blank=True)
    version = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = u'migrate_version'

class Flavor(models.Model):
    name = models.CharField(max_length=64)
    cpu = models.IntegerField()
    ram = models.IntegerField()
    hdd = models.IntegerField()

    def __unicode__(self):
        return self.name
