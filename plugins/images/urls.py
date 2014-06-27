from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('plugins.images.views',
    url(r'^create/$', "create", name='create_image'),
    url(r'^list/$', "list", name='list_images'),
#    url(r'^get_vms_state/(?P<sliceid>\d+)/$', "get_vms_state_by_sliceid", name='get_vms_state'),
)
