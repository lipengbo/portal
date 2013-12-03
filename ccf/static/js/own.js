$(document).ready(function() {
	//help页面滑动到顶部效果
	$(".bs-docs-sidenav li a").click(function() {
		var navHeight = $(".navbar").height();
		$("html, body").animate({
			scrollTop: $($(this).attr("href")).offset().top - navHeight + "px"
			}, {
			duration: 500,
			easing: "swing"
		});
		$(".bs-docs-sidenav li").removeClass();
		$(this).parent("li").addClass("active");
		return false;
	});
	
	//虚拟机创建页面，添加和删除按钮功能
	$(".add").click(function(){
		$(".sec_block").first().clone().appendTo(".vm_info_list");		
        var spans_info = $(".sec_block").last().find("span");
        for (var i=0; i<spans_info.length; i++){
            spans_info[i].innerHTML = '';
        } 
		$(".sec_block").last().find("input[type='text']").val("");
		$(".sec_block").last().find("input[type='checkbox']").next().remove();
		$(".sec_block").last().find("input[type='checkbox']").unwrap('icheckbox_square-blue');
		//$(".sec_block").last().find("input[type='checkbox']").attr("checked","true");
		$(".sec_block").last().find("input[type='checkbox']").iCheck({
            checkboxClass: 'icheckbox_square-blue',
            radioClass: 'iradio_square-blue',
            increaseArea: '20%' // optional
        });
		$(".sec_block").last().find(".del").css("visibility","visible");
		$(".sec_block:odd").css("background","#f5f5f5");
		$(".del").click(function(){
           $(this).parent(".operate_btn").parent(".span5").parent(".vm_well_wrap").parent(".sec_block").remove();
           $(".sec_block").css("background","#ffffff");
           $(".sec_block:odd").css("background","#f5f5f5");
        });                          
	});

/*	$(".del").click(function(){
       $(this).parent(".operate_btn").parent(".sec_block").remove();
       $(".sec_block").css("background","#dff0d8");
       $(".sec_block:odd").css("background","#d9edf7");
    });*/
    
    //创建slice第3步，选择控制器配置方式
    $(".tab_radio1, .tab_radio1 .iCheck-helper").click(function(){
        $(".tab_radio2").parent("td").siblings("td").children("#ipInput").css({"background":"#eee"}).addClass("disabled");        
        $(".tab_radio1").parent("td").siblings("td").children("select").removeAttr("disabled");
        $(".tab_radio2").parent("td").siblings("td").children("#ipInput").children("input").attr("disabled","disabled");
        $(".tab_radio2").parent("td").siblings("td").children("input").attr("disabled","disabled");
        $("#controller_ip_portInfo").html("");
    });
    $(".tab_radio2, .tab_radio2 .iCheck-helper").click(function(){
        $(".tab_radio2").parent("td").siblings("td").children("#ipInput").css({"background":"#fff"}).removeClass("disabled");        
        $(".tab_radio2").parent("td").siblings("td").children("#ipInput").children("input").removeAttr("disabled");
        $(".tab_radio2").parent("td").siblings("td").children("input").removeAttr("disabled");
        $(".tab_radio1").parent("td").siblings("td").children("select").attr("disabled","disabled");
    });
    $(".tab_radio3, .tab_radio3 .iCheck-helper").click(function(){
        $(".tab_radio3").parent("td").parent("tr").siblings("tr").children("td").children("input").attr("disabled","disabled");
    });
    $(".tab_radio4, .tab_radio4 .iCheck-helper").click(function(){
        $(".tab_radio4").parent("td").siblings("td").children("input").removeAttr("disabled");
    });
    
    //slice详情启动停止按钮
/*    $(".start_btn").click(function(){
        if($(this).hasClass("btn-success")){
            $(this).removeClass("btn-success").addClass("btn-danger");
            if($(this).hasClass("btn-large")){            
                $(this).text("停止Slice");
            } else {              
                $(this).text("停止");
            }           
        } else {
            $(this).removeClass("btn-danger").addClass("btn-success");
            if($(this).hasClass("btn-large")){
                $(this).text("启动Slice");
            } else {
                $(this).text("启动");
            }           
        }
    });      */
    
    // show topology
    $('.btn-step1').click(function () {
        var island_id = $('select[name="island_id"]').val();
        $('#topology-iframe').attr('src', '/topology/?size=big&no_parent=true&show_virtual_switch=true&hide_filter=true&island_id=' + island_id);
        selected_ports = {};
        $('.switch-table tbody tr').hide();
        $('.switch-table tbody tr label').hide();
    });

    $('.btn-step4').click(function () {
        $('.switch-manifest tbody').html('');
        $.each($('.switch-table tbody tr'), function (index, tr) {
            var clone = $(tr).clone();
            $('.switch-manifest tbody').append(clone);
        });
        $('.switch-manifest tbody input').attr('disabled', '');
    });
    //slice步骤切换
    $(".tab_part:not(:first)").hide();
    $(".next_btn").click(function(){


        $('.no-virtual-switch').hide();
        if ($(this).hasClass('btn-step2')) {
            var has_virtual_switch = false;
            for(dpid in window.selected_dpids) {
                if (dpid.indexOf('00:ff:') == 0) {
                    has_virtual_switch = true;
                }
            }
            if (!has_virtual_switch) {
                $('.no-virtual-switch').show();
                return false;
            }
        }

       $("html, body").scrollTop(0);
       var thisIndex = $(".next_btn").index(this);
       var nowIndex = thisIndex + 1;
       if(thisIndex == 0){
           ret = page_function0();
           if (!ret){
           		return;
           }
       }
       if(thisIndex == 1){
       	   ret = page_function1();
       	   if (!ret){
           		return;
           }
       }
       if(thisIndex == 2){
           ret = page_function2();
           if (!ret){
           		return;
           }
       }
       if(thisIndex == 3){
           ret = page_function3();
           if (!ret){
           		return;
           }
       }
       if(thisIndex == 4){
           ret = page_function4();
           if (!ret){
           		nowIndex = 0;
           }
    	   else{
				return;
    	   }
       }
       $(".tab_part").hide();
       $(".tab_part").eq(nowIndex).show();
       $(".nav-pills .span2").eq(thisIndex).children(".step").children(".desc").removeClass("active");
       if(nowIndex == 0){
       		$(".nav-pills .span2").removeClass("visit");
       }
       $(".nav-pills .span2").eq(nowIndex).addClass("visit");
       $(".nav-pills .span2").eq(nowIndex).children(".step").children(".desc").addClass("active");
    });
    $(".prev_btn").click(function(){
       $("html, body").scrollTop(0);
       var thisIndex = $(".prev_btn").index(this) + 1;
       var nowIndex = thisIndex - 1;
       //alert(vm_info_flag);
       $(".tab_part").hide();
       $(".tab_part").eq(nowIndex).show();
       $(".nav-pills .span2").eq(thisIndex).removeClass("visit");
       $(".nav-pills .span2").eq(thisIndex).children(".step").children(".desc").removeClass("active");
       $(".nav-pills .span2").eq(nowIndex).addClass("visit");
       $(".nav-pills .span2").eq(nowIndex).children(".step").children(".desc").addClass("active");
    });
    
    //通过复选框控制表单显示和隐藏
    $(".tab_checkbox").click(function(){
        if($(this).children(".icheckbox_square-blue").hasClass("checked")){
             $(".hide_form").slideDown();                                
        } else {
             $(".hide_form").slideUp(); 
        }
    });
    $(".tab_checkbox .iCheck-helper").click(function(){
        if($(this).parent(".icheckbox_square-blue").hasClass("checked")){
             $(".hide_form").slideDown();                                
        } else {
             $(".hide_form").slideUp(); 
        }
    });
    
    //输入框兼选择框
    $(".select_input ul li a").click(function(){
        var selectText = $(this).text();
        $(".select_input input").val(selectText);
    }); 
    
   //全选全不选
    $(".checkall .iCheck-helper").click(function(){
       if($(this).parent(".icheckbox_square-blue").hasClass("checked")){
           $(".icheckbox_square-blue:not(.disabled)").iCheck('check');
       } else {
           $(".icheckbox_square-blue").iCheck('uncheck');
       }
    });
    
    $(".checkboxs .iCheck-helper").each(function(){
        $(this).click(function(){
            if($(".checkboxs .checked").length<$(".checkboxs .iCheck-helper").length){
                $(".checkall .icheckbox_square-blue").iCheck('uncheck');
            } else if($(".checkboxs .checked").length==$(".checkboxs .iCheck-helper").length) {
                $(".checkall .icheckbox_square-blue").iCheck('check');
            }
        });
    });
    
    //tooltip demo
     $('.tooltip-demo').tooltip({
       selector: "a[data-toggle=tooltip]"
     });
     
     //slice_list slice文字说明显示与隐藏
    /* $(".slice_topology").mouseenter(function(){
         $(this).find(".slice_text").stop().animate({bottom:"0"});
     }).mouseleave(function(){
         $(this).find(".slice_text").stop().animate({bottom:"-67px"});
     });*/
     
     //管理员首页轮播
     $('#myCarousel').carousel();          
     
    // 基础设施页面按钮点击效果
    $(".device_link").mouseup(function(){
        $(this).addClass("active");
    });
	
	//创建虚拟机时显示拓扑
	$("#show_topo").on("click", function(){
		show_topology();
	})
});


//全选全不选
/*function check_all(obj,cName){
    var checkboxs = document.getElementsByName(cName);
    for(var i=0;i<checkboxs.length;i++){checkboxs[i].checked = obj.checked;}
}*/

//slice创建页面js
function page_function0(){
	ret1 = check_slice_name('slice_name',2);
	ret2 = check_slice_description('slice_description',2);
	ret3 = check_island_id('island_id')
	if (ret1 && ret2 && ret3){
		return true;
	}
	else{
		return false;
	}
}
function page_function1(){
	
	//ret1 = check_switch_port();
	var ret2 = check_nw_num();
	//alert(ret1);
	//alert(ret2);
	if (ret2){
		
		var slice_name_obj = document.getElementById("slice_name");
    	var user_id_obj = document.getElementById("user_id");
		var slice_name = slice_name_obj.value + "_" + user_id_obj.value;
    	fetch_serverinfo("id_server_gw");
    	fetch_gw_ip(slice_name);

		if(check_ovs_gw()){
			$('#gw_setting').show();
		}else{
			$('#gw_setting').hide();
		}
		return true;
	}
	else{
		return false;
	}
}
function page_function2(){
    fetch_serverinfo("id_server");
	$('#topologyiframe').attr("src", "/slice/topology_d3/?slice_id=0&width=620&height=300&top=0&switch_port_ids=" + get_select_ports())
	ret1 = check_slice_controller('controller_type');
	if(!document.getElementById('dhcp_selected').checked){
		$('#dhcp').hide();
		document.getElementById('id_enable_dhcp').checked = false;
	}else{
		$('#dhcp').show();
	}
	if (ret1){
		//
		return true;
	}
	else{
		return false;
	}
}
function page_function3(){
	//网段
	var slice_nw = document.getElementById("slice_nw");
	var list_slice_nw = document.getElementById("list_slice_nw");
	list_slice_nw.innerHTML = slice_nw.innerHTML;
	//DHCP
	var dhcp_selected_obj = document.getElementById("dhcp_selected");
	var list_slice_dhcp = document.getElementById("list_slice_dhcp");
	if(dhcp_selected_obj.checked){
       list_slice_dhcp.innerHTML = "已配置";
    }else{
       list_slice_dhcp.innerHTML = "未配置";
    }
	//控制器
	var controller_type_obj = document.getElementsByName("controller_type");
	$("div#list_controller").empty();
	for(var i=0;i<controller_type_obj.length;i++){  
		if(controller_type_obj[i].checked){  
			if(controller_type_obj[i].value=="default_create"){  
				var controller_sys_obj = document.getElementById("controller_sys");
				var controller_sys = controller_sys_obj.options[controller_sys_obj.selectedIndex].value;
				var str = "";
				str = str + "<table class=\"table\">"
			        + "<tbody>"
			        + "<tr>"
			        + "<td width=\"100\">创建方式：</td>"
			        + "<td>默认创建</td>"
			        + "</tr>"
			        + "<tr>"
			        + "<td width=\"100\">控制器类型：</td>"
			        + "<td>" + controller_sys + "</td>"
			        + "</tr>"                     
			        + "</tbody>"
			        + "</table>";  
			}  
			if(controller_type_obj[i].value=="user_define"){
			    cip0_obj = document.getElementById("cip0");
                cip1_obj = document.getElementById("cip1");
                cip2_obj = document.getElementById("cip2");
                cip3_obj = document.getElementById("cip3");
                //controller_ip = ''+cip0_obj.value+'.'+cip1_obj.value+'.'+cip2_obj.value+'.'+cip3_obj.value;
                controller_port_obj = document.getElementById("controller_port");
				//var controller_ip_port_obj = document.getElementById("controller_ip_port");
				var controller_ip_port = ''+cip0_obj.value+'.'+cip1_obj.value+'.'+cip2_obj.value+'.'+cip3_obj.value+':'+controller_port_obj.value;
				var str = "";
				str = str + "<table class=\"table\">"
			        + "<tbody>"
			        + "<tr>"
			        + "<td width=\"100\">创建方式：</td>"
			        + "<td>自定义</td>"
			        + "</tr>"
			        + "<tr>"
			        + "<td width=\"100\">控制器IP端口：</td>"
			        + "<td>" + controller_ip_port + "</td>"
			        + "</tr>"                     
			        + "</tbody>"
			        + "</table>";        
	  		}  
		}   
	}
	$("div#list_controller").append(str); 
	//网关
	var id_server_gw_obj = document.getElementById("id_server_gw");
    var gateway_ip_obj = document.getElementById("gateway_ip");
    var id_server_gw_index;
    if(id_server_gw_obj){
        id_server_gw_index = id_server_gw_obj.selectedIndex;
    }
	$("div#list_gw").empty();
    var str = "";
    if(id_server_gw_obj && gateway_ip_obj && id_server_gw_obj.value && gateway_ip_obj.value){  
        
        str = str + "<table class=\"table\">"
                + "<tbody><tr>"
                        +"<td width=\"100\">网关宿主机：</td>"
                        +"<td>"+ id_server_gw_obj.options[id_server_gw_index].text +"</td></tr>"
                    +"<tr><td>网关IP地址：</td>"
                        +"<td>"+ gateway_ip_obj.value +"</td></tr>";
        
        //if(dhcp_selected_obj.checked){
        //   str = str + "<tr><td colspan=2>"
        //   +"已配置DHCP服务器</td></tr>";
           
       // }else{
       //    str = str + "<tr><td colspan=2>"
       //    +"未配置DHCP服务器</td></tr>";
       // }
        str = str + "</tbody></table>";  
    }else{
        str = str + "<table class=\"table\">"
                + "<tbody><tr>"
                        +"<td>未配置</td>"                 
        str = str + "</tr></tbody></table>"; 
    }  

    $("div#list_gw").append(str); 
    //$("#dhcp_show").iCheck({
    //        checkboxClass: 'icheckbox_square-blue',
    //        radioClass: 'iradio_square-blue',
    //        increaseArea: '20%' // optional
   // });
        //虚拟机
        fetch_vminfo();
        return check_vminfo()
}
function page_function4(){
	var project_id = $("#project_id").text();
	//alert(project_id);
	ret1 = submit_slice_info(project_id);
	if (ret1){
		return true;
	}
	else{
		return false;
	}
}


//提交slice信息创建slice
function submit_slice_info(project_id){
	//alert("here");
	var slice_name_obj = document.getElementById("slice_name");
	var slice_description_obj = document.getElementById("slice_description");
	var island_id_obj = document.getElementById("island_id");
	var controller_type_objs = document.getElementsByName("controller_type");
	var controller_sys_obj = document.getElementById("controller_sys");
	//var controller_ip_port_obj = document.getElementById("controller_ip_port");
	var switch_port_ids_obj = document.getElementsByName("switch_port_ids");
	var old_slice_nw_obj = document.getElementById("old_slice_nw");
	var id_server_gw_obj = document.getElementById("id_server_gw");
	var gateway_ip_obj = document.getElementById("gateway_ip");
	var dhcp_selected_obj = document.getElementById("dhcp_selected");
	var switch_port_ids = "";
	var controller_type;
	var dhcp_selected = 0;
	var j = 0;
	var cip0_obj = document.getElementById("cip0");
    var cip1_obj = document.getElementById("cip1");
    var cip2_obj = document.getElementById("cip2");
    var cip3_obj = document.getElementById("cip3");
    var controller_ip = ''+cip0_obj.value+'.'+cip1_obj.value+'.'+cip2_obj.value+'.'+cip3_obj.value;
    var controller_port_obj = document.getElementById("controller_port");
    for(var i=0;i<switch_port_ids_obj.length;i++){
		if(!switch_port_ids_obj[i].disabled){
			//alert(switch_port_ids_obj[i].value);
			if(j==0){
				switch_port_ids = switch_port_ids_obj[i].value;
			}
			else{
				switch_port_ids = switch_port_ids + "," + switch_port_ids_obj[i].value;
			}
			j++;
		}
    }      
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
    if(dhcp_selected_obj && dhcp_selected_obj.checked){ 
       // alert(1); 
        dhcp_selected = 1; 
    }   
	//var controller_ip_port = controller_ip_port_obj.value.split(":");
    var user_id_obj = document.getElementById("user_id");
    var id_server_gw_obj_value = 0;
    var gateway_ip_obj_value = '';
    if(id_server_gw_obj && gateway_ip_obj && id_server_gw_obj.value && gateway_ip_obj.value){
        id_server_gw_obj_value = id_server_gw_obj.value;
        gateway_ip_obj_value = gateway_ip_obj.value;
    }
	var submit_data = {"slice_name": slice_name_obj.value + "_" + user_id_obj.value,
						"slice_description": slice_description_obj.value,
						"island_id": island_id_obj.options[island_id_obj.selectedIndex].value,
						"controller_type": controller_type,
						"controller_sys": controller_sys_obj.value,
						"controller_ip": controller_ip,
						"controller_port": controller_port.value,
						"switch_port_ids": switch_port_ids,
						"slice_nw": old_slice_nw_obj.value,
						"gw_host_id": id_server_gw_obj_value,
						"gw_ip": gateway_ip_obj_value,
						"dhcp_selected": dhcp_selected
		};

	check_url = "http://" + window.location.host + "/slice/create_first/"+project_id+"/";
	var ajax_ret = true;
	$.ajax({
			type: "POST",
			url: check_url,
			dataType: "json",
			data: submit_data,
			async: false, 
			success: function(data) {
	        	if (data.result == 1){
	        		//alert(data.slice_id);
	        		submit_vms(data.slice_id);
	        		location.href = "http://" + window.location.host + "/slice/detail/"+data.slice_id+"/";
	            }
	            else{
	            	//alert(data.error_info);
	            	$("div#slice_alert_info").empty();
                    str = "" + "<p class=\"text-center\">" + data.error_info + "</p>";
                    $("div#slice_alert_info").append(str);
                    $('#slicealertModal').modal('show');
	            	ajax_ret = false;
	            }
	        },
	        error: function(data) {
	        	//alert("创建slice异常！");
	        	$("div#slice_alert_info").empty();
                str = "" + "<p class=\"text-center\">" + "创建slice异常！" + "</p>";
                $("div#slice_alert_info").append(str);
                $('#slicealertModal').modal('show');
	        }
	});
	if(ajax_ret){
    	return true;
    }
    else{
    	var old_slice_nw_obj = document.getElementById("old_slice_nw");
    	var old_nw_owner_obj = document.getElementById("old_nw_owner");
    	var old_nw_num_obj = document.getElementById("old_nw_num");
    	old_slice_nw_obj.value = "";
    	old_nw_owner_obj.value = "";
    	old_nw_num_obj.value = "";
    	return false;
    }
}
