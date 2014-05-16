//虚拟机启动停止click事件
function start_stop_vm(vm_id, vm_type){
    var a_obj = $("#"+vm_id+"_qt")[0];
    if(a_obj.style.cursor == "not-allowed"){
        //alert(0);
        return;
    }
    var img_obj = $("#"+vm_id+"_qt").children("img")[0];
    var STATIC_URL = $("#STATIC_URL").text();
    if(img_obj.title == "启动"){
        //alert(1);
        ret = start_or_stop_vm(vm_id, "create");
        if(ret){
            img_obj.src = STATIC_URL + "img/ic-ks-un.png";      
            img_obj.title = "启动中";//"停止";
            //$("#icon_state"+vm_id).removeClass("icon-minus-sign").addClass("icon-ok-sign");
			$("#icon_state"+vm_id)
				.removeClass("icon-minus-sign")
                .removeClass("icon_state")
                .addClass("icon-spinner")
                .addClass("icon-spin")
				.addClass("check_vm");
            //document.getElementById('topologyiframe').contentWindow.topology_update_vm_state(vm_id, 1);
            //a_obj = $("#"+vm_id+"_dl")[0];
            //img_obj = $("#"+vm_id+"_dl").children("img")[0];
            //a_obj.style.cursor = "pointer";
            //img_obj.src = STATIC_URL + "img/btn_dl.png";
			update_vm_status(); 
        }else{
            //alert(1);
        }
    } else {
        //alert(2);
        ret = start_or_stop_vm(vm_id, "destroy");
        if(ret){
            img_obj.src = STATIC_URL + "img/ic-tz-un.png";       
            img_obj.title = "停止中";//"启动";
            //$("#icon_state"+vm_id).removeClass("icon-ok-sign").addClass("icon-minus-sign");
			$("#icon_state"+vm_id).removeClass("icon-ok-sign").removeClass("icon_state")
								  .addClass("icon-spinner").addClass("icon-spin").addClass("check_vm");
            //document.getElementById('topologyiframe').contentWindow.topology_update_vm_state(vm_id, 5);
            a_obj = $("#"+vm_id+"_dl")[0];
            img_obj = $("#"+vm_id+"_dl").children("img")[0];
            a_obj.style.cursor = "not-allowed";
            img_obj.src = STATIC_URL + "img/btn_dl_gray.png"; 
			update_vm_status();
        }else{
            //alert(2);
        }
    }
}

//ajax启停虚拟机
function start_or_stop_vm(vm_id, flag){
    check_url = "http://" + window.location.host + "/plugins/vt/do/vm/action/"+vm_id+"/"+flag+"/";
    //alert(check_url)
    var ret = false;
    $.ajax({
        type: "GET",
        url: check_url,
        dataType: "json",
        cache: false,
        async: false,  
        success: function(data) {
            if (data.result==1)
             {
                //alert("failed");
                $("div#slice_alert_info").empty();
                var str = "" + "<p class=\"text-center\">" + data.error + "</p>";
                $("div#slice_alert_info").append(str);
                $('#slicealertModal').modal('show');
             } 
             else
             {
                //alert("ok");
                ret = true;
             }
        }
    });
    return ret;
}

//虚拟机监控click事件
function jk_vm(vm_id){
    var a_obj = $("#"+vm_id+"_jk")[0];
    if(a_obj.style.cursor == "not-allowed"){
        //alert(0);
        return;
    }
    document.location='/monitor/vm/'+vm_id+'/';
}

//虚拟机登录click事件
function dl_vm(vm_id){
    var a_obj = $("#"+vm_id+"_dl")[0];
    //alert(a_obj.attr("style"));
    if(a_obj.style.cursor == "not-allowed"){
        //alert(0);
        return;
    }
    window.open("http://" + window.location.host + "/plugins/vt/vm/vnc/"+vm_id+"/");
}


//控制器编辑click事件
function bj_vm(vm_id){
    var a_obj = $("#"+vm_id+"_bj")[0];
    var slice_type = $("#slice_type").text();
    //alert(a_obj.attr("style"));
    if(a_obj.style.cursor == "not-allowed"){
        //alert(0);
        return false;
    }else{
        //alert(1);
        if(slice_type == "baseslice"){
            $('#editbasectModal').modal('show');
        }else{
            $('#editmixctModal').modal('show');
        }
        return false;
    }
}


//控制器添加click事件
function add_ct(){
    var a_obj = $("#add_ct")[0];
    var slice_type = $("#slice_type").text();
    //alert(a_obj.attr("style"));
    if(a_obj.style.cursor == "not-allowed"){
        //alert(0);
        return false;
    }else{
        if(slice_type == "baseslice"){
            $('#editbasectModal').modal('show');
        }else{
            $('#editmixctModal').modal('show');
        }
        return true;
    }
}

//虚拟机删除click事件
function sc_vm(vm_id){
    var a_obj = $("#"+vm_id+"_sc")[0];
    //alert($('.endless_page_current')[0].innerHTML);
    //alert(document.location);
    if(a_obj.style.cursor == "not-allowed"){
        return false;
    }else{
        $('#alertModal').modal();
        $('.delete-confirm').unbind('click');
        $('.delete-confirm').click(function(){
            ret = delete_vm(vm_id);
            if(ret){
                document.getElementById('topologyiframe').contentWindow.topology_del_vm(vm_id);
                
                if($('.endless_page_current')[0]){
                    c_p = $('.endless_page_current')[0].innerHTML;
                    url = document.location + "?page=" + c_p + "#topsection";
                    update_list(url);
                }else{
                    url = document.location + "?";
                    update_list(url);
                }
            }
        });
        return false;
    }
}

//ajax删除虚拟机
function delete_vm(vm_id){
    check_url = "http://" + window.location.host + "/plugins/vt/delete/vm/"+vm_id+"/"+0+"/";
    //alert(check_url)
    var ret = false;
    $.ajax({
        type: "GET",
        url: check_url,
        dataType: "json",
        cache: false,
        async: false,  
        success: function(data) {
            if (data.result==1)
            {
                $("div#slice_alert_info").empty();
                var str = "" + "<p class=\"text-center\">" + data.error_info + "</p>";
                $("div#slice_alert_info").append(str);
                $('#slicealertModal').modal('show');
             } 
             else
             {
                ret = true;
             }
        }
    });
    return ret;
}


//虚网启动停止click事件
function start_stop_slice(slice_id){
    var a_obj = $("#slice_qt")[0];
    if(a_obj.style.cursor == "not-allowed"){
        //alert(0);
        return;
    }
    var img_obj = $("#slice_qt").children("img")[0];
    var STATIC_URL = $("#STATIC_URL").text();
    if(img_obj.title == "启动"){
        //alert(1);
        ret = start_or_stop_slice(slice_id, 1);
        if(ret){
            //slice状态和操作状态变化
            //alert("in1");
            $("#slice_state")
                .removeClass("icon-minus-sign")
                .removeClass("icon_state")
                .addClass("icon-spinner")
                .addClass("icon-spin");
            a_obj.style.cursor = "not-allowed";
            img_obj.src = STATIC_URL + "img/ic-ks-un.png";       
            img_obj.title = "启动中"; 
            //控制器编辑、slice编辑按钮变化
            $(".bianji").attr("style","cursor:not-allowed");
            $(".bianji").children("img").attr("src",STATIC_URL+"img/btn_bj_gray.png");
            //vm删除、port删除
            $(".shanchu").attr("style","cursor:not-allowed");
            $(".shanchu").children("img").attr("src",STATIC_URL+"img/btn_sc_gray.png");
            //dhcp启停、vm添加
            $(".dhcp_div").addClass("disabled");
            $(".dhcp").attr("style","cursor:not-allowed");
            $("#vm_add").addClass("disabled").attr("style","cursor:not-allowed");
            //controller、gw状态和操作
            if ($(".default_create").length > 0){
                vm_id = $(".default_create")[0].getAttribute("vm_id");
                if($("#icon_state"+vm_id).hasClass("icon-minus-sign")){
                    img_obj = $("#"+vm_id+"_qt").children("img")[0];
                    img_obj.src = STATIC_URL + "img/ic-ks-un.png";     
                    img_obj.title = "启动中";
                    $("#icon_state"+vm_id)
                        .removeClass("icon-minus-sign")
                        .removeClass("icon_state")
                        .addClass("icon-spinner")
                        .addClass("icon-spin");
                }
            }
            if ($(".gw").length > 0){
                vm_id = $(".gw")[0].getAttribute("vm_id");
                if($("#icon_state"+vm_id).hasClass("icon-minus-sign")){
                    img_obj = $("#"+vm_id+"_qt").children("img")[0];
                    img_obj.src = STATIC_URL + "img/ic-ks-un.png";      
                    img_obj.title = "启动中";
                    $("#icon_state"+vm_id)
                        .removeClass("icon-minus-sign")
                        .removeClass("icon_state")
                        .addClass("icon-spinner")
                        .addClass("icon-spin");
                }
            }
            update_slice_status(); 
        }else{
            //alert("in2");
            //alert(1);
        }
    } else {
        //alert(2);
        ret = start_or_stop_slice(slice_id, 0);
        if(ret){
            //slice状态和操作状态变化
            $("#slice_state")
                .removeClass("icon-ok-sign")
                .removeClass("icon_state")
                .addClass("icon-spinner")
                .addClass("icon-spin");
            a_obj.style.cursor = "not-allowed";
            img_obj.src = STATIC_URL + "img/ic-tz-un.png";       
            img_obj.title = "停止中";
            update_slice_status();
        }else{
            //alert(2);
        }
    }
}

//ajax启停slice
function start_or_stop_slice(slice_id, flag){
    check_url = "http://" + window.location.host + "/slice/start_or_stop/"+slice_id+"/"+flag+"/";
    //alert(check_url)
    var ret = false;
    $.ajax({
        type: "GET",
        url: check_url,
        dataType: "json",
        cache: false,
        async: false,  
        success: function(data) {
            if (data.value == 1)
             {
                //alert("ok");
                ret = true;
             } 
             else
             {
                //alert(data.error_info);
                $("#slice_alert_info").empty();
                var str = "" + "<p class=\"text-center\">" + data.error_info + "</p>";
                $("#slice_alert_info").append(str);
                $('#slicealertModal').modal('show');
             }
        }
    });
    return ret;
}


//slice编辑click事件
function bj_slice(vm_id){
    var a_obj = $("#slice_bj")[0];
    //alert(a_obj.attr("style"));
    if(a_obj.style.cursor == "not-allowed"){
        //alert(0);
        return false;
    }else{
        //alert(1);
        $('#editInfoModal').modal('show');
        return true;
    }
}

//带宽监控与dhcp启停按钮点击事件
$(".switch_btn").live("click", function(){
    if($(this)[0].style.cursor == "not-allowed"){
        //alert(1);
        return false;
    }
    //alert(2);
    if($(this).hasClass("checked")) {
        //alert(3);
        if($(this).hasClass("dhcp")){
            slice_id = $("#slice_id").text();
            ret = set_dhcp(slice_id, 0);
            //alert(ret);
            if(ret){
                $(this).removeClass("checked");
                $(this).children(".switch_content").html("停止");
            }
        }else{
            if($(this).hasClass("add_dhcp")){
                $(this).removeClass("checked");
                $(this).children(".switch_content").html("否");
            }else{
                document.getElementById('topologyiframe').contentWindow.random_refresh2 (0);
                $(this).removeClass("checked");
                $(this).children(".switch_content").html("停止");
            }
        }
    }else {
        //alert(4);
        if($(this).hasClass("dhcp")){
            slice_id = $("#slice_id").text();
            ret = set_dhcp(slice_id, 1);
            //alert(ret);
            if(ret){
                $(this).addClass("checked");
                $(this).children(".switch_content").html("启动");
            }
        }else{
            if($(this).hasClass("add_dhcp")){
                $(this).addClass("checked");
                $(this).children(".switch_content").html("是");
            }else{
                document.getElementById('topologyiframe').contentWindow.random_refresh2 (1);
                $(this).addClass("checked");
                $(this).children(".switch_content").html("启动"); 
            }
        }
    }
    return false;
});

//ajax设置dhcp服务启停
function set_dhcp(slice_id, flag){
    var ret = false;
    $.ajax({
            url: '/slice/dhcp_switch/'+slice_id+"/"+flag+"/",
            type: 'GET',
            dataType: "json",
            cache: false,
            async: false,
            success: function(data){
                //alert(data.result);
                if(data.result == 0){
                    ret = true;
                }else{
                    $("div#slice_alert_info").empty();
                    str = "" + "<p class=\"text-center\">设置网关服务失败！</p>";
                    $("div#slice_alert_info").append(str);
                    $('#slicealertModal').modal('show');
                }
            }
        });
    return ret;
}


//添加设备
function select_to_add_device(slice_id){
    //判断是否有可用的边缘端口
    var ports = 0;
    $.ajax({
        url : "/plugins/vt/get_switch_port/"+slice_id+"/",
        type : "GET",
        dataType : "json",
        async : false,
        success : function(switchs){
            $.each(switchs, function(i, _switch){
                $.each(_switch['ports'], function(j, _port){
                   ports++;
                });
                        
            });
            if(ports == 0){
                $("#customdevice").attr("disabled", "disabled");
                document.getElementById("customdevice_msg").innerHTML = '*没有可用的边缘节点端口';
                document.getElementById("customdevice_msg").style.color = "red";
            }
       }
    });

    var a_obj = $("#vm_add")[0];
    //alert(a_obj.attr("style"));
    if(a_obj.style.cursor == "not-allowed"){
        //alert(0);
        return;
    }else{
        //alert(1);
        //location.href = "http://" + window.location.host + "/plugins/vt/create/vm/"+slice_id+"/0/";
		$("#adddevicetModal").modal('show');
    }
	//
}

function can_create_vm(slice_id){
    var a_obj = $("#vm_add")[0];
    if(a_obj.style.cursor == "not-allowed"){
        $("div#slice_alert_info").empty();
        str = "" + "<p class=\"text-center\">请确保虚网已停止！</p>";
        $("div#slice_alert_info").append(str);
        $('#slicealertModal').modal('show');
    }else{
        $.ajax({
            url: '/plugins/vt/can_create_vm/'+slice_id+'/',
            type: 'GET',
            dataType: 'json',
            success: function(data){
                if(data.result == 0){
                    location.href = "http://" + window.location.host + "/plugins/vt/create/vm/"+slice_id+"/";
                }else{
                    $("div#slice_alert_info").empty();
                    str = "" + "<p class=\"text-center\">虚拟机个数已达上限！</p>";
                    $("div#slice_alert_info").append(str);
                    $('#slicealertModal').modal('show');
                }
    
            }
        });
    }
}

function can_add_port(slice_id){
    //判断是否有可用的边缘端口
    var a_obj = $("#port_add")[0];
    if(a_obj.style.cursor == "not-allowed"){
        $("div#slice_alert_info").empty();
        str = "" + "<p class=\"text-center\">请确保虚网已停止！</p>";
        $("div#slice_alert_info").append(str);
        $('#slicealertModal').modal('show');
    }else{
        var ports = 0;
        $.ajax({
            url : "/plugins/vt/get_switch_port/"+slice_id+"/",
            type : "GET",
            dataType : "json",
            async : false,
            success : function(switchs){
                $.each(switchs, function(i, _switch){
                    $.each(_switch['ports'], function(j, _port){
                       ports++;
                    });
                            
                });
                if(ports == 0){
                    $("div#slice_alert_info").empty();
                    str = "" + "<p class=\"text-center\">没有可用的边缘节点端口！</p>";
                    $("div#slice_alert_info").append(str);
                    $('#slicealertModal').modal('show');
                }else{
                    location.href = "http://" + window.location.host + "/plugins/vt/create/device/"+slice_id+"/";
                }
           }
        });
    }
}

function delete_switch_port(sliceid, portid){
    var a_obj = $("#"+portid+"_sc_port")[0];
    if(a_obj.style.cursor == "not-allowed"){
        return false;
    }else{
        $('#alertModal').modal();
        $('.delete-confirm').unbind('click');
        $('.delete-confirm').click(function(){
            $.ajax({
                url: '/slice/delete_switch_port/' + sliceid + "/" + portid + "/",
                type: 'GET',
                dataType: 'json',
                success:function(data){
                    if(data.result == 1){
                        $("div#slice_alert_info").empty();
                        str = "" + "<p class=\"text-center\">删除端口失败！</p>";
                        $("div#slice_alert_info").append(str);
                        $('#slicealertModal').modal('show');
                    }else{
                        if($('.endless_page_current')[0]){
                            c_p = $('.endless_page_current')[0].innerHTML;
                            var url = document.location + "?port_page=" + c_p + "#topsection";
                            update_list(url);
                        }else{
                            var url = document.location + "?";
                            update_list(url);
                        }
                    }
                }
            });
        });
    }
}
function add_device(slice_id){
	var device_type = document.getElementsByName("device");
	 for(var i=0; i<device_type.length; i++){  
            if(device_type[i].checked){  
                if(device_type[i].value == "customdevice"){
					location.href = "http://" + window.location.host + "/plugins/vt/create/device/"+slice_id+"/";  
                }  
                if(device_type[i].value == "vmdevice"){
					location.href = "http://" + window.location.host + "/plugins/vt/create/vm/"+slice_id+"/";
                }  
            }   
        }
}

 //编辑slice描述信息
 function edit_description(slice_id){
    var ret;
    ret = check_slice_description('slice_description',1);
    if(ret){
        var obj = document.getElementById('slice_description');
        check_url = "http://" + window.location.host + "/slice/edit_description/"+slice_id+"/";
        $.ajax({
                type: "POST",
                url: check_url,
                dataType: "json",
                data: {"slice_description": obj.value},
                async: false, 
                success: function(data) {
                    if (data.result == 1){
                        //alert("ok");
                        var description_old = document.getElementById('slice_description_old');
                        description_old.innerHTML = obj.value;
                    }
                    else{
                        //alert(failed);
                        $("div#slice_alert_info").empty();
                        str = "" + "<p class=\"text-center\">编辑失败！</p>";
                        $("div#slice_alert_info").append(str);
                        $('#editSliceModal').modal('show');
                    }
                },
                error: function(data) {
                    $("div#slice_alert_info").empty();
                    str = "" + "<p class=\"text-center\">编辑失败！</p>";
                    $("div#slice_alert_info").append(str);
                    $('#slicealertModal').modal('show');
                }
        });
        $('#editInfoModal').modal('hide');
    }
 }


//缩写uuid
function show_uuid(objs){
    for (var i=0; i<objs.length; i++){
        objs[i].innerHTML = objs[i].innerHTML.split("-")[0].split(".") + "...";
    }
}


//提交虚拟网关信息
function submit_gw(slice_id){
    ret = check_gw_select();
    if(ret){
        var id_server_gw_obj = document.getElementById("id_server_gw");
        var gateway_ip_obj = document.getElementById("gateway_ip");
        var dhcp_selected = 0;
        if($('.switch_btn.add_dhcp').hasClass("checked")){
            dhcp_selected = 1; 
        }
        var id_server_gw_obj_value = 0;
        var gateway_ip_obj_value = '';
        if(id_server_gw_obj && gateway_ip_obj && id_server_gw_obj.value && gateway_ip_obj.value){
            id_server_gw_obj_value = id_server_gw_obj.value;
            gateway_ip_obj_value = gateway_ip_obj.value;
        }
        var submit_data = {"gw_host_id": id_server_gw_obj_value,
                    "gw_ip": gateway_ip_obj_value,
                    "dhcp_selected": dhcp_selected  
        };

        check_url = "http://" + window.location.host + "/slice/create_gw/"+slice_id+"/";
        var ajax_ret = true;
        $.ajax({
                type: "POST",
                url: check_url,
                dataType: "json",
                data: submit_data,
                async: false, 
                success: function(data) {
                    if (data.result == 1){
                        update_list_content(document.location, "list_fw");
    
                    }else{
                        $("div#slice_alert_info").empty();
                        str = "" + "<p class=\"text-center\">" + data.error_info + "</p>";
                        $("div#slice_alert_info").append(str);
                        $('#slicealertModal').modal('show');
                        ajax_ret = false;
                    }
                },
                error: function(data) {
                    $("div#slice_alert_info").empty();
                    str = "" + "<p class=\"text-center\">添加网关异常！</p>";
                    $("div#slice_alert_info").append(str);
                    $('#slicealertModal').modal('show');
                    ajax_ret = false;
                }
        });
        $('#addgwModal').modal('hide');
        $("div#ts").empty();
        update_vm_status();
    } 
}

//添加虚拟网关
function add_gw(){
    var a_obj = $("#add_gw")[0];
    var slice_uuid = $("#slice_uuid").text();
    var slice_id = $("#slice_id").text();
    if(a_obj.style.cursor == "not-allowed"){
        //alert(0);
        return false;
    }else{
        ret1 = fetch_gw_select_server(slice_id)
        ret2 = fetch_gateway_ip(slice_uuid);
        if(ret1 && ret2){
            $('#addgwModal').modal('show');
            return true;
        }else{
            $("div#slice_alert_info").empty();
            str = "" + "<p class=\"text-center\">添加网关异常！</p>";
            $("div#slice_alert_info").append(str);
            $('#editSliceModal').modal('show');
            return false;
        }
    }
}

//获取被用户选择的server
function fetch_gateway_ip(slice_name){
    var ret = false;
    $.ajax({
        url : "/plugins/vt/get_slice_gateway_ip/" + slice_name + "/",
        type : "GET",
        contentType: "application/json; charset=utf-8",
        dataType : "json",
        async: false,
        success : function(gw_ips){
            document.getElementById("gateway_ip").value = gw_ips["ipaddr"];
            ret = true;
        }
    });
    return ret;
}

//获取被用户选择的server
function fetch_gw_select_server(slice_id){
    check_url = "http://" + window.location.host + "/slice/get_select_server/"+slice_id+"/";
    //alert(check_url)
    var ret = false;
    $.ajax({
        type: "GET",
        url: check_url,
        dataType: "json",
        cache: false,
        async: false,  
        success: function(data) {
                servers = data;
                content = '<option value="" selected="selected">---------</option>';
                for(var i=0; i < servers.length; i++)
                {
                    content = content + '<option value="' + servers[i].id;
                    content = content +  '">';
                    content = content + servers[i].name;
                    content = content + '</option>';
                }
                var obj = $("#id_server_gw")[0];
                obj.innerHTML = "" + content;
                ret = true;
        }
    });
    return ret;  
}

//验证是否选择了gw的server
function check_gw_select(){
    var info = document.getElementById('gwInfo');
    if($('#id_server_gw').get(0).selectedIndex == 0){
        $(".gw_ip").addClass("has-error");
        showInfo(info," * 该项为必填项","red");
        return false;
    }else{
        info.innerHTML = '';
        $(".gw_ip").removeClass("has-error");
        return true;
    }
}
