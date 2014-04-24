
var switch_ports_info = parent.switch_ports_info;
function show_switch_port(_dpid){
    var switch_name = switch_ports_info({dpid:_dpid}).first().switch_name;
    parent._switch_name = switch_name;
    parent._dpid = _dpid;
    parent.document.getElementById("_switch_port").innerHTML = switch_name;
    var port_content = '<option value>------</option>';    
    switch_ports_info({dpid:_dpid}).each(function(s){
        port_content = port_content + '<option id='+ s.port_id +' value='+ s.port_type +'>' + s.port_name + '</option>';
    });
    parent.document.getElementById("enable_switch_port").innerHTML = port_content;
}
