from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.db.models import F
from django.contrib.admin.models import LogEntry, ADDITION
from django.contrib.contenttypes.models import ContentType

SUCCESS = 200
FAIL = 201

def log(user, target, message, result_code=SUCCESS):
    LogEntry.objects.log_action(user_id=user.id,
            content_type_id=ContentType.objects.get_for_model(target).pk,
            object_id=target.pk,
            object_repr=target.__unicode__(),
            action_flag=result_code,
            change_message=message)
