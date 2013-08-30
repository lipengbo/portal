from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, m2m_changed
from django.db.models import F
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic


SLICE_STATE_STOPPED = 0
SLICE_STATE_STARTED = 1
SLICE_STATES = (
        (SLICE_STATE_STOPPED, 'stopped'),
        (SLICE_STATE_STARTED, 'started'),)

SWITCH_TYPE_PHYSICAL = 0
SWITCH_TYPE_VIRTUAL = 1
SWITCH_TYPES = (
        (SWITCH_TYPE_PHYSICAL, 'physical'),
        (SWITCH_TYPE_VIRTUAL, 'virtual')
        )
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

class Category(models.Model):
    name = models.CharField(max_length=256)

class Project(models.Model):
    owner = models.ForeignKey(User)
    name = models.CharField(max_length=256)
    description = models.TextField()
    islands = models.ManyToManyField(Island)  # Usage: project.islands.add(island)
    memberships = models.ManyToManyField(User, through="Membership", 
            related_name="project_belongs") 
    categories = models.ManyToManyField(Category, through="ProjectCategory")

    def __unicode__(self):
        return self.name


class ProjectCategory(models.Model):
    project = models.ForeignKey(Project)
    category = models.ForeignKey(Category)

    class Meta:
        unique_together = (("project", "category"),)


class Membership(models.Model):
    project = models.ForeignKey(Project)
    user = models.ForeignKey(User)
    is_owner = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (("project", "user"), )

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

class IslandResource(Resource):
    island = models.ForeignKey(Island)

    class Meta:
        abstract = True


class ComputeResource(IslandResource):
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

    slices = models.ManyToManyField(Slice)

    def __unicode__(self):
        return self.hostname

    class Meta:
        abstract = True

class Server(ComputeResource):
    pass

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
    slices = models.ManyToManyField(Slice)

    def __unicode__(self):
        return self.hostname

    class Meta:
        abstract = True

class Controller(ServiceResource):
    is_root = models.BooleanField(default=False)

class Flowvisor(ServiceResource):
    pass

class Gateway(Server):
    pass

class VirtualMachine(ComputeResource):
    slice = models.ForeignKey(Slice, related_name="virtual_machines")
    server = models.ForeignKey(Server)

class Switch(IslandResource):
    ip = models.IPAddressField()
    port = models.IntegerField()
    http_port = models.IntegerField()
    hostname = models.CharField(max_length=20)
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=20)
    dpid = models.CharField(max_length=256)
    has_gre_tunnel = models.BooleanField(default=False)
    slices = models.ManyToManyField(Slice)

    type = models.IntegerField(choices=SWITCH_TYPES)

    def __unicode__(self):
        return self.hostname

class VirtualSwitch(Switch):
    """
        A virtual switch service that created on a Physical Server
    """
    server = models.ForeignKey(Server)

class HostMac(models.Model):
    mac = models.CharField(max_length=32)
    content_type = models.ForeignKey(ContentType)
    host_id = models.PositiveIntegerField()
    #: the switch that the rule is applied on, can be Switch or VirtualSwitch
    host = generic.GenericForeignKey('content_type', 'host_id')

class SwitchPort(Resource):

    #: the switch that the rule is applied on, can be Switch or VirtualSwitch
    switch = models.ForeignKey(Switch)
    port = models.PositiveIntegerField()
    slices = models.ManyToManyField(Slice, through="SlicePort")

    class Meta:
        unique_together = (("switch", "port"), )

class SlicePort(models.Model):
    slice = models.ForeignKey(Slice)
    switch_port = models.ForeignKey(SwitchPort)

class FlowSpaceRule(Resource):
    slice_port = models.ForeignKey(SlicePort)
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


class Network(Resource):
    netaddr = models.IPAddressField(null=False)
    netmask = models.IPAddressField(null=False)
    slices = models.ManyToManyField(Slice, through="SliceNetwork")

    class Meta:
        unique_together = ("netaddr", "netmask")

class IPRange(Resource):
    network = models.ForeignKey(Network)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    host = generic.GenericForeignKey('content_type', 'object_id')
    start = models.IPAddressField(null=False)
    end = models.IPAddressField(null=False)
    type = models.IntegerField(default=1) # 1: static, 2: dynamic

    def __unicode__(self):
        return u"%s ~ %s" % (self.start, self.end)

    class Meta:
        unique_together = (u"network", u"object_id", u"start", u"end")

class IPAddress(models.Model):
    ip_range = models.ForeignKey(IPRange)
    address = models.IPAddressField(null=False)
    available  = models.BooleanField(default=False)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    host = generic.GenericForeignKey('content_type', 'object_id')

    def __unicode__(self):
        return self.address

    class Meta:
        pass

class SliceNetwork(models.Model):
    network = models.ForeignKey(Network)
    slice = models.ForeignKey(Slice)
    use_dhcp = models.BooleanField(default=False)
    public = models.BooleanField(default=False)
    description = models.TextField(null=True)
    ip_ranges = models.ManyToManyField(IPRange)
    ip_addresses = models.ManyToManyField(IPAddress, related_name="ipaddress_slice_network")
    dnses = models.ManyToManyField(IPAddress)
    dhcpes = models.ManyToManyField(IPAddress, related_name="dhcp_slice_networks")

    def __unicode__(self):
        return self.name

    class Meta:
        pass


class IslandSliceNetworkGateway(IslandResource):
    slice_network = models.ForeignKey(SliceNetwork)
    gateway = models.ForeignKey(Gateway)

    def __unicode__(self):
        return self.address

    class Meta:
        unique_together = ("slice_network", "island")

class NAT(Resource):
    """
    primary key: level + public_address
    """
    slice = models.ForeignKey(Slice)
    parent = models.ForeignKey("self", null=True)
    public_ip = models.ForeignKey(IPAddress, related_name="public_ip_nats")
    private_ip = models.ForeignKey(IPAddress, related_name="private_ip_nats")
    date_expired = models.DateTimeField()
    available = models.BooleanField(default=False)

    def __unicode__(self):
        return self.public_ip

@receiver(m2m_changed, sender=Flowvisor.slices.through)
@receiver(m2m_changed, sender=Controller.slices.through)
def on_add_into_slice(sender, instance, action, pk_set, model, **kwargs):
    resource = instance
    if action == 'post_add': #: only handle post_add event
        resource.on_add_into_slice()
