//入口,定期获取slice中虚拟机状态
var check_vm_time_id;
var check_slice_time_id;

$(document).ready(function() {
	//alert("here");
	update_vm_status();
	update_slice_status();
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
                    if(status!=8){
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
                    vm_obj = $("#icon_state"+check_nodes[j].cur_vm_id);
                    if(vm_obj){
                        status = check_nodes[j].status;
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
                            a_obj = $("#"+check_nodes[j].cur_vm_id+"_qt")[0];
                            img_obj = $("#"+check_nodes[j].cur_vm_id+"_qt").children("img")[0];
							if(img_obj.title == "停止"){
								$("div#slice_alert_info").empty();
                            	var str = "" + "<p class=\"text-center\">虚拟机停止失败！</p>";
                            	$("div#slice_alert_info").append(str);
                            	$('#slicealertModal').modal('show');
							}
                            if(a_obj){
                            	a_obj.style.cursor = "pointer";
							}
                            if(img_obj){
                            	img_obj.src = STATIC_URL + "img/btn_tz.png";       
                            	img_obj.title = "停止";
							}
                            //虚拟机登录按钮
                            a_obj = $("#"+check_nodes[j].cur_vm_id+"_dl")[0];
                            img_obj = $("#"+check_nodes[j].cur_vm_id+"_dl").children("img")[0];
                            if(a_obj){
                            a_obj.style.cursor = "pointer";}
                            if(img_obj){
                            img_obj.src = STATIC_URL + "img/btn_dl.png"; }
                            //虚拟机监控按钮
                            a_obj = $("#"+check_nodes[j].cur_vm_id+"_jk")[0];
                            img_obj = $("#"+check_nodes[j].cur_vm_id+"_jk").children("img")[0];
                            if(a_obj){
                            a_obj.style.cursor = "pointer";}
                            if(img_obj){
                            img_obj.src = STATIC_URL + "img/btn_jk.png"; } 
							document.getElementById('topologyiframe').contentWindow.topology_update_vm_state(check_nodes[j].cur_vm_id, 1);   
                        }else{
							vm_obj.removeClass("icon-spinner")
                                .removeClass("icon-spin")
                                .removeClass("check_vm")
                                .addClass("icon-minus-sign")
                                .addClass("icon_state"); 
                            a_obj = $("#"+check_nodes[j].cur_vm_id+"_qt")[0];
                            img_obj = $("#"+check_nodes[j].cur_vm_id+"_qt").children("img")[0];
							if(img_obj.title == "启动"){
								$("div#slice_alert_info").empty();
                            	var str = "" + "<p class=\"text-center\">虚拟机启动失败！</p>";
                            	$("div#slice_alert_info").append(str);
                            	$('#slicealertModal').modal('show');
							}
                            if(a_obj){
                            a_obj.style.cursor = "pointer";}
                            if(img_obj){
                            img_obj.src = STATIC_URL + "img/btn_qd.png";       
                            img_obj.title = "启动"; }
							document.getElementById('topologyiframe').contentWindow.topology_update_vm_state(check_nodes[j].cur_vm_id, 5);
                        }
                    }
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
                        img_obj.src = STATIC_URL + "img/btn_qd.png";
                        if(img_obj.title == "启动中"){
                            $("div#slice_alert_info").empty();
                            var str = "" + "<p class=\"text-center\">虚网启动失败！</p>";
                            $("div#slice_alert_info").append(str);
                            $('#slicealertModal').modal('show');
                        }    
                        img_obj.title = "启动"; }
                        //控制器编辑、slice编辑按钮变化
                        $(".bianji").attr("style","cursor:pointer");
                        $(".bianji").children("img").attr("src",STATIC_URL+"img/btn_bj.png");
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
                        img_obj.src = STATIC_URL + "img/btn_tz.png";
                        if(img_obj.title == "停止中"){
                            $("div#slice_alert_info").empty();
                            var str = "" + "<p class=\"text-center\">虚网停止失败！</p>";
                            $("div#slice_alert_info").append(str);
                            $('#slicealertModal').modal('show');
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
