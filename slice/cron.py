# coding:utf-8
import datetime
import pdb;

from django_cron.base import Job, cronScheduler
from django.db.models.signals import post_save
from django.core.mail import send_mail

# This is a function I wrote to check a feedback email address and add it to our database. Replace with your own imports
#from MyMailFunctions import check_feedback_mailbox
from slice.models import Slice, SliceDeleted
from plugins.openflow.flowvisor_api import flowvisor_del_slice
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
        #user = request.user
        time_delta = datetime.timedelta(seconds=1)
        for slice_obj in slices:
            print "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++time manage 1"
            print datetime.datetime.now()
            print slice_obj.date_expired
            date = datetime.datetime.now() - slice_obj.date_expired
            if date > time_delta:
#                 print "_____________________________________________________________time manage 2"
                try:
                    print 1
                    email = slice_obj.owner.email
                    slice_deleted = SliceDeleted(name = slice_obj.name,
                        show_name = slice_obj.show_name,
                        owner_name = slice_obj.owner.username,
                        description = slice_obj.description,
                        project_name = slice_obj.project.name,
                        date_created = slice_obj.date_created,
                        date_expired = slice_obj.date_expired,
                        type = 2)
                    print 2
                    slice_obj.delete()
                    print 3
                except Exception, ex:
                    print 4
                    pass
                else:
                    print 5
                    slice_deleted.save()
#                     if email:
#                         send_mail("slice 已过期 ", 'slice('+slice_deleted.show_name+')已过期！', 'chenjunxia@fnic.cn', [email], fail_silently=False)
            else:
                pass


cronScheduler.register(Checkslice)
