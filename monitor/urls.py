from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('monitor.views',
	url(r'^vm/(?P<vm_id>\d+)/$', "monitor_vm", name="monitor_vm"),
    url(r'^Server/(?P<host_id>\d+)/$', "monitor_host", name="monitor_host"),
    url(r"^Switch/(?P<switch_id>\d+)/$", "monitor_switch", name="monitor_switch"),
    url(r"^VirtualSwitch/(?P<switch_id>\d+)/$", "monitor_switch", name="monitor_switch"),
    url(r"^get_br_info/(?P<switch_id>\d+)/$", "get_br_info", name="get_br_info"),
    url(r"^get_switch_port_info/(?P<switch_id>\d+)/$", "get_switch_port_info", name="get_switch_port_info"),
    url(r"^port/$", "update_port_performace_data", name="update_port_performace_data"),
    url(r'^update_performace_data/host/$', "update_host_performace_data", name="update_host_performace_data"),
    url(r'^update_index_data/$', "update_index_performace_data", name="update_index_performace_data"),
    #url(r'^update_performace_data/vm/(?P<host_id>\d+)/(?P<vm_id>\d+)/$', "update_vm_performace_data", name="update_vm_performace_data"),
    url(r'^update_performace_data/vm/$', "update_vm_performace_data", name="update_vm_performace_data"),
)
