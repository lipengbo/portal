from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.db.models import F
from django.contrib.admin.models import LogEntry, ADDITION
from django.contrib.contenttypes.models import ContentType

SUCCESS = 200
FAIL = 201

# Create your models here.
def log(user, target, message, result_code=SUCCESS):
    content_type_id = target and ContentType.objects.get_for_model(target).pk or None
    object_id = target and target.pk or None
    object_repr = target and target.__unicode__() or ''
    LogEntry.objects.log_action(user_id=user.id,
            content_type_id=content_type_id,
            object_id=object_id,
            object_repr=object_repr,
            action_flag=result_code,
            change_message=message)
