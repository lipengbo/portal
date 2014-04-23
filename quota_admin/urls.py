from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('quota_admin.views',
    url(r'^$', "index", name='quota_admin_index'),
)
