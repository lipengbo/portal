from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('project.views',
    url(r'^$', "index", name='project_index'),
    url(r'^detail/(?P<id>\d+)/$', "detail", name='project_detail'),
    url(r'^edit/(?P<id>\d+)/$', "create_or_edit", name='project_edit'),
    url(r'^create/$', "create_or_edit", name='project_create'),
)
