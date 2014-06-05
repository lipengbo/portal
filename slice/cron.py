# coding:utf-8
import datetime
import pdb;

from django_cron.base import Job, cronScheduler
from django.db.models.signals import post_save
from django.core.mail import send_mail
from django.contrib.auth.models import User

# This is a function I wrote to check a feedback email address and add it to our database. Replace with your own imports
#from MyMailFunctions import check_feedback_mailbox
from slice.models import Slice, SliceDeleted
from plugins.openflow.virttool_api import virttool_del_slice
from notifications import notify
DEBUG = False


class Checkslice(Job):
    """
    Cron Job that checks the lgr users mailbox and adds any approved senders' attachments to the db
    """

    # run every 300 seconds (5 minutes)
    run_every = 43200

    def job(self):
        # This will be executed every 5 minutes
        #check_feedback_mailbox()
        if DEBUG == True:
            pdb.set_trace()
#         print "+++++++++++++++++++++job"
#         print "before time"
        slices = Slice.objects.filter(type=0)
        time_delta = datetime.timedelta(seconds=1)
        for slice_obj in slices:
#             print "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++time manage 1"
#             print datetime.datetime.now()
#             print slice_obj.date_expired
            date = datetime.datetime.now() - slice_obj.date_expired
            if date > time_delta:
                try:
                    admins = User.objects.filter(is_superuser=True)
                    if len(admins) > 0:
                        slice_name = slice_obj.name
                        slice_show_name = slice_obj.show_name
                        project_name = slice_obj.project.name
                        user = slice_obj.owner
                        admin = admins[0]
                    slice_obj.delete(user=None)
                except:
                    pass
                else:
                    try:
                        if user and admin:
                            slice_deleted_objs = SliceDeleted.objects.filter(name=slice_name)
                            if len(slice_deleted_objs) > 0:
                                print 1
                                notify.send(admin, recipient=user, verb=u"虚网过期删除", action_object=slice_deleted_objs[0],
                                            description=u"您创建的虚网“" + slice_show_name + u"“超过有效期已经被删除" + u"！")
                            else:
                                print 2
                                notify.send(admin, recipient=user, verb=u"虚网过期删除", action_object=slice_obj,
                                            description=u"您创建的虚网“" + slice_show_name + u"“超过有效期已经被删除" + u"！")
                    except:
                        pass
#                         import traceback
#                         traceback.print_exc()
            else:
                pass


cronScheduler.register(Checkslice)
