#coding: utf-8
from django.db.models.signals import post_syncdb
from django.dispatch import receiver

import agora

@receiver(post_syncdb, sender=agora.models)
def init_forum(sender, **kwargs):

    if not agora.models.Forum.objects.all():
        forum = agora.models.Forum(id=1, title=u"工单", description="")
        forum.save()

