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
                            port_name:_port['name'], port_num:_port['port'], port_id:_port['id'], port_type:_port['can_monopolize']});
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
    $("#topologyiframe").attr("src", "/slice/topology_d3/?slice_id="+sliceid+"&width=700&height=400&top=0&band=0&own_device=1");
    $('.mac_addrs').hide();
    /*$('.device_access_savebtn').on("click", function(){
        if(selected_switch_ports().count() != 0){
            show_err_msg('请先提交已保存的端口，或删除后重新选择');
            return;
        }
        if(!check_port()) return;
        if(!$('.switch_btn.dk').hasClass("checked")){
            if(check_macs()){
                document.getElementById('mac_err_msg').innerHTML = '';
            }else{
                return;
            }
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
        
        //show_port_info_table();
    });*/
    
    $("#enable_switch_port").change(function(){
        $('.tuopu_btn.dk').removeClass("disabled");
        if($("#enable_switch_port").find("option:selected").val() == 0){
            //非独占
            $('.switch_btn.dk').removeClass("checked");
            $('.switch_btn.dk').children(".switch_content").html("否");
            $('.tuopu_btn.dk').addClass("disabled");
            $(".mac_addrs").show();
        }else{
            $('.switch_btn.dk').addClass("checked");
            $('.switch_btn.dk').children(".switch_content").html("是");
            $("#mac_addrs").val('');
            $(".mac_addrs").hide();
            
        }
    });
    $('#enable_switch_port').on("blur", function(){
        check_port();
        if(check_macs()){
            document.getElementById('mac_err_msg').innerHTML = '';
        return true;
        }
    })
    $("#mac_addrs").on("focus", function(){
        $("#mac_addrs").val('');
    }).on("blur", function(){
        check_macs();
    });
    $('.switch_btn.dk').on("click", function(){
			if($(this).hasClass("checked")) {
                $(this).removeClass("checked");
                $(this).children(".switch_content").html("否");
                $("#mac_addrs").val('示例：a4:1f:72:50:78:9a,a4:1f:72:50:78:9b');
                $('.mac_addrs').show();
            }else{
				$(this).addClass("checked");
                $(this).children(".switch_content").html("是");
                $('#mac_addrs').val('');
                $('.mac_addrs').hide();
			}
		});
    
})



function check_port(){
    if($("#enable_switch_port").find("option:selected").val() == ''){
        $('#port_err_msg').html('该项为必填项');
        return false;
    }else{
        $('#port_err_msg').html('');
        return true;
    }
}

function check_macs(){
    if($('#mac_addrs').val().trim() == ""){
        $('#mac_err_msg').html('该项为必填项');
        return false;
    }
    var mac_addrs = $('#mac_addrs').val().trim().split(",");
    for(var i=0; i<mac_addrs.length; i++){
        if(!isMac(mac_addrs[i])){
            $('#mac_err_msg').html('MAC地址格式不正确');
            return false;
        }
    }
    $('#mac_err_msg').html('');
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

/*
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
}*/

function show_err_msg(msg){
    var str = "<p class=\"text-center\">"+msg+"</p>";
    $("#port_alert_info").empty().append(str);
    $('#portalertModal').modal('show');
}

function commit_ports(sliceid){
    if(!check_port()) return;
    if(!$('.switch_btn.dk').hasClass("checked")){
        if(check_macs()){
            document.getElementById('mac_err_msg').innerHTML = '';
        }else{
            return;
        }
    }
    _port_id = parseInt($("#enable_switch_port").find("option:selected").attr("id"));
    _port_name = $("#enable_switch_port").find("option:selected").text();
    if ($('.switch_btn.dk').hasClass("checked")){
        _port_type = 0;
    }else{
        _port_type = 1;
    }
    selected_switch_ports.insert({switch_name:_switch_name, dpid: _dpid, port_id: _port_id, port_name: _port_name,
                                     port_type:_port_type, macs: $('#mac_addrs').val().trim()});

    var ports_data = JSON.stringify(selected_switch_ports().select("port_id", "port_type", "macs"));    
    $.ajax({
        url: '/plugins/vt/add_own_ports/'+sliceid+'/',
        type: 'POST',
        data: {"ports_data" : ports_data},
        dataType : "json",
        async: false,
        success:function(data){
            if(data.result == 1){
                var str = '/slice/detail/' + sliceid + '/';
                $(".modal-footer").html("<button class='btn delete-confirm btn_info' data-dismiss='modal' onclick='document.location=&quot;"+str+"&quot;'>确定</button>");
                show_err_msg('添加端口失败，请稍后重试');
            }else{
                window.location.href='/slice/detail/' + sliceid + '/';
            }
            
        }
        
    });
}
