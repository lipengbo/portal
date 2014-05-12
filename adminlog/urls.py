from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('adminlog.views',
    url(r'^$', "index", name='adminlog_index'),
)
