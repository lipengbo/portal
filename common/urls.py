from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('common.views',
    url(r'^$', "index", name='common_index'),
)
