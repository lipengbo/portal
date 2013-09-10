from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('project.views',
    url(r'^$', "index", name='project_index'),
    url(r'^create/$', "create", name='project_create'),
)
