from django.contrib import admin

from project.models import (City, Island, Project, Category,
        Membership)
from slice.models import Slice
from resources.models import  Switch, SwitchPort, Server, VirtualSwitch
from plugins.openflow.models import Flowvisor, Controller
from plugins.network.models import Network, IPAddress
from plugins.vt.models import VirtualMachine, HostMac

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
admin.site.register(Network)
admin.site.register(HostMac)
admin.site.register(SwitchPort)
admin.site.register(IPAddress)
admin.site.register(Membership)
