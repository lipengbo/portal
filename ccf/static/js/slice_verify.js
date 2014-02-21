//验证slice名称是否是字母数字下划线
function check_slice_name(obj_id,flag){
	//alert("in check_slice_form");
	var obj = document.getElementById(obj_id);
	var info = document.getElementById(obj_id+"Info"); 
	var user_id_obj = document.getElementById("user_id");
	var len;
	//var reg = /^([u4e00-u9fa5]|[ufe30-uffa0]|[a-zA-Z_])*$/;
	//var reg = /^[a-zA-Z_]\w*$/;
	var reg = /^[a-zA-Z0-9_\u4e00-\u9fa5]+$/;
	//alert(user_id_obj.value.length);
	if(obj.value.replace(/(^\s*)|(\s*$)/g, "").length > 0){
        //if(!reg.test(obj.value)){
        	//alert("in 输入");
        	//showInfo(info," * 请输入中英文数字下划线的组合","red");
        	//return false;
        //}
       // else{
        	//alert("in green");
        	//alert(slice_exist);
        	isslice_exist(obj.value +"_"+user_id_obj.value);
        	if(slice_exist){
        		showInfo(info," * 该虚网已经存在","red");
        		return false;
        	}
        	else{
        		showInfo(info," ","green");
        		return true;
        	}
       // }
	}
	else{
		showInfo(info," * 必填","red");
		return false;
	}	
}
//验证slice描述信息
function check_slice_description(obj_id,flag){
	var obj = document.getElementById(obj_id);
	var info = document.getElementById(obj_id+"Info"); 
	var text = obj.value;
	if(text.replace(/(^\s*)|(\s*$)/g, "").length == 0){
	    showInfo(info," * 必填","red");
        return false;
	}
	else{
		showInfo(info," ","green");
        return true;
	}
}
//验证节点的选择
function check_island_id(obj_id){
	var obj = document.getElementById(obj_id);
	var info = document.getElementById(obj_id+"Info"); 
	var island_id = obj.options[obj.selectedIndex].value;
	if(obj.value == "no"){
		showInfo(info," * 必选","red");
		return false;
	}
	else{
		showInfo(info," ","green");
		return true;
	}
}
//验证控制器的选择
function check_slice_controller(obj_name){
	var objs = document.getElementsByName(obj_name);
	for(var i=0;i<objs.length;i++){  
		if(objs[i].checked){  
			if(objs[i].value=="default_create"){  
				return true; 
			}  
			if(objs[i].value=="user_define"){
				cip0_obj = document.getElementById("cip0");
				cip1_obj = document.getElementById("cip1");
				cip2_obj = document.getElementById("cip2");
				cip3_obj = document.getElementById("cip3");
				controller_ip = ''+cip0_obj.value+'.'+cip1_obj.value+'.'+cip2_obj.value+'.'+cip3_obj.value;
				//controller_ip_port = controller_ip_port_obj.value.split(":")
				var info = document.getElementById("controller_ip_portInfo");
				//if(controller_ip_port.length != 2){
				//	showInfo(info," * 格式错误(ip:port)","red");
				//	return false;
				//}
				//else{
				ret1 = check_ip(controller_ip,1);
				if(!ret1){
					return false;
				}
				else{
					ret2 = check_port('port',1);
					if (ret2){
						return true;
					}
					else{
						return false;
					}
				}
				//}
	  		}  
		}   
	}
}

//验证IP地址格式
function check_ip(ip,flag){
	var info = document.getElementById("controller_ip_portInfo");
	var reg=/^(\d+)\.(\d+)\.(\d+)\.(\d+)$/;//正则表达式

	if(ip.length > 0){
		//alert(ip);
		if(reg.test(ip)){
			if( RegExp.$1<256 && RegExp.$2<256 && RegExp.$3<256 && RegExp.$4<256){
				showInfo(info," ","green")
				return true;
			}
		}
		
		showInfo(info," * ip格式错误","red");	
		return false;
	}
	else{
		if(flag){
			showInfo(info," * ip格式错误","red");
			return false;
		}
		else{
			return true;
		}
	}	
}

//校验端口值
function check_port(port,flag){
	var info = document.getElementById("controller_ip_portInfo");
	if(port == 'port'){
	   var controller_port = document.getElementById("controller_port");
	   port = controller_port.value;
	}
	var reg = /^[0-9]*$/;
	if(port.length > 0){
		if(port >= 65535 || port < 0 || !reg.test(port)){
			showInfo(info," * port在(0-65535)之间","red");
			return false;
		}
		else{
			showInfo(info," ","green");
			return true;
		}	
	}
	else{
		if(flag){
			showInfo(info," * 不能为空","red");
			return false;
		}
		else{
			return true;
		}
	}
}

//校验网段分配
function check_nw_num(){
    var nw_num_obj = document.getElementById("nw_num");
    var nw_num = nw_num_obj.options[nw_num_obj.selectedIndex].value;
    var old_nw_num_obj = document.getElementById("old_nw_num");
    var old_nw_num = old_nw_num_obj.value;
    var old_slice_nw_obj = document.getElementById("old_slice_nw");
    var old_slice_nw = old_slice_nw_obj.value;
    var slice_uuid_obj = document.getElementById("slice_uuid");
    var slice_uuid = slice_uuid_obj.value;
    

    var slice_name_obj = document.getElementById("slice_name");
    var old_nw_owner_obj = document.getElementById("old_nw_owner");
    var slice_nw_obj = document.getElementById("slice_nw");
    var slice_nw_input_obj = document.getElementById("slice_nw_input");
    
    var user_id_obj = document.getElementById("user_id");
    var slice_name = slice_name_obj.value + "_" + user_id_obj.value;
    var old_nw_owner = old_nw_owner_obj.value;
    
    
    var info = document.getElementById("nw_numInfo");
    
    var ajax_ret = false;
    
    if(nw_num!=old_nw_num){
        if(old_slice_nw==''){
            check_url = "http://" + window.location.host + "/slice/create_nw/0/"+nw_num+"/";
        }
        else{
            check_url = "http://" + window.location.host + "/slice/create_nw/"+slice_uuid+"/"+nw_num+"/";
        }
        $.ajax({
            type: "GET",
            url: check_url,
            dataType: "json",
            cache: false,
            async: false,  
            success: function(data) {
                //alert(data.value);
                if (data.value == 0 || data.value == 1){
                    //alert(1);
                    showInfo(info," * 分配网段失败！","red");
                    ajax_ret = false;
                }
                else{
                    //alert(3);
                    slice_nw_obj.innerHTML = data.value;
                    slice_nw_input_obj.value = data.value;
                    old_slice_nw_obj.value = data.value;
                    setTimeout("nw_timeout()",1750000);
                    
                    slice_uuid_obj.value = data.owner
                    old_nw_owner_obj.value = slice_name;
                    old_nw_num_obj.value = nw_num;
                    showInfo(info," ","green");
                    //alert(5);
                    ajax_ret = true;
                }
            },
            error: function(data) {
                showInfo(info," * 分配网段失败！","red");
                ajax_ret = false;
            }
        });
        if(ajax_ret){
            return true;
        }
        else{
            return false;
        }
    }
    else{
        //alert(4);
        showInfo(info," ","green");
        return true;
    }
}


function check_nw_num1(){
	var slice_name_obj = document.getElementById("slice_name");
	var old_nw_owner_obj = document.getElementById("old_nw_owner");
	var nw_num_obj = document.getElementById("nw_num");
	var old_nw_num_obj = document.getElementById("old_nw_num");
	var slice_nw_obj = document.getElementById("slice_nw");
	var old_slice_nw_obj = document.getElementById("old_slice_nw");
	var user_id_obj = document.getElementById("user_id");
	var slice_name = slice_name_obj.value + "_" + user_id_obj.value;
	var old_nw_owner = old_nw_owner_obj.value;
	var nw_num = nw_num_obj.options[nw_num_obj.selectedIndex].value;
	var old_nw_num = old_nw_num_obj.value;
	var old_slice_nw = old_slice_nw_obj.value;
	var info = document.getElementById("nw_numInfo");
	
	var ajax_ret = false;
	
	if((slice_name!=old_nw_owner) || (nw_num!=old_nw_num)){
		if(old_slice_nw==''){
			check_url = "http://" + window.location.host + "/slice/create_nw/"+slice_name+"/"+nw_num+"/";
		}
		else{
			if(nw_num!=old_nw_num){
				check_url = "http://" + window.location.host + "/slice/create_nw/"+slice_name+"/"+nw_num+"/";
			}
			else{
				check_url = "http://" + window.location.host + "/slice/create_nw/"+slice_name+"/"+nw_num+"/";
			}
		}
	    $.ajax({
	        type: "GET",
	        url: check_url,
	        dataType: "json",
	        cache: false,
	        async: false,  
	        success: function(data) {
	        	//alert(data.value);
	        	if (data.value == 0){
	        		//alert(1);
	        		showInfo(info," * 分配网段失败！(改虚网名称)","red");
	        		ajax_ret = false;
	            }
	            else{
	            	if (data.value != 1){
	            		//alert(3);
	        			slice_nw_obj.innerHTML = data.value;
		             	old_slice_nw_obj.value = data.value;
		             	setTimeout("nw_timeout()",1750000);
	            	}
	            	old_nw_owner_obj.value = slice_name;
	    			old_nw_num_obj.value = nw_num;
	    			showInfo(info," ","green");
	    			//alert(5);
	    			ajax_ret = true;
	            }
	        },
	        error: function(data) {
	        	showInfo(info," * 分配网段失败！(改虚网名称)","red");
	    		ajax_ret = false;
	        }
	    });
	    if(ajax_ret){
	    	return true;
	    }
	    else{
	    	return false;
	    }
	}
	else{
		//alert(4);
		showInfo(info," ","green");
		return true;
	}
}

//网段过期
function nw_timeout(){
	$("div#slice_alert_info").empty();
    var str = "" + "<p class=\"text-center\">" + "分配的网段已过期！" + "</p>";
    $("div#slice_alert_info").append(str);
    $('#slicealertModal').modal('show');
	//alert("分配的网段已过期！");
	//window.top.location.reload();
}

//验证交换机端口的选择
function check_switch_port(){
	var switch_port_ids_obj = document.getElementsByName("switch_port_ids");
	var info = document.getElementById("switch_portInfo");
	for(var i=0;i<switch_port_ids_obj.length;i++){
		if(!switch_port_ids_obj[i].disabled){
			//alert(switch_port_ids_obj[i].value);
			switch_port_id = switch_port_ids_obj[i].value;
			switchtype_obj = document.getElementById("switchtype"+switch_port_id);
			if(switchtype_obj.value == 3){
				showInfo(info,"","green");
				return true;
			}
		}
    }
    showInfo(info," * 必选一台虚拟机关联节点！","red");
	return false;
}

var slice_exist;
//校验所填的slice是否存在
function isslice_exist(slicename){
	//alert (slicename)
	check_url = "http://" + window.location.host + "/slice/check_slice_name/?slice_name="+slicename;
	//alert(check_url)
    $.ajax({
        type: "GET",
        url: check_url,
        dataType: "json",
        cache: false,
        async: false,  
        success: function(data) {
        	if (data.value == 1)
             {
                //alert("in true")
                slice_exist = true;
             } 
             else
             {
              	//alert("in false");
                slice_exist = false;
             }
        }
    });
}


//显示信息
function showInfo(_info,msg,color){
    var info=_info;
    info.innerHTML = msg;
    info.style.color=color;
}


//验证网关ip
function check_gw_ip(flag){
    var gw_ip_obj = document.getElementById("gw_ip");
    var info = document.getElementById("gw_ipInfo");
    var old_slice_nw_obj = document.getElementById("old_slice_nw");
    
    var reg=/^((25[0-5])|(2[0-4]\d)|(1\d\d)|([1-9]\d)|\d)(\.((25[0-5])|(2[0-4]\d)|(1\d\d)|([1-9]\d)|\d)){3}?$/;//正则表达式
    
    if(obj.value.length > 0){
        if(reg.test(obj.value))
        {
            slice_nw = old_slice_nw_obj.value;
            gw_ip = gw_ip_obj.value;  
            slice_ip_mask=slice_nw.split("/");
            ip = slice_ip_mask[0];
            mask = slice_ip_mask[1];
            ips = ip.split(".");
            masks = maskint_to_maskstr(mask);
            cur_ips = nw_ip.split(".");
            if(((ips[0]&masks[0]) == (cur_ips[0]&masks[0]))&&((ips[1]&masks[1]) == (cur_ips[1]&masks[1]))&&((ips[2]&masks[2]) == (cur_ips[2]&masks[2]))&&((ips[3]&masks[3]) == (cur_ips[3]&masks[3]))){
                showInfo(info," ","green");
                return true;
            }
        }
        showInfo(info,"IP地址错误","red")   ;   
        return false;
    }
    else{
        if(flag){
            showInfo(info,"请填写IP地址","blue");
            return false;
        }
        return true;
    } 
}

//验证dhcp的ip段
function check_dhcp_ip(flag){
    var src_obj = document.getElementById("dhcp_src_ip");
    var des_obj = document.getElementById("dhcp_des_ip");
    var old_slice_nw_obj = document.getElementById("old_slice_nw");
    
    var reg=/^((25[0-5])|(2[0-4]\d)|(1\d\d)|([1-9]\d)|\d)(\.((25[0-5])|(2[0-4]\d)|(1\d\d)|([1-9]\d)|\d)){3}?$/;//正则表达式
    
     if(src_obj.value.length > 0 && des_obj.value.length > 0){
        if(reg.test(src_obj.value) && reg.test(des_obj.value))
        {
            slice_nw = old_slice_nw_obj.value;
            src_ip = src_obj.value;  
            slice_ip_mask=slice_nw.split("/");
            ip = slice_ip_mask[0];
            mask = slice_ip_mask[1];
            ips = ip.split(".");
            masks = maskint_to_maskstr(mask);
            cur_ips = src_ip.split(".");
            if(((ips[0]&masks[0]) == (cur_ips[0]&masks[0]))&&((ips[1]&masks[1]) == (cur_ips[1]&masks[1]))&&((ips[2]&masks[2]) == (cur_ips[2]&masks[2]))&&((ips[3]&masks[3]) == (cur_ips[3]&masks[3]))){
                des_ip = des_obj.value; 
                cur_ips = des_ip.split(".");
                if(((ips[0]&masks[0]) == (cur_ips[0]&masks[0]))&&((ips[1]&masks[1]) == (cur_ips[1]&masks[1]))&&((ips[2]&masks[2]) == (cur_ips[2]&masks[2]))&&((ips[3]&masks[3]) == (cur_ips[3]&masks[3]))){
                    showInfo(info," ","green");
                    return true;
                }
            }
        }
        showInfo(info,"IP地址错误","red");   
        return false;
    }
    else{
        if(flag){
            showInfo(info,"请填写IP地址","blue");
            return false;
        }
        return true;
    } 
    
}


function maskint_to_maskstr(mask){
    masks = new Array(255, 255, 255, 255);
    if(0<=mask && mask<=8){
        masks = new Array(trans(mask), 0, 0, 0);
    }
    if(9<=mask && mask<=16){
        masks = new Array(255, trans(mask-8), 0, 0);
    }
    if(17<=mask && mask<=24){
        masks = new Array(255, 255, trans(mask-16), 0);
    }
    if(25<=mask && mask<=32){
        masks = new Array(255, 255, 255, trans(mask-24));
    }   
    return masks ;
}

function trans(mask){
    if(mask==0){
        return 0;
    }
    if(mask==1){
        return 128;
    }
    if(mask==2){
        return 192;
    }
    if(mask==3){
        return 224;
    }
    if(mask==4){
        return 240;
    }
    if(mask==5){
        return 248;
    }
    if(mask==6){
        return 252;
    }
    if(mask==7){
        return 254;
    }
    if(mask==8){
        return 255;
    }
}

function start_or_stop(slice_id, flag){
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
                //alert("failed");
                $("div#slice_alert_info").empty();
                var str = "" + "<p class=\"text-center\">" + data.error_info + "</p>";
                $("div#slice_alert_info").append(str);
                $('#slicealertModal').modal('show');
             }
        }
    });
    return ret;
}

//slice启动停止按钮
   $(".start_slice").click(function(){
        var slice_id = $("#slice_id").text();
        if($(this).hasClass("btn-success")){
            ret = start_or_stop(slice_id, 1);
            if(ret){
                $(this).removeClass("btn-success").addClass("btn-danger");           
                $(this).text("停止虚网");
                $(".label").removeClass("label-important").addClass("label-success");
                $(".icon-2x").removeClass("icon-minus-sign").addClass("icon-ok-sign");
                $(".btn-slice-state").addClass("disabled");
                $(".slice_state_del").addClass("disabled");
				$(".start_dhcp").attr("disabled", "true");
            }     
        } else {
            ret = start_or_stop(slice_id, 2);
            if(ret){
                $(this).removeClass("btn-danger").addClass("btn-success");
                $(this).text("启动虚网");
                $(".label").removeClass("label-success").addClass("label-important");
                $(".icon-2x").removeClass("icon-ok-sign").addClass("icon-minus-sign");
                $(".btn-slice-state").removeClass("disabled");
                $(".slice_state_del").removeClass("disabled");
				$(".start_dhcp").removeAttr("disabled");
            }         
        }
    }); 

     $(".btn-slice-state").click(function(){
        if($(this).hasClass("disabled")){
            return false;
        } else {
            return true;
        }
     }); 
 
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
 
 
 //虚拟机启动停止按钮
   $(".start_vm").live("click", function(){
        if($(this).hasClass("disabled")){
            return false;
        }else{
            //alert("he");
            vm_id = $(this).attr('vm_id');
            //alert(vm_id);
            if($(this).hasClass("btn-success")){
                ret = start_or_stop_vm(vm_id, "create");
                if(ret){
                    $(this).removeClass("btn-success").addClass("btn-danger");           
                    $(this).text("停止");
                    $("#btn_vnc"+vm_id).removeClass("disabled");
                    $("#icon_state"+vm_id).removeClass("icon-minus-sign").addClass("icon-ok-sign");
                    document.getElementById('topologyiframe').contentWindow.topology_update_vm_state(vm_id, 1);
                    
                }     
            } else {
                ret = start_or_stop_vm(vm_id, "destroy");
                if(ret){
                    $(this).removeClass("btn-danger").addClass("btn-success");
                    $(this).text("启动");
                    $("#btn_vnc"+vm_id).addClass("disabled");
                    //$(this).parent("td").prev("td").children(".icon_state").removeClass("icon-ok-sign").addClass("icon-minus-sign");
                    $("#icon_state"+vm_id).removeClass("icon-ok-sign").addClass("icon-minus-sign");
                    document.getElementById('topologyiframe').contentWindow.topology_update_vm_state(vm_id, 5);
                }         
            }
        }
    });
  
   $(".start_gw_dhcp").live("click", function(){
        if($(this).hasClass("disabled")){
            return false;
        }else{
            vm_id = $(this).attr('vm_id');
            //alert(vm_id);
            if($(this).hasClass("btn-success")){
                ret = start_or_stop_vm(vm_id, "create");
                if(ret){
                    $(".start_gw_dhcp").removeClass("btn-success").addClass("btn-danger");           
                    $(".start_gw_dhcp").text("停止");
                    $(".gw_dhcp_vnc").removeClass("disabled");
                    $(".gw_dhcp_icon").removeClass("icon-minus-sign").addClass("icon-ok-sign");
                }     
            } else {
                ret = start_or_stop_vm(vm_id, "destroy");
                if(ret){
                    $(".start_gw_dhcp").removeClass("btn-danger").addClass("btn-success");
                    $(".start_gw_dhcp").text("启动");
                    $(".gw_dhcp_vnc").addClass("disabled");
                    $(".gw_dhcp_icon").removeClass("icon-ok-sign").addClass("icon-minus-sign");
                }         
            }
        }
    });
   
   $(".btn_vnc").live("click", function(){
        if($(this).hasClass("disabled")){
            return false;
        } else {
            url = $(this).attr('url');
            open_vnc(url);
        }
     }); 
 
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
                //alert("failed");
                $("div#slice_alert_info").empty();
                var str = "" + "<p class=\"text-center\">" + data.error_info + "</p>";
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

    $(".slice_state_del").click(function(){
        if($(this).hasClass("disabled")){
            return false;
        }else{
            $('#alertModal').modal();
            var self = $(this);
            $('.delete-confirm').unbind('click');
            $('.delete-confirm').click(function(){
                vm_id = self.attr('vm_id');
                //alert(vm_id);
                ret = delete_vm(vm_id);
                if(ret){
                    $("#vm_tr"+vm_id).hide();
                    document.getElementById('topologyiframe').contentWindow.topology_del_vm(vm_id);
                    slice_id = $("#slice_id").text();
                    //document.getElementById("topologyiframe").src="/slice/topology_d3/?slice_id="+slice_id+"&width=800&height=300&top=1";
                }
            });
            return false;
        }
    });
 
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
                        description_old.innerHTML = "描述："+obj.value;
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
 
  //编辑slice控制器
 function edit_controller(slice_id){
    var ret;
    ret = check_slice_controller('controller_type');
    var STATIC_URL = $("#STATIC_URL").text();
    if(ret){
        var controller_type_objs = document.getElementsByName("controller_type");
        var controller_sys_obj = document.getElementById("controller_sys");
        //var controller_ip_port_obj = document.getElementById("controller_ip_port");
        var controller_type;
        for(var i=0;i<controller_type_objs.length;i++){  
            if(controller_type_objs[i].checked){  
                if(controller_type_objs[i].value=="default_create"){  
                    controller_type = "default_create";
                }  
                if(controller_type_objs[i].value=="user_define"){
                    controller_type = "user_define";
                }  
            }   
        }
        cip0_obj = document.getElementById("cip0");
        cip1_obj = document.getElementById("cip1");
        cip2_obj = document.getElementById("cip2");
        cip3_obj = document.getElementById("cip3");
        controller_ip = ''+cip0_obj.value+'.'+cip1_obj.value+'.'+cip2_obj.value+'.'+cip3_obj.value;
        controller_port_obj = document.getElementById("controller_port");
        //var controller_ip_port = controller_ip_port_obj.value.split(":");
        var submit_data = {"controller_type": controller_type,
                        "controller_sys": controller_sys_obj.value,
                        "controller_ip": controller_ip,
                        "controller_port": controller_port_obj.value};
        check_url = "http://" + window.location.host + "/slice/edit_controller/"+slice_id+"/";
        $.ajax({
                type: "POST",
                url: check_url,
                dataType: "json",
                data: submit_data,
                async: false, 
                success: function(data) {
                    if (data.result == 1 || data.result == 2){
                        //alert("ok");
                        controller = data.controller;
                        //alert(controller);
                        $("div#controller_nm").empty();
                        if(controller.name == 'user_define'){
                            str = "" + "自定义控制器";
                        }else{
                            str = "" + controller.name;
                        }
                        $("div#controller_nm").append(str);
                        $("div#controller_pp").empty();
                        str = "" + controller.ip + ":" + controller.port;
                        $("div#controller_pp").append(str);

                        if(data.result == 1){
                            //alert(controller.host_uuid);
                            $("div#controller_uuid").empty();
                            str = "" + "<a id=\"uuid\" href=\"javascript:void(0);\" data-toggle=\"tooltip\" data-placement=\"bottom\" title=\"\" data-original-title=\""+controller.host_uuid+"\">";
                            str = str + controller.host_uuid.split("-")[0] + "..." + "</a>";
                            $("div#controller_uuid").append(str);
                            $("div#controller_sp").empty();
                            str = "" + controller.server_ip;
                            $("div#controller_sp").append(str);
                            $("div#controller_st").empty();
                            if(controller.host_state == 8){
                                str = "" + "<img src=\""+STATIC_URL+"img/loader.gif\"/>";
                            }else if(controller.host_state == 9){
                                str = "" + "<i class=\"icon-remove\"></i>";
                            }else if(controller.host_state == 1){
                                str = "" + "<i class=\"icon-ok-sign icon_state\" id=\"icon_state"+controller.host_id+"\"></i>";
                            }else{
                                str = "" + "<i class=\"icon-minus-sign icon_state\" id=\"icon_state"+controller.host_id+"\"></i>";
                            }
                            $("div#controller_st").append(str);
                            $("span#controller_fc").empty();
                            if(controller.host_state == 8){
                                str = "" + "<input class=\"aa\" type=\"checkbox\" name=\"check_vm_ids\" value=\""+controller.host_id+"\" checked style=\"display:none\"/>"
                                +"<button type=\"button\" class=\"btn btn-success disabled start_vm\">启动</button>"
                                +"<button type=\"button\" class=\"btn  btn_vnc disabled\" id=\"btn_vnc"+controller.host_id+"\">登录</button> ";
                            }else if(controller.host_state == 9){
                                str = "" + "<button type=\"button\" class=\"btn btn-success disabled start_vm\">启动</button>"
                                +"<button type=\"button\" class=\"btn btn_vnc disabled\" id=\"btn_vnc"+controller.host_id+"\">登录</button>";
                            }else if(controller.host_state == 1){
                                str = "" + "<button type=\"button\" vm_id=\""+controller.host_id+"\" class=\"btn btn-danger start_vm\">停止</button>"                                         
                                +"<button type=\"button\" url=\"/plugins/vt/vm/vnc/"+controller.host+id+"\" class=\"btn btn_vnc\" id=\"btn_vnc"+controller.host_id+"\">登录</button>";
                            }else{
                                str = "" + "<button type=\"button\" vm_id=\""+controller.host.id+"\" class=\"btn btn-success start_vm\">启动</button>"
                                +"<button type=\"button\" url=\"/plugins/vt/vm/vnc/"+controller.host.id+"\" class=\"btn btn_vnc disabled\" id=\"btn_vnc"+controller.host_id+"\">登录</button>";
                            }
                            $("span#controller_fc").append(str);
                            if(controller.host_state == 8){
                                update_vm_status();
                            }
                        }else{
                            $("div#controller_uuid").empty();
                            $("div#controller_sp").empty();
                            $("div#controller_st").empty();
                            $("span#controller_fc").empty();
                        }
                        //var description_old = document.getElementById('slice_description_old');
                        //description_old.innerHTML = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"+obj.value;
                    }
                    else{
                        //alert(failed);
                        $("div#slice_alert_info").empty();
                        str = "" + "<p class=\"text-center\">"+data.error_info+"</p>";
                        $("div#slice_alert_info").append(str);
                        $('#slicealertModal').modal('show');
                    }
                },
                error: function(data) {
                    $("div#slice_alert_info").empty();
                    str = "" + "<p class=\"text-center\">编辑失败！</p>";
                    $("div#slice_alert_info").append(str);
                    $('#slicealertModal').modal('show');
                }
        });
        $('#editSliceModal').modal('hide');
    }
 }
function set_dhcp(slice_id, flag){
	$.ajax({
			url: '/slice/dhcp_switch/'+slice_id+"/"+flag+"/",
			type: 'GET',
			dataType: "json",
			success: function(data){
				if(data.result == 0){
					if(flag == 1){
						$('.start_dhcp').removeClass("btn-success").addClass("btn-danger");           
                		$('.start_dhcp').text("停止DHCP服务");
					}else{
						$('.start_dhcp').removeClass("btn-danger").addClass("btn-success");
                		$('.start_dhcp').text("启动DHCP服务");
					}
					
				}else{
					$("div#slice_alert_info").empty();
                    str = "" + "<p class=\"text-center\">设置网关服务失败！</p>";
                    $("div#slice_alert_info").append(str);
                    $('#slicealertModal').modal('show');
				}
			}
		});
}

$('.start_dhcp').click(function(){
        var slice_id = $("#slice_id").text();
        if($(this).hasClass("btn-success")){
            set_dhcp(slice_id, 1);
        } else {
            set_dhcp(slice_id, 0);
        }
    }); 
