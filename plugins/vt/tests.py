"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from api import create_vm_for_controller, delete_vm_for_controller
from django.contrib.auth.models import User
from slice.models import Slice
from project.models import Island


class VmTest(TestCase):
    fixtures = ['lpb_pemission.json', 'lpb_project_data.json', 'lpb_resource.json', 'lpb_image_data.json', 'lpb_unittest.json']

    def test_create_vm_for_controller(self):
        island_obj = Island.objects.get(id=1)
        slice_obj = Slice.objects.get(id=1)
        image_name = 'floodlight'
        vm = create_vm_for_controller(island_obj, slice_obj, image_name)
        print vm

    def test_create_vm_for_slice(self):
        pass

    def test_delete_vm_for_controller(self):
        pass

    def test_delete_vm_for_slice(self):
        pass


class ServerTest(TestCase):
    def test_getinfo(self):
        pass
