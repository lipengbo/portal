from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('invite.views',
    url(r'^invite/(?P<target_type_id>\d+)/(?P<target_id>\d+)/$', "invite", name='invite_invite'),
)

