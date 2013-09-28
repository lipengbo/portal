from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('plugins.vt.views',
    url(r'^create/vm/(?P<sliceid>\d+)/$', "create_vm", name='create_vm'),
    url(r'^vm/list/(?P<sliceid>\d+)/$', "vm_list", name='vm_list'),
)
