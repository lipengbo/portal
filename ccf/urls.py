from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.views.generic import TemplateView

from django.contrib import admin
admin.autodiscover()
#import xadmin
#xadmin.autodiscover()

#from xadmin.plugins import xversion
#xversion.registe_models()

urlpatterns = patterns("",
    url(r"^$", TemplateView.as_view(template_name="homepage.html"), name="home"),
    url(r"^login/", TemplateView.as_view(template_name="login.html"), name="home"),
    url(r"^help/", TemplateView.as_view(template_name="help.html"), name="home"),
    url(r"^create_project/", TemplateView.as_view(template_name="create_project.html"), name="home"),
    url(r"^detail_project/", TemplateView.as_view(template_name="detail_project.html"), name="home"),

    url(r"^project/", include("project.urls")),
    url(r"^slice/", include("slice.urls")),
    url(r"^admin/", include(admin.site.urls)),
#    url(r'^xadmin/', include(xadmin.site.urls)),
    url(r"^accounts/", include("account.urls")),
)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
