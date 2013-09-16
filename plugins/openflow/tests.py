"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from plugins.openflow.controller_api import slice_add_controller
from slice.models import Slice
from plugins.openflow.models import Controller, Flowvisor, FlowSpaceRule
from plugins.openflow.flowvisor_api import flowvisor_add_slice
from project.models import Island, City
from resources.models import Server
from plugins.openflow.flowspace_api import create_default_flowspace, flowspace_nw_add


class ControllerTest(TestCase):
    fixtures = ['users.json', 'export_openflow.json', 'export_project.json',
            'export_resources.json', 'export_slice.json']

    def test_slice_add_controller(self):
        slice_obj = Slice.objects.all()[0]
#         print slice_obj.controller_set.all().count()
        controller = Controller.objects.all()[0]
        citys = City.objects.all()
        islands = Island.objects.filter(city__in=citys)
        print islands.count()
        try:
            slice_add_controller(slice_obj, controller)
        except Exception, ex:
            print ex
            self.assertFalse(True)
        else:
            if slice_obj.controller_set.all().count() == 1:
                self.assertTrue(True)


class FlowvisorTest(TestCase):
    fixtures = ['users.json', 'export_openflow.json', 'export_project.json',
            'export_resources.json', 'export_slice.json']

    def test_flowvisor_add_slice(self):
        server = Server.objects.all()[0]
        island = Island.objects.all()[0]
        controller = Controller(name='cjxnu', ip="192.168.5.103", port="6125",
                http_port="6124", username="test", password="test",
                hostname="test_contoller", host=server, island=island, state=1)
        controller.save()
        flowvisor = Flowvisor(name='cjxsv', ip="192.168.5.103", port="6634",
                http_port="8181", username="test", password="123",
                hostname="test_flowvisor", host=server, island=island, state=1)
        flowvisor.save()
        slice_name = 'cjxunittest2'
        user_email = 'cjx@qq.com'
        try:
            flowvisor_add_slice(flowvisor, controller, slice_name, user_email)
        except Exception, ex:
            print ex
            self.assertFalse(True)
        else:
            self.assertTrue(True)


class FlowspaceTest(TestCase):
    fixtures = ['users.json', 'export_openflow.json', 'export_project.json',
            'export_resources.json', 'export_slice.json']

    def test_create_default_flowspace(self):
        slice_obj = Slice.objects.all()[0]
        flowspace_obj = create_default_flowspace(slice_obj, 'test1', 100, 1,
            '', '', '', '', '', '', '', '', '', '', '')
        self.assertTrue(flowspace_obj.id)

    def test_flowspace_nw_add(self):
        slice_obj = Slice.objects.all()[0]
        old_nws = ['192.168.5.37/24', '192.168.5.38/24']
        new_nm = '192.168.5.35/24'
        try:
            flowspace_nw_add(slice_obj, old_nws, new_nm)
        except Exception, ex:
            self.assertFalse(True)
        else:
            if FlowSpaceRule.objects.all().count() == 6:
                self.assertTrue(True)
            else:
                self.assertFalse(True)
