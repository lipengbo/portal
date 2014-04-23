var switch_ports_info = TAFFY();
var selected_switch_ports = TAFFY();
$(document).ready(function(){
    $.ajax({
                url : "/plugins/vt/get_switch_port/",
                type : "GET",
                contentType: "application/json; charset=utf-8",
                dataType : "json",
                async : false,
                error : function(e){
			        //document.getElementById('alert_info').innerHTML = "获取网关IP出错！";
			       // $('#alert_modal').modal('show');
                    // alert("获取网关IP出错！");
                },
                success : function(switchs){
                    $.each(switchs, function(i, _switch){
                        $.each(_switch['ports'], function(j, _port){
                            switch_ports_info.insert({id:_switch['id'], dpid:_switch['dpid'], switch_name:_switch['name'],
                                                    port_name:_port['name'], port_num:_port['port'], port_type:_port['type']});
                        });
                        
                    });
                }
    });
    $('.device_access_savebtn').on("click", function(){
        if(!check_port()) return;
        if(check_macs()){
            $('.mac_addrs').removeClass('has-error');
            document.getElementById('mac_err_msg').innerHTML = '';
        }
        
    });
    
    //var default_switch_name = switch_ports_info().first().switch_name;
    show_switch_port(switch_ports_info().first().dpid);
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

function show_switch_port(_dpid){
    document.getElementById("_switch_port").innerHTML = '<strong>' 
                                                        + switch_ports_info({dpid:_dpid}).first().switch_name
                                                        + '</strong>';
    var port_content = '<option value>------</option>';    
    switch_ports_info({dpid:_dpid}).each(function(s){
        port_content = port_content + '<option value='+ s.port_type +'>' + s.port_name + '</option>';
    });
    document.getElementById("enable_switch_port").innerHTML = port_content;
}

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
    var mac_addrs = $('#mac_addrs').val().trim().split(";");
    for(var i=0; i<mac_addrs.length; i++){
        alert(mac_addrs[i]);
        if(mac_addrs[i] == null){
            alert('mac null')
            $('.mac_addr').addClass('has-error');
            document.getElementById('mac_err_msg').innerHTML = '该项为必填项';
            return false;
        }
        if(!isMac(mac_addrs[i])){
            $('.mac_addr').addClass('has-error');
            alert('mac err');
            document.getElementById('mac_err_msg').innerHTML = 'mac地址格式不正确';
            return false;
        }
    }
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


