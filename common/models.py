from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.db.models import F

class Counter(models.Model):
    target = models.IntegerField(choices=((0, "project"),(1, "slice")))
    count = models.PositiveIntegerField(default=0)
    date = models.DateField(auto_now_add=True)
    type = models.IntegerField(choices=((0, "year"),(1, "month"),(2, "day")))

    class Meta:
        unique_together = (("target", "date", "type"), )

