from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('project.views',
    url(r'^$', "index", name='project_index'),
    url(r'^detail/(?P<id>\d+)/$', "detail", name='project_detail'),
    url(r'^edit/(?P<id>\d+)/$', "create_or_edit", name='project_edit'),
    url(r'^delete/project/(?P<id>\d+)/$', "delete_project", name='project_delete'),
    url(r'^delete/member/(?P<id>\d+)/$', "delete_member", name='project_delete_member'),
    url(r'^create/$', "create_or_edit", name='project_create'),
    url(r'^apply/$', "apply", name='project_apply'),
)
