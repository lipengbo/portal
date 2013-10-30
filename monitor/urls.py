from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('monitor.views',
	url(r'^vm/(?P<host_id>\d+)/(?P<vm_id>\d+)/$', "monitor_vm", name="monitor_vm"),
    url(r'^host/(?P<host_id>\d+)/$', "monitor_host", name="monitor_host"),
    url(r"^monitor/ovs/(?P<host_id>\d+)/$", "monitor_ovs", name="monitor_ovs"),
    url(r"^monitor/port/$", "monitor_port", name="monitor_port"),
    url(r'^update_performace_data/host/$', "update_host_performace_data", name="update_host_performace_data"),
    #url(r'^update_performace_data/vm/(?P<host_id>\d+)/(?P<vm_id>\d+)/$', "update_vm_performace_data", name="update_vm_performace_data"),
    url(r'^update_performace_data/vm/$', "update_vm_performace_data", name="update_vm_performace_data"),
)
