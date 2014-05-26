from django.contrib import admin

from project.models import (City, Island, Project, Category,
        Membership)
from slice.models import Slice
from resources.models import  Switch, SwitchPort, Server, VirtualSwitch
from plugins.openflow.models import Virttool, Controller
#from plugins.network.models import Network, IPAddress
from resources.models import  Switch, SwitchPort, Server, VirtualSwitch, SliceSwitch
from plugins.openflow.models import Virttool, Controller, Link, VirttoolLinksMd5

admin.site.register(City)
admin.site.register(Island)
admin.site.register(Project)
admin.site.register(Category)
admin.site.register(Slice)
admin.site.register(Switch)
admin.site.register(VirtualSwitch)
admin.site.register(Server)
admin.site.register(Controller)
admin.site.register(Virttool)
admin.site.register(SwitchPort)
admin.site.register(Membership)

admin.site.register(SliceSwitch)
admin.site.register(Link)
admin.site.register(VirttoolLinksMd5)
