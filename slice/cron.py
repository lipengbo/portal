# coding:utf-8
import datetime
import pdb;

from django_cron.base import Job, cronScheduler
from django.db.models.signals import post_save
from django.core.mail import send_mail

# This is a function I wrote to check a feedback email address and add it to our database. Replace with your own imports
#from MyMailFunctions import check_feedback_mailbox
from slice.models import Slice
from plugins.openflow.flowvisor_api import flowvisor_del_slice
DEBUG = False


class Checkslice(Job):
    """
    Cron Job that checks the lgr users mailbox and adds any approved senders' attachments to the db
    """

    # run every 300 seconds (5 minutes)
    run_every = 86400

    def job(self):
        # This will be executed every 5 minutes
        #check_feedback_mailbox()
        if DEBUG == True:
            pdb.set_trace()
#         print "timer ******"
#         print "before time"
        slices = Slice.objects.all()
        #user = request.user
        time_delta = datetime.timedelta(seconds=1)
        for slice_obj in slices:
#             print "time manage 1"
            date = datetime.datetime.now() - slice_obj.date_expired
            if (date > time_delta and slice_obj.expired == 0):
                print "time manage 2"
                email = '350603736@qq.com'
                slice_obj.expired = 1
                slice_obj.save()
#                     try:
#                         flowvisor_del_slice(slice_obj.get_flowvisor(), slice_obj.name)
#                     except:
#                         pass
                send_mail("slice 已过期 ", '该slice已过期！', 'chenjunxia@fnic.cn', [email], fail_silently=False)
            else:
                pass


cronScheduler.register(Checkslice)