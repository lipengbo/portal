from django.contrib import admin

from project.models import (City, Island, Project, Category,
        Membership)
from slice.models import Slice
<<<<<<< HEAD
from resources.models import  Switch, SwitchPort, Server, VirtualSwitch
from plugins.openflow.models import Flowvisor, Controller
#from plugins.network.models import Network, IPAddress
=======
from resources.models import  Switch, SwitchPort, Server, VirtualSwitch, SliceSwitch
from plugins.openflow.models import Flowvisor, Controller, Link
from plugins.network.models import Network, IPAddress
>>>>>>> 4a4f3136d3aa25e5ab05bbf3b77a15c3f0837d31
from plugins.vt.models import VirtualMachine, HostMac
from plugins.ipam import models

admin.site.register(City)
admin.site.register(Island)
admin.site.register(Project)
admin.site.register(Category)
admin.site.register(Slice)
admin.site.register(Switch)
admin.site.register(VirtualSwitch)
admin.site.register(Server)
admin.site.register(Controller)
admin.site.register(Flowvisor)
admin.site.register(HostMac)
admin.site.register(SwitchPort)
admin.site.register(Membership)
<<<<<<< HEAD

admin.site.register(models.Network)
admin.site.register(models.Subnet)
admin.site.register(models.IPUsage)
=======
admin.site.register(SliceSwitch)
admin.site.register(Link)
>>>>>>> 4a4f3136d3aa25e5ab05bbf3b77a15c3f0837d31
