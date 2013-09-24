from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('plugins.vt.views',
    url(r'^vm/detail/(?P<vmId>\d+)/$', "vm_detail", name='vt_vm_detail'),
    url(r'^create/vm/(?P<sliceId>\d+)/$', "create_vm", name='vt_create_vm'),
)
