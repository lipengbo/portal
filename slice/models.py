from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.db.models import F
from resources.models import Resource

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
        slice_island, created = SliceIsland.objects.get_or_create(
            island=island, slice=self)

    def add_resource(self, resource):
        resource.on_add_into_slice()

#     def add_controller(self, controller):
#         controller.slices.add(self)
# 
#     def add_switch(self, switch):
#         slice_switch, created = SliceSwitch.objects.get_or_create(
#             switch=switch, slice=self)
# 
#     def add_virtual_switch(self, virtual_switch):
#         slice_switch, created = SliceSwitch.objects.get_or_create(
#             switch=virtual_switch, slice=self)

    def __unicode__(self):
        return self.name


class SliceIsland(models.Model):
    slice = models.ForeignKey(Slice)
    island = models.ForeignKey(Island)

    class Meta:
        unique_together = (("slice", "island"), )
