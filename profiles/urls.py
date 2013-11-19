from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('profiles.views',
    url(r'^send_confirmation/(?P<id>\d+)/$', "send_confirmation", name='profiles_confirmation'),
    url(r'^reject/(?P<id>\d+)/$', "reject", name='profiles_reject'),
)
