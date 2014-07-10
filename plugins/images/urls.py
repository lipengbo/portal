from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('plugins.images.views',
    url(r'^create/$', "create", name='create_image'),
    url(r'^list/(?P<image_type>\d+)/$', "list", name='list_images'),
    url(r'^update/$', "update", name='update_image'),
    url(r'^delete/$', "delete", name='delete_image'),
    url(r'^upload/$', "upload", name='upload_image'),
#    url(r'^get_vms_state/(?P<sliceid>\d+)/$', "get_vms_state_by_sliceid", name='get_vms_state'),
)
