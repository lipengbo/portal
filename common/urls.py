from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('common.views',
    url(r'^$', "index", name='common_index'),
    url(r'^close/thread/(?P<thread_id>\d+)/$', "close_thread", name='common_close_thread'),
)
