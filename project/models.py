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



#@receiver(m2m_changed, sender=Flowvisor.slices.through)
#@receiver(m2m_changed, sender=Controller.slices.through)
def on_add_into_slice(sender, instance, action, pk_set, model, **kwargs):
    resource = instance
    if action == 'post_add': #: only handle post_add event
        resource.on_add_into_slice()
