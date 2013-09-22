from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('slice.views',
    url(r'^$', "index", name='slice_index'),
    url(r'^create/(?P<proj_id>\d+)/$', "create", name='create_slice'),
    url(r'^edit/(?P<slice_id>\d+)/$', "edit", name='edit_slice'),
    url(r'^delete/(?P<slice_id>\d+)/$', "delete", name='delete_slice'),
    url(r'^detail/(?P<slice_id>\d+)/$', "detail", name='slice_detail'),
    url(r'^start_or_stop/(?P<slice_id>\d+)/(?P<flag>\d+)/$', "start_or_stop", name='start_or_stop'),
    url(r'^topology/(?P<slice_id>\d+)/$', "topology", name='slice_topology'),
)
