from optparse import make_option

from django.core.management.base import AppCommand, BaseCommand, CommandError
from django.conf import settings

from plugins.openflow.models import Link, Virttool, update_links

class Command(BaseCommand):
    help = ''

    def handle(self, **options):
        virttools = Virttool.objects.all()
        for virttool in virttools:
            update_links(None, virttool, False)

