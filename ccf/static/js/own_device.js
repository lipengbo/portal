var switch_ports_info = TAFFY();
var selected_switch_ports = TAFFY();

var _switch_name, _dpid, _port_id, _port_name, _port_type, _port_type_content;

$(document).ready(function(){
    $.ajax({
        url : "/plugins/vt/get_switch_port/"+sliceid+"/",
        type : "GET",
        dataType : "json",
        //async : false,
        error : function(e){
        },
        success : function(switchs){
            $.each(switchs, function(i, _switch){
                $.each(_switch['ports'], function(j, _port){
                    switch_ports_info.insert({id:_switch['id'], dpid:_switch['dpid'], switch_name:_switch['name'],
                            port_name:_port['name'], port_num:_port['port'], port_id:_port['id'], port_type:_port['type']});
                });
                        
            });
            _dpid = switch_ports_info().first().dpid;
            _switch_name = switch_ports_info({dpid:_dpid}).first().switch_name;
            document.getElementById("_switch_port").innerHTML = _switch_name;
            var port_content = '<option value>------</option>';    
            switch_ports_info({dpid:_dpid}).each(function(s){
                port_content = port_content + '<option id='+ s.port_id + ' value='+ s.port_type +'>' + s.port_name + '</option>';
            });
            document.getElementById("enable_switch_port").innerHTML = port_content;
       }
    });
    $('.device_access_savebtn').on("click", function(){
        if(!check_port()) return;
        if(check_macs()){
            $('.mac_addrs').removeClass('has-error');
            document.getElementById('mac_err_msg').innerHTML = '';
        }
        _port_id = parseInt($("#enable_switch_port").find("option:selected").attr("id"));
        _port_name = $("#enable_switch_port").find("option:selected").text();
        if ($('.switch_btn.dk').hasClass("checked")){
            _port_type = 0;
            _port_type_content = '是';
        }else{
            _port_type = 1;
            _port_type_content = '否';
        }
        if (selected_switch_ports({port_id:_port_id}).count() != 0){
            var str = "<p class=\"text-center\">不可以重复添加端口</p>";
            $("#port_alert_info").empty().append(str);
            $('#portalertModal').modal('show');            
            return;
        }
        selected_switch_ports.insert({switch_name:_switch_name, dpid: _dpid, port_id: _port_id, port_name: _port_name,
                                     port_type:_port_type, port_type_content:_port_type_content, 
                                     macs: $('#mac_addrs').val().trim()});
        
        show_port_info_table();
    });
    
    $("#enable_switch_port").change(function(){
        $('.tuopu_btn.dk').removeClass("disabled");
        if($("#enable_switch_port").find("option:selected").val() == 0){
            //非独占
            $('.switch_btn.dk').removeClass("checked");
            $('.switch_btn.dk').children(".switch_content").html("否");
            $('.tuopu_btn.dk').addClass("disabled");
        }else{
            $('.switch_btn.dk').addClass("checked");
            $('.switch_btn.dk').children(".switch_content").html("是");
        }
    });
    $('#enable_switch_port').on("blur", function(){
        check_port();
        if(check_macs()){
            $('.mac_addrs').removeClass('has-error');
            document.getElementById('mac_err_msg').innerHTML = '';
        return true;
        }
    })

    $('.switch_btn.dk').on("click", function(){
			if($(this).hasClass("checked")) {
                $(this).removeClass("checked");
                $(this).children(".switch_content").html("否");
            }else{
				$(this).addClass("checked");
                $(this).children(".switch_content").html("是");
			}
		});
    
})



function check_port(){
    if($("#enable_switch_port").find("option:selected").val() == ''){
        $('.form-group.switch_port').addClass('has-error');
        document.getElementById('port_err_msg').innerHTML = '该项为必填项';
        return false;
    }else{
        $('.form-group.switch_port').removeClass('has-error');
            document.getElementById('port_err_msg').innerHTML = '';
        return true;
    }
}

function check_macs(){
    if($('#mac_addrs').val().trim() == ""){
        $('.mac_addr').addClass('has-error');
        document.getElementById('mac_err_msg').innerHTML = '该项为必填项';
        return false;
    }
    var mac_addrs = $('#mac_addrs').val().trim().split(";");
    for(var i=0; i<mac_addrs.length; i++){
        if(!isMac(mac_addrs[i])){
            $('.mac_addr').addClass('has-error');
            document.getElementById('mac_err_msg').innerHTML = 'mac地址格式不正确';
            return false;
        }
    }
    return true;
}

function isMac(macaddr)
{
   var reg = /^[A-Fa-f0-9]{1,2}\:[A-Fa-f0-9]{1,2}\:[A-Fa-f0-9]{1,2}\:[A-Fa-f0-9]{1,2}\:[A-Fa-f0-9]{1,2}\:[A-Fa-f0-9]{1,2}$/;
   if (reg.test(macaddr)) {
        return true;
   }else {
        return false;
   }
}

function show_port_info_table(){
    $("#port_info_table").find("tbody").empty();
    selected_switch_ports().each(function(port){
    $("#port_info_table").find("tbody").append("<tr>"
                            +"<td>"+port.switch_name+"</td>"
                            +"<td>"+port.dpid+"</td>"
                            +"<td>"+port.port_name+"</td>"
                            +"<td>"+port.port_type_content+"</td>"
                            +"<td>"+port.macs+"</td>"
                            +"<td class='btn_operation'>"
                            +"   <a href='javascript:;' onclick='javascript:delete_portinfo("+port.port_id+")'>"
                            +"    <img src='"+STATIC_URL+"img/btn_sc.png' title='删除'>"
                            +"    </a>"
                            +"</td>"
                          +"</tr> ");
    });
}

function delete_portinfo(portid){
    selected_switch_ports({port_id:portid}).remove();
    show_port_info_table();
}
