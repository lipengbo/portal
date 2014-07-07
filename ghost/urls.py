from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('ghost.views',
    url(r'^create_snapshot/$', "create_snapshot", name="create_snapshot"),
    url(r'^list_snapshot/$', "list_snapshot", name="list_snapshot"),
    url(r'^delete_snapshot/$', "delete_snapshot", name="delete_snapshot"),
    url(r'^restore_snapshot/$', "restore_snapshot", name="restore_snapshot"),
)
