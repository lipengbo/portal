from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('quota_admin.views',
    url(r'^apply/$', "index", name='quota_admin_apply'),
    url(r'^quota/$', "quota", name='quota_admin_quota'),
)
