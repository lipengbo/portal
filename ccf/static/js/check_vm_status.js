//入口,定期获取slice中虚拟机状态
var check_time_id;

$(document).ready(function() {
	//alert("here");
	update_vm_status();
});

function update_vm_status(){
    if(check_time_id){
        clearTimeout(check_time_id);
    }
    var check_vm_ids_obj = document.getElementsByName("check_vm_ids");
    if(check_vm_ids_obj){
       for(var i=0;i<check_vm_ids_obj.length;i++){
           if(check_vm_ids_obj[i].checked){
               slice_id = $("#slice_id").text();
               check_time_id = setTimeout("check_vm_status("+slice_id+")",5000);
           }
       }
    }
}

function check_vm_status(slice_id){
	//alert(3);
	check_url = "http://" + window.location.host + "/plugins/vt/get_vms_state/"+slice_id+"/";
	var check_vm_ids_obj = document.getElementsByName("check_vm_ids");
	var check = false;
	var status;
	var cur_vm_id;
	var str;
	var check_nodes = [];
	var admin = $("#admin").text();
	//alert(check_url)
    $.ajax({
        type: "GET",
        url: check_url,
        dataType: "json",
        cache: false,
        async: false,  
        success: function(data) {
        	vms = data.vms;
        	status = 8;
        	if(vms){
        	    //alert('check_vm_ids_obj.length');
        	    //alert(check_vm_ids_obj.length);
	        	for(var i=0;i<check_vm_ids_obj.length;i++){
	        	    //alert(i);
					if(check_vm_ids_obj[i].checked){
					    //alert('checked id');
					    //alert(i)
						cur_vm_id = check_vm_ids_obj[i].value;
						for(var j=0;j<vms.length;j++){
							if(vms[j].id == cur_vm_id){
								status = vms[j].state;
								break;
							}
						}
						//alert('status');
						//alert(status);
						if(status!=8){
						    var check_node = {};
						    check_node.status = status;
						    check_node.cur_vm_id = cur_vm_id;
						    check_nodes.push(check_node);
                        }
                        else{
                            check = true;
                        }
					}
					//alert(i);
			    } 
			    if(admin == 1){
			     for(var k=0;k<check_nodes.length;k++){
                        status = check_nodes[k].status;
                        cur_vm_id = check_nodes[k].cur_vm_id;
                        if(status == 9){
                            c_id = $("span#controller_fc").children(".aa").attr('value');
                            if(c_id && c_id == cur_vm_id){
                                $("div#controller_st").empty();
                                str = "";
                                str = str + "<i class=\"icon-remove\"></i>";
                                $("div#controller_st").append(str);
                                
                                $("span#controller_fc").empty();
                                str = "";
                                str = str + "<button type=\"button\" onclick=\"\" class=\"btn\" disabled>监控</button>";
                                $("span#controller_fc").append(str);
                            }
                            
                            $("div#gw_st"+cur_vm_id).empty();
                            str = "";
                            str = str + "<i class=\"icon-remove\"></i>";
                            $("div#gw_st"+cur_vm_id).append(str);
                            
                            $("span#gw_fc"+cur_vm_id).empty();
                            str = "";
                            str = str + "<button type=\"button\" onclick=\"\" class=\"btn\" disabled>监控</button>";
                            $("span#gw_fc"+cur_vm_id).append(str);
                            
                            $("div#dhcp_st"+cur_vm_id).empty();
                            str = "";
                            str = str + "<i class=\"icon-remove\"></i>";
                            $("div#dhcp_st"+cur_vm_id).append(str);
                            
                            $("span#dhcp_fc"+cur_vm_id).empty();
                            str = "";
                            str = str + "<button type=\"button\" onclick=\"\" class=\"btn\" disabled>监控</button>";
                            $("span#dhcp_fc"+cur_vm_id).append(str);
                            
                            $("div#vm_st"+cur_vm_id).empty();
                            str = "";
                            str = str + "<i class=\"icon-remove\"></i>";
                            $("div#vm_st"+cur_vm_id).append(str);
                            
                            $("span#vm_fc"+cur_vm_id).empty();
                            str = "";
                            str = str + "<button type=\"button\" onclick=\"\" class=\"btn\" disabled>监控</button>";
                            $("span#vm_fc"+cur_vm_id).append(str);
                        }else if(status == 1){
                            c_id = $("span#controller_fc").children(".aa").attr('value');
                            if(c_id && c_id == cur_vm_id){
                            $("div#controller_st").empty();
                                str = "";
                                str = str + "<i class=\"icon-ok-sign\"></i>";
                                $("div#controller_st").append(str);
                                
                                $("span#controller_fc").empty();
                                str = "";
                                str = str +  "<button type=\"button\" onclick=\"document.location='/monitor/vm/"+cur_vm_id+"/'\" class=\"btn\">监控</button>";
                                $("span#controller_fc").append(str);
                            }
                            
                            $("div#gw_st"+cur_vm_id).empty();
                            str = "";
                            str = str + "<i class=\"icon-ok-sign\"></i>";
                            $("div#gw_st"+cur_vm_id).append(str);
                            
                            $("span#gw_fc"+cur_vm_id).empty();
                            str = "";
                            str = str +  "<button type=\"button\" onclick=\"document.location='/monitor/vm/"+cur_vm_id+"/'\" class=\"btn\">监控</button>";
                            $("span#gw_fc"+cur_vm_id).append(str);
                            
                            $("div#dhcp_st"+cur_vm_id).empty();
                            str = "";
                            str = str + "<i class=\"icon-ok-sign\"></i>";
                            $("div#dhcp_st"+cur_vm_id).append(str);
                            
                            $("span#dhcp_fc"+cur_vm_id).empty();
                            str = "";
                            str = str +  "<button type=\"button\" onclick=\"document.location='/monitor/vm/"+cur_vm_id+"/'\" class=\"btn\">监控</button>";
                            $("span#dhcp_fc"+cur_vm_id).append(str);
                            
                            $("div#vm_st"+cur_vm_id).empty();
                            str = "";
                            str = str + "<i class=\"icon-ok-sign\"></i>";
                            $("div#vm_st"+cur_vm_id).append(str);
                            
                            $("span#vm_fc"+cur_vm_id).empty();
                            str = "";
                            str = str + "<button type=\"button\" onclick=\"document.location='/monitor/vm/"+cur_vm_id+"/'\" class=\"btn\">监控</button>";
                            $("span#vm_fc"+cur_vm_id).append(str);
                        }else{
                            c_id = $("span#controller_fc").children(".aa").attr('value');
                            if(c_id && c_id == cur_vm_id){
                                $("div#controller_st").empty();
                                str = "";
                                str = str + "<i class=\"icon-minus-sign\"></i>";
                                $("div#controller_st").append(str);
                                
                                $("span#controller_fc").empty();
                                str = "";
                                str = str + "<button type=\"button\" onclick=\"document.location='/monitor/vm/"+cur_vm_id+"/'\" class=\"btn\">监控</button>";
                                $("span#controller_fc").append(str);
                            }
                            
                            $("div#gw_st"+cur_vm_id).empty();
                            str = "";
                            str = str + "<i class=\"icon-minus-sign\"></i>";
                            $("div#gw_st"+cur_vm_id).append(str);
                            
                            $("span#gw_fc"+cur_vm_id).empty();
                            str = "";
                            str = str + "<button type=\"button\" onclick=\"document.location='/monitor/vm/"+cur_vm_id+"/'\" class=\"btn\">监控</button>";
                            $("span#gw_fc"+cur_vm_id).append(str);
                            
                            $("div#dhcp_st"+cur_vm_id).empty();
                            str = "";
                            str = str + "<i class=\"icon-minus-sign\"></i>";
                            $("div#dhcp_st"+cur_vm_id).append(str);
                            
                            $("span#dhcp_fc"+cur_vm_id).empty();
                            str = "";
                            str = str + "<button type=\"button\" onclick=\"document.location='/monitor/vm/"+cur_vm_id+"/'\" class=\"btn\">监控</button>";
                            $("span#dhcp_fc"+cur_vm_id).append(str);
                            
                            $("div#vm_st"+cur_vm_id).empty();
                            str = "";
                            str = str + "<i class=\"icon-minus-sign\"></i>";
                            $("div#vm_st"+cur_vm_id).append(str);
                            
                            $("span#vm_fc"+cur_vm_id).empty();
                            str = "";
                            str = str + "<button type=\"button\" onclick=\"document.location='/monitor/vm/"+cur_vm_id+"/'\" class=\"btn\">监控</button>";
                            $("span#vm_fc"+cur_vm_id).append(str);
                        }//endif
                    }//endfor
			        
			    }else{
			    
    			    for(var k=0;k<check_nodes.length;k++){
                        status = check_nodes[k].status;
                        cur_vm_id = check_nodes[k].cur_vm_id;
                        if(status == 9){
                            c_id = $("span#controller_fc").children(".aa").attr('value');
                            if(c_id && c_id == cur_vm_id){
                                $("div#controller_st").empty();
                                str = "";
                                str = str + "<i class=\"icon-remove\"></i>";
                                $("div#controller_st").append(str);
                                
                                $("span#controller_fc").empty();
                                str = "";
                                str = str + "<button type=\"button\" onclick=\"\" class=\"btn btn-success start_btn\" disabled>启动</button>"
                                    +"<button type=\"button\" onclick=\"\" class=\"btn\" disabled>登录</button>";
                                $("span#controller_fc").append(str);
                            }
                            
                            $("div#gw_st"+cur_vm_id).empty();
                            str = "";
                            str = str + "<i class=\"icon-remove\"></i>";
                            $("div#gw_st"+cur_vm_id).append(str);
                            
                            $("span#gw_fc"+cur_vm_id).empty();
                            str = "";
                            str = str + "<button type=\"button\" onclick=\"\" class=\"btn btn-success start_btn\" disabled>启动</button>"
                                +"<button type=\"button\" onclick=\"\" class=\"btn\" disabled>登录</button>";
                            $("span#gw_fc"+cur_vm_id).append(str);
                            
                            $("div#dhcp_st"+cur_vm_id).empty();
                            str = "";
                            str = str + "<i class=\"icon-remove\"></i>";
                            $("div#dhcp_st"+cur_vm_id).append(str);
                            
                            $("span#dhcp_fc"+cur_vm_id).empty();
                            str = "";
                            str = str + "<button type=\"button\" onclick=\"\" class=\"btn btn-success start_btn\" disabled>启动</button>"
                                +"<button type=\"button\" onclick=\"\" class=\"btn\" disabled>登录</button>";
                            $("span#dhcp_fc"+cur_vm_id).append(str);
                            
                            $("div#vm_st"+cur_vm_id).empty();
                            str = "";
                            str = str + "<i class=\"icon-remove\"></i>";
                            $("div#vm_st"+cur_vm_id).append(str);
                            
                            $("span#vm_fc"+cur_vm_id).empty();
                            str = "";
                            str = str + "<button type=\"button\" onclick=\"\" class=\"btn btn-success start_btn\" disabled>启动</button>"
                                +"<button type=\"button\" onclick=\"\" class=\"btn\" disabled>登录</button>";
                            $("span#vm_fc"+cur_vm_id).append(str);
                        }else if(status == 1){
                            c_id = $("span#controller_fc").children(".aa").attr('value');
                            if(c_id && c_id == cur_vm_id){
                                $("div#controller_st").empty();
                                str = "";
                                str = str + "<i class=\"icon-ok-sign icon_state\" id=\"icon_state"+cur_vm_id+"\"></i>";
                                $("div#controller_st").append(str);
                                
                                $("span#controller_fc").empty();
                                str = "";
                                str = str +  "<button type=\"button\" vm_id=\""+cur_vm_id+"\" class=\"btn btn-danger start_vm\">停止</button>"
                                    + "<button type=\"button\" url=\"/plugins/vt/vm/vnc/"+cur_vm_id+"\" class=\"btn btn_vnc\" id=\"btn_vnc"+cur_vm_id+"\">登录</button>";
                                $("span#controller_fc").append(str);
                            }
                            
                            $("div#gw_st"+cur_vm_id).empty();
                            str = "";
                            str = str + "<i class=\"icon-ok-sign gw_dhcp_icon\"></i>";
                            $("div#gw_st"+cur_vm_id).append(str);
                            
                            $("span#gw_fc"+cur_vm_id).empty();
                            str = "";
                            str = str +  "<button type=\"button\" vm_id=\""+cur_vm_id+"\" class=\"btn btn-danger start_gw_dhcp\">停止</button>"
                                + "<button type=\"button\" url=\"/plugins/vt/vm/vnc/"+cur_vm_id+"\" class=\"btn btn_vnc gw_dhcp_vnc\">登录</button>";
                            $("span#gw_fc"+cur_vm_id).append(str);
                            
                            $("div#dhcp_st"+cur_vm_id).empty();
                            str = "";
                            str = str + "<i class=\"icon-ok-sign gw_dhcp_icon\"></i>";
                            $("div#dhcp_st"+cur_vm_id).append(str);
                            
                            $("span#dhcp_fc"+cur_vm_id).empty();
                            str = "";
                            str = str +  "<button type=\"button\" vm_id=\""+cur_vm_id+"\" class=\"btn btn-danger start_gw_dhcp\">停止</button>"
                                + "<button type=\"button\" url=\"/plugins/vt/vm/vnc/"+cur_vm_id+"\" class=\"btn btn_vnc gw_dhcp_vnc\">登录</button>";
                            $("span#dhcp_fc"+cur_vm_id).append(str);
                            
                            $("div#vm_st"+cur_vm_id).empty();
                            str = "";
                            str = str + "<i class=\"icon-ok-sign icon_state\"  id=\"icon_state"+cur_vm_id+"\"></i>";
                            $("div#vm_st"+cur_vm_id).append(str);
                            
                            $("span#vm_fc"+cur_vm_id).empty();
                            str = "";
                            str = str + "<button type=\"button\" vm_id=\""+cur_vm_id+"\" class=\"btn btn-danger start_vm\">停止</button>"
                                + "<button type=\"button\" url=\"/plugins/vt/vm/vnc/"+cur_vm_id+"\" class=\"btn btn_vnc\" id=\"btn_vnc"+cur_vm_id+"\">登录</button>";
                            $("span#vm_fc"+cur_vm_id).append(str);
                        }else{
                            c_id = $("span#controller_fc").children(".aa").attr('value');
                            if(c_id && c_id == cur_vm_id){
                                $("div#controller_st").empty();
                                str = "";
                                str = str + "<i class=\"icon-minus-sign icon_state\" id=\"icon_state"+cur_vm_id+"\"></i>";
                                $("div#controller_st").append(str);
                                
                                $("span#controller_fc").empty();
                                str = "";
                                str = str + "<button type=\"button\" vm_id=\""+cur_vm_id+"\" class=\"btn btn-success start_vm\">启动</button>"
                                    + "<button type=\"button\" url=\"/plugins/vt/vm/vnc/"+cur_vm_id+"\" class=\"btn btn_vnc disabled\" id=\"btn_vnc"+cur_vm_id+"\">登录</button>";
                                $("span#controller_fc").append(str);
                            }
                            
                            $("div#gw_st"+cur_vm_id).empty();
                            str = "";
                            str = str + "<i class=\"icon-minus-sign gw_dhcp_icon\"></i>";
                            $("div#gw_st"+cur_vm_id).append(str);
                            
                            $("span#gw_fc"+cur_vm_id).empty();
                            str = "";
                            str = str + "<button type=\"button\" vm_id=\""+cur_vm_id+"\" class=\"btn btn-success start_gw_dhcp\">启动</button>"
                                + "<button type=\"button\" url=\"/plugins/vt/vm/vnc/"+cur_vm_id+"\" class=\"btn btn_vnc gw_dhcp_vnc disabled\">登录</button>";
                            $("span#gw_fc"+cur_vm_id).append(str);
                            
                            $("div#dhcp_st"+cur_vm_id).empty();
                            str = "";
                            str = str + "<i class=\"icon-minus-sign gw_dhcp_icon\"></i>";
                            $("div#dhcp_st"+cur_vm_id).append(str);
                            
                            $("span#dhcp_fc"+cur_vm_id).empty();
                            str = "";
                            str = str + "<button type=\"button\" vm_id=\""+cur_vm_id+"\" class=\"btn btn-success start_gw_dhcp\">启动</button>"
                                + "<button type=\"button\" url=\"/plugins/vt/vm/vnc/"+cur_vm_id+"\" class=\"btn btn_vnc gw_dhcp_vnc disabled\">登录</button>";
                            $("span#dhcp_fc"+cur_vm_id).append(str);
                            
                            $("div#vm_st"+cur_vm_id).empty();
                            str = "";
                            str = str + "<i class=\"icon-minus-sign icon_state\" id=\"icon_state"+cur_vm_id+"\"></i>";
                            $("div#vm_st"+cur_vm_id).append(str);
                            
                            $("span#vm_fc"+cur_vm_id).empty();
                            str = "";
                            str = str + "<button type=\"button\" vm_id=\""+cur_vm_id+"\" class=\"btn btn-success start_vm\">启动</button>"
                                + "<button type=\"button\" url=\"/plugins/vt/vm/vnc/"+cur_vm_id+"\" class=\"btn btn_vnc disabled\" id=\"btn_vnc"+cur_vm_id+"\">登录</button>";
                            $("span#vm_fc"+cur_vm_id).append(str);
                        }//endif
                    }//endfor
                }//endif
                    
			}    
        	if (check){
                check_time_id = setTimeout("check_vm_status("+slice_id+")",5000);
            } 
        }
    });
}
