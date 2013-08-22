from django.contrib import admin

from project.models import City, Island, Slice, Project,\
        Switch, Flowvisor, Controller, Server


admin.site.register(City)
admin.site.register(Island)
admin.site.register(Project)
admin.site.register(Slice)
admin.site.register(Switch)
admin.site.register(Server)
admin.site.register(Controller)
admin.site.register(Flowvisor)
