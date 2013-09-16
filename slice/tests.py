"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from slice.slice_api import create_slice_api
from django.contrib.auth.models import User
from project.models import Project, Island
from slice.models import Slice


class SimpleTest(TestCase):
    fixtures = ['users.json', 'export_openflow.json', 'export_project.json',
            'export_resources.json']

    def test_create_slice_api(self):
        user = User.objects.all()[0]
        project = Project.objects.all()[0]
        name = 'cjx'
        description = 'ok'
        island = Island.objects.all()[0]
        try:
            slice_obj = create_slice_api(project, name, description, island, user)
        except Exception, ex:
            self.assertFalse(True)
        else:
            self.assertTrue(slice_obj.id)
