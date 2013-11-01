from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('nexus.views',
    url(r'^$', "index", name='nexus_index'),
    url(r'^get_islands/$', "get_islands", name='nexus_islands'),
    url(r'^(?P<app_label>\w+)/(?P<model_class>\w+)/$', "list_objects", name='nexus_list'),
    url(r'^(?P<app_label>\w+)/(?P<model_class>\w+)/add/$', "add_or_edit", name='nexus_add'),
    url(r'^(?P<app_label>\w+)/(?P<model_class>\w+)/delete/(?P<id>\d+)/$', "delete_action", name='nexus_delete'),
    url(r'^(?P<app_label>\w+)/(?P<model_class>\w+)/edit/(?P<id>\d+)/$', "add_or_edit", name='nexus_edit'),
)
