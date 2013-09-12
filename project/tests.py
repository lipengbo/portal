"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import datetime

from django.test import TestCase
from django.contrib.auth.models import User

from project.models import (Project, Category, Island)

class SimpleTest(TestCase):
    fixtures = ['users.json', 'islands.json',
            'cities.json', 'categories']

    def test_create_project(self):
        owner = User.objects.all()[0]
        category = Category.objects.all()[0]
        project = Project(name="sdn project", owner=owner, category=category)
        project.save()
        self.assertTrue(project.id)

    def test_create_category(self):
        category = Category(name="sdn2")
        category.save()
        self.assertTrue(category.id)

    def test_add_member_to_project(self):
        owner = User.objects.all()[0]
        category = Category.objects.all()[0]
        project = Project(name="sdn project", owner=owner, category=category)
        project.save()
        self.assertTrue(project.memberships.count() == 0)
        project.add_member(User.objects.all()[1])
        self.assertTrue(project.memberships.count() == 1)

    def test_add_same_member_to_project(self):
        owner = User.objects.all()[0]
        category = Category.objects.all()[0]
        project = Project(name="sdn project", owner=owner, category=category)
        project.save()
        self.assertTrue(project.memberships.count() == 0)
        project.add_member(User.objects.all()[1])
        self.assertTrue(project.memberships.count() == 1)
        project.add_member(User.objects.all()[1])
        self.assertTrue(project.memberships.count() == 1)

    def est_create_slice(self):
        slice = Slice(name="test_slice", description=" ",
                owner=User.objects.all()[0],
                project=Project.objects.all()[0],
                date_expired=datetime.datetime.now())
        slice.save()

        #: add controller
        controller = Controller(ip="192.168.5.41", port="8081",
                http_port="8080", username="test", password="test",
                hostname="test_contoller", island=Island.objects.all()[0])
        controller.save()
        controller.slices.add(slice)

        #: add flowvisor
        flowvisor = Flowvisor(ip="192.168.5.41", port="8081",
                http_port="8080", username="test", password="test",
                hostname="test_flowvisor", island=Island.objects.all()[0])

        flowvisor.save()
        flowvisor.slices.add(slice)

        self.assertTrue(slice.controller_set.all().count() == 1)
        self.assertTrue(slice.id)
