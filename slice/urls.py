from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('slice.views',
    url(r'^$', "index", name='slice_index'),
    url(r'^create/$', "create", name='project_create'),
)
