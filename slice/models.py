from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.db.models import F

from project.models import Project, Island

SLICE_STATE_STOPPED = 0
SLICE_STATE_STARTED = 1
SLICE_STATES = (
        (SLICE_STATE_STOPPED, 'stopped'),
        (SLICE_STATE_STARTED, 'started'),
)
# Create your models here.


class Slice(models.Model):
    owner = models.ForeignKey(User)
    name = models.CharField(max_length=256)
    description = models.TextField()
    project = models.ForeignKey(Project)
    date_created = models.DateTimeField(auto_now_add=True)
    date_expired = models.DateTimeField()
    state = models.IntegerField(choices=SLICE_STATES,
            default=SLICE_STATE_STOPPED)

    islands = models.ManyToManyField(Island, through="SliceIsland")

    def add_island(self, island):
        SliceIsland.objects.get_or_create(
            island=island, slice=self)

    def change_description(self, description):
        self.description = description
        self.save()

    def add_resource(self, resource):
        resource.on_add_into_slice(self)

    def remove_resource(self, resource):
        resource.on_remove_from_slice(self)

    def stop(self):
        self.state = SLICE_STATE_STOPPED
        self.save()

    def start(self):
        self.state = SLICE_STATE_STARTED
        self.save()

    def get_flowvisor(self):
        flowvisors = self.flowvisor_set.all()
        if flowvisors:
            return flowvisors[0]
        else:
            return None

    def get_controller(self):
        controllers = self.controller_set.all()
        if controllers:
            return controllers[0]
        else:
            return None

    def get_island(self):
        islands = self.islands.all()
        if islands:
            return islands[0]
        else:
            return None

    def get_switches(self):
        return self.switch_set.all()

    def get_virtual_switches(self):
        from resources.models import VirtualSwitch
        switches = self.switch_set.all()
        virtual_switches = []
        for switch in switches:
            try:
                virtual_switch = VirtualSwitch.objects.get(id = switch.id)
            except:
                pass
            else:
                virtual_switches.append(virtual_switch)
        return virtual_switches

    def get_default_flowspaces(self):
        return self.flowspacerule_set.filter(is_default=1)

    def get_switch_ports(self):
        return self.switchport_set.all()

    def get_vms(self):
        return self.virtual_machines.all()

    def __unicode__(self):
        return self.name


class SliceIsland(models.Model):
    slice = models.ForeignKey(Slice)
    island = models.ForeignKey(Island)

    class Meta:
        unique_together = (("slice", "island"), )
