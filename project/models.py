from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, m2m_changed
from django.db.models import F
from django.dispatch import receiver


SLICE_STATE_STOPPED = 0
SLICE_STATE_STARTED = 1
SLICE_STATES = (
        (SLICE_STATE_STOPPED, 'stopped'),
        (SLICE_STATE_STARTED, 'started'),)

class City(models.Model):
    name = models.CharField(max_length=256)
    description = models.TextField()

    def __unicode__(self):
        return self.name

class Island(models.Model):
    name = models.CharField(max_length=256)
    description = models.TextField()
    city = models.ForeignKey(City)

    def __unicode__(self):
        return self.name

class Project(models.Model):
    owner = models.ForeignKey(User)
    name = models.CharField(max_length=256)
    description = models.TextField()
    islands = models.ManyToManyField(Island)
    memberships = models.ManyToManyField(User, through="Membership", 
            related_name="project_belongs")

    def __unicode__(self):
        return self.name

class Membership(models.Model):
    project = models.ForeignKey(Project)
    user = models.ForeignKey(User)
    is_owner = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

class Slice(models.Model):
    owner = models.ForeignKey(User)
    name = models.CharField(max_length=256)
    description = models.TextField()
    project = models.ForeignKey(Project)
    date_created = models.DateTimeField(auto_now_add=True)
    date_expired = models.DateTimeField()
    state = models.IntegerField(choices=SLICE_STATES, 
            default=SLICE_STATE_STOPPED)

    def __unicode__(self):
        return self.name

class Resource(models.Model):
    name = models.CharField(max_length=256)
    island = models.ForeignKey(Island)
    slices = models.ManyToManyField(Slice)

    def on_create_slice(self):
        pass

    def on_delete_slice(self):
        pass

    def on_start_slice(self):
        pass

    def on_add_into_slice(self):
        print self, 'on_add_into_slice'

    def on_remove_from_slice(self):
        pass

    def __unicode__(self):
        return self.name

    class Meta:
        abstract = True

class Controller(Resource):
    ip = models.IPAddressField()
    port = models.IntegerField()
    http_port = models.IntegerField()
    is_root = models.BooleanField(default=False)
    hostname = models.CharField(max_length=20)
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=20)

    def __unicode__(self):
        return self.hostname

class Flowvisor(Resource):
    ip = models.IPAddressField()
    port = models.IntegerField()
    http_port = models.IntegerField()
    hostname = models.CharField(max_length=20)
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=20)

    def __unicode__(self):
        return self.hostname

class Switch(Resource):
    ip = models.IPAddressField()
    port = models.IntegerField()
    http_port = models.IntegerField()
    hostname = models.CharField(max_length=20)
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=20)
    dpid = models.CharField(max_length=256)
    has_gre_tunnel = models.BooleanField(default=False)
 
    def __unicode__(self):
        return self.hostname

class Server(Resource):
    ip = models.IPAddressField()
    hostname = models.CharField(max_length=20)
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=20)
    state = models.IntegerField(null=True)
    cpu = models.CharField(max_length=256, null=True)
    memory = models.IntegerField(null=True)
    bandwidth = models.IntegerField(null=True)
    disk_size = models.IntegerField(null=True)
    os = models.CharField(max_length=256, null=True)
    mac = models.CharField(max_length=256, null=True)
    update_time = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.hostname

class VirtualMachine(Server):
    slice = models.ForeignKey(Slice, related_name="virtual_machines")

class VirtualSwitch(Resource):
    server = models.ForeignKey(Server)


class FlowSpaceRule(Resource):
    dpid = models.CharField(max_length=256)
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
    wildcards = models.CharField(max_length=256)
    is_default = models.IntegerField()
    actions = models.CharField(max_length=256)

@receiver(m2m_changed, sender=Flowvisor.slices.through)
@receiver(m2m_changed, sender=Controller.slices.through)
def on_add_into_slice(sender, instance, action, pk_set, model, **kwargs):
    resource = instance
    if action == 'post_add': #: only handle post_add event
        resource.on_add_into_slice()
