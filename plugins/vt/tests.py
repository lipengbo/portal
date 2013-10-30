"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from api import create_vm_for_controller, create_vm_for_gateway
from slice.models import Slice
from project.models import Island
import json


def test_create_vm_for_controller():
    island_obj = Island.objects.get(id=1)
    slice_obj = Slice.objects.get(id=1)
    image_name = 'floodlight'
    vm = create_vm_for_controller(island_obj, slice_obj, image_name)
    return vm


def test_create_vm_for_gateway():
    island_obj = Island.objects.get(id=1)
    slice_obj = Slice.objects.get(id=1)
    image_name = 'floodlight'
    server_id = 1
    vm = create_vm_for_gateway(island_obj, slice_obj, server_id, image_name=image_name)
    return vm


class VMCreate(TestCase):
    fixtures = ['lpb_pemission.json', 'lpb_project_data.json', 'lpb_resource.json', 'lpb_image_data.json', 'lpb_unittest.json']

    def test_create_vm_for_controller(self):
        vm = test_create_vm_for_controller()
        self.assertTrue(vm)

    def test_create_vm_for_gateway(self):
        vm = test_create_vm_for_gateway()
        self.assertTrue(vm)

    def test_create_vm_for_slice(self):
        context = {}
        context['name'] = 'vm1'
        context['flavor'] = 1
        context['image'] = 1
        context['server'] = 1
        context['enable_dhcp'] = True
        response = self.client.post(path='/plugins/vt/create/vm/1/1/', data=context)
        result = json.loads(response.content)
        self.assertTrue(result.get('result') == 0)


class Gateway_ip(TestCase):
    fixtures = ['lpb_pemission.json', 'lpb_project_data.json', 'lpb_resource.json', 'lpb_image_data.json', 'lpb_unittest.json']

    def test_get_slice_gateway_ip(self):
        slice_obj = Slice.objects.get(id=1)
        response = self.client.get(path='/plugins/vt/get_slice_gateway_ip/%s/' % slice_obj.name)
        result = json.loads(response.content)
        self.assertTrue(result.get('ipaddr') == '10.0.0.1')
