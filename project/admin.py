from django.contrib import admin

from project.models import City, Island, Slice, Project,\
        Switch, Flowvisor, Controller, Server, VirtualSwitch,\
        Network, HostMac, SwitchPort, IPAddress


admin.site.register(City)
admin.site.register(Island)
admin.site.register(Project)
admin.site.register(Slice)
admin.site.register(Switch)
admin.site.register(VirtualSwitch)
admin.site.register(Server)
admin.site.register(Controller)
admin.site.register(Flowvisor)
admin.site.register(Network)
admin.site.register(HotsMac)
admin.site.register(SwitchPort)
admin.site.register(IPAddress)
