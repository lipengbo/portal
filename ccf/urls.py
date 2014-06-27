from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.views.generic import TemplateView

import notifications

from profiles.views import SignupView
from profiles.forms import SignupForm
from profiles.views import ConfirmEmailView
from django.views.generic.simple import direct_to_template

from django.contrib import admin
admin.autodiscover()
import django_cron
if settings.ENABLE_CRON:
    django_cron.autodiscover()

urlpatterns = patterns("",
    url(r"^$",  "project.views.home", name="home"),
    url(r"^global/$", TemplateView.as_view(template_name="homepage.html"), name="global"),
    url(r"^login/", TemplateView.as_view(template_name="login.html"), name="demo"),
    url(r"^help/", TemplateView.as_view(template_name="help.html"), name="demo"),
# <<<<<<< HEAD
# =======
#     url(r"^create_project/", TemplateView.as_view(template_name="create_project.html"), name="demo"),
#     url(r"^detail_project/", TemplateView.as_view(template_name="detail_project.html"), name="demo"),
#     url(r"^create_slice1/", TemplateView.as_view(template_name="create_slice1.html"), name="demo"),
#     url(r"^create_slice2/", TemplateView.as_view(template_name="create_slice2.html"), name="demo"),
#     url(r"^create_slice3/", TemplateView.as_view(template_name="create_slice3.html"), name="demo"),
#     url(r"^create_slice4/", TemplateView.as_view(template_name="create_slice4.html"), name="demo"),
#     url(r"^create_slice5/", TemplateView.as_view(template_name="create_slice5.html"), name="demo"),
#     url(r"^detail_slice/", TemplateView.as_view(template_name="detail_slice.html"), name="demo"),
#     url(r"^create_slice/", TemplateView.as_view(template_name="create_slice.html"), name="demo"),
#     url(r"^project_manage/", TemplateView.as_view(template_name="project_manage.html"), name="proje_manage"),
#     url(r"^list_project/", TemplateView.as_view(template_name="list_project.html"), name="demo"),
#     url(r"^list_slice/", TemplateView.as_view(template_name="list_slice.html"), name="demo"),
#     url(r"^list_vm/", TemplateView.as_view(template_name="list_vm.html"), name="demo"),
#     url(r"^apply_project/", TemplateView.as_view(template_name="apply_project.html"), name="demo"),
#     url(r"^homepage/", TemplateView.as_view(template_name="homepage.html"), name="demo"),
#     url(r"^logs/", TemplateView.as_view(template_name="logs.html"), name="demo"),
#     url(r"^logs_handle/", TemplateView.as_view(template_name="logs_handle.html"), name="demo"),
#     url(r"^member_check/", TemplateView.as_view(template_name="member_check.html"), name="demo"),
#     url(r"^invite_member/", TemplateView.as_view(template_name="invite_member.html"), name="demo"),
#     url(r"^404error/", TemplateView.as_view(template_name="404.html"), name="demo"),
#     url(r"^500error/", TemplateView.as_view(template_name="500.html"), name="demo"),
#     url(r"^502error/", TemplateView.as_view(template_name="502.html"), name="demo"),
#     url(r"^manage_index/", 'project.views.manage_index', name="manage_index"),
#     url(r"^check_quota/", TemplateView.as_view(template_name="check_quota.html"), name="demo"),
#     url(r"^apply_expanding_quota/", TemplateView.as_view(template_name="apply_expanding_quota.html"), name="demo"),
#     url(r"^basenet/", TemplateView.as_view(template_name="basenet.html"), name="demo"),
#
# >>>>>>> 8db340c2dbe23426749528106cb7a30cee5e9c6b

#    url(r"^monitor/", TemplateView.as_view(template_name="monitor.html"), name="demo"),
#    url(r"^jxbf_jx/", TemplateView.as_view(template_name="jxbf_jx.html"), name="demo"),
#    url(r"^jxbf_bf/", TemplateView.as_view(template_name="jxbf_bf.html"), name="demo"),

    url(r"^manage_index/", 'project.views.manage_index', name="manage_index"),
    url(r"^password_change_success/$", TemplateView.as_view(template_name="account/password_change_success.html"), name="password_change_success"),
    url(r"^signup_confirmation_complete/$", TemplateView.as_view(template_name="account/signup_confirmation_complete.html"), name="signup_confirmation_complete"),
    url(r"^password_reset_success/$", TemplateView.as_view(template_name="account/password_reset_success.html"), name="password_reset_success"),
    url(r"^forbidden/", TemplateView.as_view(template_name="forbidden.html"), name="forbidden"),
    #url(r'^ticket/', include('helpdesk.urls')),
    url(r'^ticket/forum/1/$', 'common.views.list_ticket', name="list_ticket"),
    url(r'^ticket/', include('agora.urls')),
    url(r'^misc/', include('common.urls')),



    url(r"^accounts/signup/$", SignupView.as_view(form_class=SignupForm), name="account_signup"),
    url(r"^accounts/confirm_email/(?P<key>\w+)/$", ConfirmEmailView.as_view(), name="account_confirm_email"),
    url('^notifications/', include(notifications.urls)),
    url('^quota_admin/', include("quota_admin.urls")),
    url('^log/', include("adminlog.urls")),

    url(r'^topology/$', 'project.views.topology', name="topology_view"),
    url(r'^(topology/.+\.html)$', direct_to_template, ),
    url(r'^direct/(?P<host>[\d\.]+):(?P<port>\d+)/wm/core/switch/(?P<dpid>[\w:]+)/aggregate/json', 'project.views.swicth_aggregate'),
    url(r'^direct/(?P<host>[\d\.]+):(?P<port>\d+)/wm/core/switch/(?P<dpid>[\w:]+)/desc/json', 'project.views.swicth_desc'),
    url(r'^direct/(?P<host>[\d\.]+):(?P<port>\d+)/wm/device/', 'project.views.device_proxy'),
    url(r'^direct/(?P<host>[\d\.]+):(?P<port>\d+)/wm/topology/links/json', 'project.views.links_direct'),
    url(r'^direct/(?P<host>[\d\.]+):(?P<port>\d+)/wm/', 'project.views.switch_direct'),

    url(r'^(?P<host>[\d\.]+):(?P<port>\d+)/wm/core/switch/(?P<dpid>[\w:]+)/aggregate/json', 'project.views.swicth_aggregate'),
    url(r'^(?P<host>[\d\.]+):(?P<port>\d+)/wm/core/switch/(?P<dpid>[\w:]+)/desc/json', 'project.views.swicth_desc'),
    url(r'^(?P<host>[\d\.]+):(?P<port>\d+)/wm/device/', 'project.views.device_proxy'),
    url(r'^(?P<host>[\d\.]+):(?P<port>\d+)/wm/topology/links/json', 'project.views.links_proxy'),
    url(r'^(?P<host>[\d\.]+):(?P<port>\d+)/wm/', 'project.views.switch_proxy'),


    url(r"^project/", include("project.urls")),
    url(r"^slice/", include("slice.urls")),
    url(r"^resources/", include("resources.urls")),
    url(r"^profiles/", include("profiles.urls")),
    url(r"^plugins/vt/", include("plugins.vt.urls")),
    url(r"^plugins/images/", include("plugins.images.urls")),
    url(r"^invite/", include("invite.urls")),
    url(r"^admin/", include(admin.site.urls)),
    #url(r'^admin/', include(xadmin.site.urls)),
    url(r"^accounts/", include("account.urls")),
    url(r'^xmlrpc/$', 'django_xmlrpc.views.handle_xmlrpc', name='xmlrpc'),
    url(r"^nexus/", include("nexus.urls")),
    url(r"^monitor/", include("monitor.urls")),
    url(r"^ghost/", include("ghost.urls")),
)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
