//入口,定期获取slice中虚拟机状态
var check_vm_time_id;
var check_slice_time_id;
var check_vpn_time_id;

$(document).ready(function() {
	//alert("here");
	update_vm_status();
	update_slice_status();
    update_vpn_status();
});

//监控虚拟机状态
function update_vm_status(){
    if(check_vm_time_id){
        clearTimeout(check_vm_time_id);
    }
    var check_vm_id_objs = $(".check_vm");
    //alert(check_vm_id_objs.length);
    if(check_vm_id_objs.length > 0){
        slice_id = $("#slice_id").text();
        check_vm_time_id = setTimeout("check_vm_status("+slice_id+")",1000);
    }else{
        //check_vm_time_id = setTimeout("update_vm_status()",5000);
    }
}

//ajax监控虚拟机状态
function check_vm_status(slice_id){
    check_url = "http://" + window.location.host + "/plugins/vt/get_vms_state/"+slice_id+"/";
    var check_vm_id_objs = $(".check_vm");
    var check = false;
    var status;
    var cur_obj
    var cur_vm_id;
    var check_nodes = [];
    var cur_obj;
    var a_obj;
    var img_obj;
    var STATIC_URL = $("#STATIC_URL").text();
    //alert(check_url)
    $.ajax({
        type: "GET",
        url: check_url,
        dataType: "json",
        cache: false,
        async: true,  
        success: function(data) {
            vms = data.vms;
            if(vms){
                for(var i=0;i<check_vm_id_objs.length;i++){
                    status = 8;
                    cur_obj = check_vm_id_objs[i].id;
                    cur_vm_id = cur_obj.split("e")[1]
                    for(var j=0;j<vms.length;j++){
                        if(vms[j].id == cur_vm_id){
                            status = vms[j].state;
                            break;
                        }
                    }
                    if(status!=8 && status!=12 && status!=13){
                        var check_node = {};
                        check_node.status = status;
                        check_node.cur_vm_id = cur_vm_id;
                        if(status==9 || status==10){
                            check_node.switch_id = 0;
                            check_node.port = 0;
                            check_node.port_name = '';
                        }else{
                            check_node.switch_id = vms[j].switch_id;
                            check_node.port = vms[j].port; 
                            check_node.port_name = vms[j].port_name;
                        }
                        check_nodes.push(check_node);
                    }
                }
                for(var j=0;j<check_nodes.length;j++){
                    if(check_nodes[j].status == 1){
                        img_obj = $("#"+check_nodes[j].cur_vm_id+"_qt").children("img")[0];
                        if(img_obj && img_obj.title == "停止中"){
                            $("div#slice_alert_info").empty();
                            var str = "" + "<p class=\"text-center\">虚拟机停止失败！</p>";
                            $("div#slice_alert_info").append(str);
                            $('#slicealertModal').modal('show');
                        }
                    }
                    if(check_nodes[j].status == 5){
                        img_obj = $("#"+check_nodes[j].cur_vm_id+"_qt").children("img")[0];
                        if(img_obj && img_obj.title == "启动中"){
                            $("div#slice_alert_info").empty();
                            var str = "" + "<p class=\"text-center\">虚拟机启动失败！</p>";
                            $("div#slice_alert_info").append(str);
                            $('#slicealertModal').modal('show');
                        }
                    }
                    change_vm_status(check_nodes[j].cur_vm_id, check_nodes[j].status)
                }
                    //alert(i);
            }
            update_vm_status();   
        },
        error: function(data) {
            update_vm_status();
        }
    });
    
}


//更新vm状态
function change_vm_status(vm_id, status){
    var STATIC_URL = $("#STATIC_URL").text();
    vm_obj = $("#icon_state"+vm_id);
    if(vm_obj && vm_obj.hasClass("icon-spinner")){
        if(status == 9 || status == 10){
            vm_obj.removeClass("icon-spinner")
                .removeClass("icon-spin")
                .removeClass("check_vm")
                .addClass("icon-remove-sign");   
        }else if(status == 1){
            vm_obj.removeClass("icon-spinner")
                .removeClass("icon-spin")
                .removeClass("check_vm")
                .addClass("icon-ok-sign")
                .addClass("icon_state");
            //启停虚拟机按钮
            a_obj = $("#"+vm_id+"_qt")[0];
            img_obj = $("#"+vm_id+"_qt").children("img")[0];
            if(a_obj){
                a_obj.style.cursor = "pointer";
            }
            if(img_obj){
                img_obj.src = STATIC_URL + "img/ic-tz.png";       
                img_obj.title = "停止";
            }
            //虚拟机登录按钮
            a_obj = $("#"+vm_id+"_dl")[0];
            img_obj = $("#"+vm_id+"_dl").children("img")[0];
            if(a_obj){
            a_obj.style.cursor = "pointer";}
            if(img_obj){
            img_obj.src = STATIC_URL + "img/btn_dl.png"; }
            //虚拟机监控按钮
            a_obj = $("#"+vm_id+"_jk")[0];
            img_obj = $("#"+vm_id+"_jk").children("img")[0];
            if(a_obj){
                a_obj.style.cursor = "pointer";}
            if(img_obj){
                img_obj.src = STATIC_URL + "img/btn_jk.png"; } 
            document.getElementById('topologyiframe').contentWindow.topology_update_vm_state(vm_id, 1);   
        }else if(status == 5 || status == 0){
            vm_obj.removeClass("icon-spinner")
                .removeClass("icon-spin")
                .removeClass("check_vm")
                .addClass("icon-minus-sign")
                .addClass("icon_state"); 
            a_obj = $("#"+vm_id+"_qt")[0];
            img_obj = $("#"+vm_id+"_qt").children("img")[0];
            if(a_obj){
                a_obj.style.cursor = "pointer";}
            if(img_obj){
                img_obj.src = STATIC_URL + "img/ic-ks.png";       
                img_obj.title = "启动"; }
            document.getElementById('topologyiframe').contentWindow.topology_update_vm_state(vm_id, 5);
        }
    }
}


//监控虚网状态
function update_slice_status(){
    //alert("h1");
    if(check_slice_time_id){
        clearTimeout(check_slice_time_id);
    }
    var check_slice_objs = $("#slice_state");
    if(check_slice_objs.hasClass("icon-spin")){
        //alert("h2");
        slice_id = $("#slice_id").text();
        check_slice_time_id = setTimeout("check_slice_status("+slice_id+")",1000);
    }else{
    //alert("h3");
        //check_slice_time_id = setTimeout("update_slice_status()",1000);
    }
}


//ajax监控slice状态
function check_slice_status(slice_id){
    check_url = "http://" + window.location.host + "/slice/get_slice_state/"+slice_id+"/";
    var check = false;
    var status;
    var a_obj;
    var img_obj;
    var STATIC_URL = $("#STATIC_URL").text();
    //alert(check_url)
    $.ajax({
        type: "GET",
        url: check_url,
        dataType: "json",
        cache: false,
        async: true,  
        success: function(data) {
            //alert("h4");
            if(data.value == 0){
                //alert("h5");
                status = data.state;
                var check_slice_objs = $("#slice_state");
                //alert(status);
                if(status == 0){
                    check_slice_objs.removeClass("icon-spinner")
                        .removeClass("icon-spin")
                        .addClass("icon-minus-sign")
                        .addClass("icon_state")
                    //alert($("#edit").text());
                    if($("#edit").text() == 1){
                        //alert("h6");
                        a_obj = $("#slice_qt")[0]
                        img_obj = $("#slice_qt").children("img")[0]
                        if(a_obj){
                        a_obj.style.cursor = "pointer";}
                        if(img_obj){
                            img_obj.src = STATIC_URL + "img/ic-ks.png";
                            if(img_obj.title == "启动中"){
                                $("div#slice_alert_info").empty();
                                if(data.c_state != 1){
                                    var str = "" + "<p class=\"text-center\">虚网启动失败(控制器启动失败)！</p>";
                                }else if(data.g_state != 1){
                                    var str = "" + "<p class=\"text-center\">虚网启动失败(网关启动失败)！</p>";
                                }else{
                                    var str = "" + "<p class=\"text-center\">虚网启动失败！</p>";
                                }
                                
                                $("div#slice_alert_info").append(str);
                                $('#slicealertModal').modal('show');
                            }
                            if ($(".default_create").length > 0){
                                vm_id = $(".default_create")[0].getAttribute("vm_id");
                                change_vm_status(vm_id, data.c_state)
                            }
                            if ($(".gw").length > 0){
                                vm_id = $(".gw")[0].getAttribute("vm_id");
                                change_vm_status(vm_id, data.g_state)
                            } 
                            img_obj.title = "启动"; 
                        }
                        //控制器编辑、slice编辑按钮变化
                        $(".bianji").attr("style","cursor:pointer");
                        $(".bianji").children("img").attr("src",STATIC_URL+"img/btn_bj.png");
                        //vm删除、port删除
                        $(".shanchu").attr("style","cursor:pointer");
                        $(".shanchu").children("img").attr("src",STATIC_URL+"img/btn_sc.png");
                        //dhcp启停、vm添加
                        $(".dhcp_div").removeClass("disabled");
                        $(".dhcp").attr("style","cursor:pointer");
                        $("#vm_add").removeClass("disabled").attr("style","cursor:pointer");   
                    } 
                }else if(status == 1){
                    check_slice_objs.removeClass("icon-spinner")
                        .removeClass("icon-spin")
                        .addClass("icon-ok-sign")
                        .addClass("icon_state"); 
                    //alert($("#edit").text());
                    if($("#edit").text() == 1){
                        //alert("h7");
                        a_obj = $("#slice_qt")[0]
                        img_obj = $("#slice_qt").children("img")[0]
                        if(a_obj){
                        a_obj.style.cursor = "pointer";}
                        if(a_obj){
                        img_obj.src = STATIC_URL + "img/ic-tz.png";
                        if(img_obj.title == "停止中"){
                            $("div#slice_alert_info").empty();
                            var str = "" + "<p class=\"text-center\">虚网停止失败！</p>";
                            $("div#slice_alert_info").append(str);
                            $('#slicealertModal').modal('show');
                        }
                        if ($(".default_create").length > 0){
                            vm_id = $(".default_create")[0].getAttribute("vm_id");
                            change_vm_status(vm_id, data.c_state)
                        }
                        if ($(".gw").length > 0){
                            vm_id = $(".gw")[0].getAttribute("vm_id");
                            change_vm_status(vm_id, data.g_state)
                        }
                        img_obj.title = "停止";  }
                    }   
                }
            }
            update_slice_status();
        },
        error: function(data) {
            update_slice_status();
        }
    });
    
}

//监控VPN服务的状态
function update_vpn_status(){
    //alert("h1");
    if(check_vpn_time_id){
        clearTimeout(check_vpn_time_id);
    }
    var check_vpn_objs = $("#vpn_state");
    if(check_vpn_objs.hasClass("icon-spin")){
        //alert("h2");
        slice_id = $("#slice_id").text();
        check_vpn_time_id = setTimeout("check_vpn_status("+slice_id+")",1000);
    }else{
    }
}

function check_vpn_status(slice_id){
    var img_obj;
    $.ajax({
        type: "GET",
        url: "/slice/get_vpn_state/"+slice_id+"/",
        dataType: "json",
        cache: false,
        async: true,  
        success: function(data) {
            var state = data.vpn_state;
            var check_vpn_obj = $("#vpn_state");
            var STATIC_URL = $("#STATIC_URL").text();
            if(state == 0){
                check_vpn_obj.removeClass("icon-spinner")
                        .removeClass("icon-spin")
                        .addClass("icon-minus-sign")
                        .addClass("icon_state");
                img_obj = $("#vpn_qt").children("img")[0];
                $("#vpn_qt").attr("style", "cursor:pointer");
                if(img_obj){
                    img_obj.src = STATIC_URL + "img/ic-ks.png";
                            if(img_obj.title == "启动中"){
                                $("div#slice_alert_info").empty();
                                var str = "" + "<p class=\"text-center\">VPN服务启动失败！</p>";
                                
                                $("div#slice_alert_info").append(str);
                                $('#slicealertModal').modal('show');
                            }
                    img_obj.title = "启动";
                }
            }else if(state == 1){
                check_vpn_obj.removeClass("icon-spinner")
                        .removeClass("icon-spin")
                        .addClass("icon-ok-sign")
                        .addClass("icon_state");
                img_obj = $("#vpn_qt").children("img")[0];
                $("#vpn_qt").attr("style", "cursor:pointer");
                if(img_obj){
                    img_obj.src = STATIC_URL + "img/ic-tz.png";
                            if(img_obj.title == "停止中"){
                                $("div#slice_alert_info").empty();
                                var str = "" + "<p class=\"text-center\">VPN服务停止失败！</p>";
                                
                                $("div#slice_alert_info").append(str);
                                $('#slicealertModal').modal('show');
                            }
                    img_obj.title = "停止";
                }
            }
            update_vpn_status();
        },
        error: function(data) {
            update_vpn_status();
        }
        
    });
}

