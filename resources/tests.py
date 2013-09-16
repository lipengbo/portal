"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from resources.ovs_api import slice_add_ovs_ports
from slice.models import Slice
from resources.models import Switch


class SimpleTest(TestCase):
    fixtures = ['users.json', 'export_openflow.json', 'export_project.json',
            'export_resources.json', 'export_slice.json']

    def test_slice_add_ovs_ports(self):
        slice_obj = Slice.objects.all()[0]
        ovs_ports = [{'ovs':Switch.objects.all()[0], 'ports':[1,2,3]}, {'ovs':Switch.objects.all()[1], 'ports':[1,2]}]
        try:
            slice_add_ovs_ports(slice_obj, ovs_ports)
        except Exception, ex:
            print ex
            self.assertFalse(True)
        else:
            if slice_obj.switch_set.all().count() == 2 and slice_obj.switchport_set.all().count() == 5:
                self.assertTrue(True)
            else:
                self.assertFalse(True)
