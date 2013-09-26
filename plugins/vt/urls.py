from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('plugins.vt.views',
    url(r'^vm/detail/(?P<vmid>\d+)/$', "vm_detail", name='vt_vm_detail'),
    url(r'^create/vm/(?P<sliceid>\d+)/$', "create_vm", name='vt_create_vm'),
    url(r'^vm/list/(?P<sliceid>\d+)/$', "vm_list", name='vm_list'),
)
