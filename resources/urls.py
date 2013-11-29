from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('resources.views',
    url(r'^$', "index", name='resources_index'),
    url(r'^topology_select/$', "topology_select", name='topology_select'),
)
