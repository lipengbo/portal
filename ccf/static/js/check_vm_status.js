//入口,定期获取slice中虚拟机状态

$(document).ready(function() {
	//alert("here");
	check_vm = $("#check_vm").text();
	if(check_vm == 1){
		//alert(2);
		slice_id = $("#slice_id").text();
		setTimeout("check_vm_status("+slice_id+")",5000);
	}
});

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
        async: true,  
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
                            $("div#controller_st"+cur_vm_id).empty();
                            str = "";
                            str = str + "<i class=\"icon-remove-sign\"></i>";
                            $("div#controller_st"+cur_vm_id).append(str);
                            
                            $("span#controller_fc"+cur_vm_id).empty();
                            str = "";
                            str = str + "<button type=\"button\" onclick=\"\" class=\"btn\" disabled>监控</button>";
                            $("span#controller_fc"+cur_vm_id).append(str);
                            
                            $("div#gw_st"+cur_vm_id).empty();
                            str = "";
                            str = str + "<i class=\"icon-remove-sign\"></i>";
                            $("div#gw_st"+cur_vm_id).append(str);
                            
                            $("span#gw_fc"+cur_vm_id).empty();
                            str = "";
                            str = str + "<button type=\"button\" onclick=\"\" class=\"btn\" disabled>监控</button>";
                            $("span#gw_fc"+cur_vm_id).append(str);
                            
                            $("div#dhcp_st"+cur_vm_id).empty();
                            str = "";
                            str = str + "<i class=\"icon-remove-sign\"></i>";
                            $("div#dhcp_st"+cur_vm_id).append(str);
                            
                            $("span#dhcp_fc"+cur_vm_id).empty();
                            str = "";
                            str = str + "<button type=\"button\" onclick=\"\" class=\"btn\" disabled>监控</button>";
                            $("span#dhcp_fc"+cur_vm_id).append(str);
                            
                            $("div#vm_st"+cur_vm_id).empty();
                            str = "";
                            str = str + "<i class=\"icon-remove-sign\"></i>";
                            $("div#vm_st"+cur_vm_id).append(str);
                            
                            $("span#vm_fc"+cur_vm_id).empty();
                            str = "";
                            str = str + "<button type=\"button\" onclick=\"\" class=\"btn\" disabled>监控</button>";
                            $("span#vm_fc"+cur_vm_id).append(str);
                        }else if(status == 1){
                            $("div#controller_st"+cur_vm_id).empty();
                            str = "";
                            str = str + "<i class=\"icon-ok-sign\"></i>";
                            $("div#controller_st"+cur_vm_id).append(str);
                            
                            $("span#controller_fc"+cur_vm_id).empty();
                            str = "";
                            str = str +  "<button type=\"button\" onclick=\"document.location='/monitor/vm/"+cur_vm_id+"/'\" class=\"btn\">监控</button>";
                            $("span#controller_fc"+cur_vm_id).append(str);
                            
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
                            $("div#controller_st"+cur_vm_id).empty();
                            str = "";
                            str = str + "<i class=\"icon-minus-sign\"></i>";
                            $("div#controller_st"+cur_vm_id).append(str);
                            
                            $("span#controller_fc"+cur_vm_id).empty();
                            str = "";
                            str = str + "<button type=\"button\" onclick=\"document.location='/monitor/vm/"+cur_vm_id+"/'\" class=\"btn\">监控</button>";
                            $("span#controller_fc"+cur_vm_id).append(str);
                            
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
                            $("div#controller_st"+cur_vm_id).empty();
                            str = "";
                            str = str + "<i class=\"icon-remove-sign\"></i>";
                            $("div#controller_st"+cur_vm_id).append(str);
                            
                            $("span#controller_fc"+cur_vm_id).empty();
                            str = "";
                            str = str + "<button type=\"button\" onclick=\"\" class=\"btn btn-success start_btn\" disabled>启动</button>&nbsp;"
                                +"<button type=\"button\" onclick=\"\" class=\"btn\" disabled>登录</button>";
                            $("span#controller_fc"+cur_vm_id).append(str);
                            
                            $("div#gw_st"+cur_vm_id).empty();
                            str = "";
                            str = str + "<i class=\"icon-remove-sign\"></i>";
                            $("div#gw_st"+cur_vm_id).append(str);
                            
                            $("span#gw_fc"+cur_vm_id).empty();
                            str = "";
                            str = str + "<button type=\"button\" onclick=\"\" class=\"btn btn-success start_btn\" disabled>启动</button>&nbsp;"
                                +"<button type=\"button\" onclick=\"\" class=\"btn\" disabled>登录</button>";
                            $("span#gw_fc"+cur_vm_id).append(str);
                            
                            $("div#dhcp_st"+cur_vm_id).empty();
                            str = "";
                            str = str + "<i class=\"icon-remove-sign\"></i>";
                            $("div#dhcp_st"+cur_vm_id).append(str);
                            
                            $("span#dhcp_fc"+cur_vm_id).empty();
                            str = "";
                            str = str + "<button type=\"button\" onclick=\"\" class=\"btn btn-success start_btn\" disabled>启动</button>&nbsp;"
                                +"<button type=\"button\" onclick=\"\" class=\"btn\" disabled>登录</button>";
                            $("span#dhcp_fc"+cur_vm_id).append(str);
                            
                            $("div#vm_st"+cur_vm_id).empty();
                            str = "";
                            str = str + "<i class=\"icon-remove-sign\"></i>";
                            $("div#vm_st"+cur_vm_id).append(str);
                            
                            $("span#vm_fc"+cur_vm_id).empty();
                            str = "";
                            str = str + "<button type=\"button\" onclick=\"\" class=\"btn btn-success start_btn\" disabled>启动</button>&nbsp;"
                                +"<button type=\"button\" onclick=\"\" class=\"btn\" disabled>登录</button>";
                            $("span#vm_fc"+cur_vm_id).append(str);
                        }else if(status == 1){
                            $("div#controller_st"+cur_vm_id).empty();
                            str = "";
                            str = str + "<i class=\"icon-ok-sign\"></i>";
                            $("div#controller_st"+cur_vm_id).append(str);
                            
                            $("span#controller_fc"+cur_vm_id).empty();
                            str = "";
                            str = str +  "<button type=\"button\" onclick=\"do_vm_action('/plugins/vt/do/vm/action/"+cur_vm_id+"/destroy')\" class=\"btn btn-danger stop_btn\">停止</button>&nbsp;"
                                + "<button type=\"button\" onclick=\"open_vnc('/plugins/vt/vm/vnc/"+cur_vm_id+"')\" class=\"btn\">登录</button>";
                            $("span#controller_fc"+cur_vm_id).append(str);
                            
                            $("div#gw_st"+cur_vm_id).empty();
                            str = "";
                            str = str + "<i class=\"icon-ok-sign\"></i>";
                            $("div#gw_st"+cur_vm_id).append(str);
                            
                            $("span#gw_fc"+cur_vm_id).empty();
                            str = "";
                            str = str +  "<button type=\"button\" onclick=\"do_vm_action('/plugins/vt/do/vm/action/"+cur_vm_id+"/destroy')\" class=\"btn btn-danger stop_btn\">停止</button>&nbsp;"
                                + "<button type=\"button\" onclick=\"open_vnc('/plugins/vt/vm/vnc/"+cur_vm_id+"')\" class=\"btn\">登录</button>";
                            $("span#gw_fc"+cur_vm_id).append(str);
                            
                            $("div#dhcp_st"+cur_vm_id).empty();
                            str = "";
                            str = str + "<i class=\"icon-ok-sign\"></i>";
                            $("div#dhcp_st"+cur_vm_id).append(str);
                            
                            $("span#dhcp_fc"+cur_vm_id).empty();
                            str = "";
                            str = str +  "<button type=\"button\" onclick=\"do_vm_action('/plugins/vt/do/vm/action/"+cur_vm_id+"/destroy')\" class=\"btn btn-danger stop_btn\">停止</button>&nbsp;"
                                + "<button type=\"button\" onclick=\"open_vnc('/plugins/vt/vm/vnc/"+cur_vm_id+"')\" class=\"btn\">登录</button>";
                            $("span#dhcp_fc"+cur_vm_id).append(str);
                            
                            $("div#vm_st"+cur_vm_id).empty();
                            str = "";
                            str = str + "<i class=\"icon-ok-sign\"></i>";
                            $("div#vm_st"+cur_vm_id).append(str);
                            
                            $("span#vm_fc"+cur_vm_id).empty();
                            str = "";
                            str = str + "<button type=\"button\" onclick=\"do_vm_action('/plugins/vt/do/vm/action/"+cur_vm_id+"/destroy')\" class=\"btn btn-danger stop_btn\">停止</button>&nbsp;"
                                + "<button type=\"button\" onclick=\"open_vnc('/plugins/vt/vm/vnc/"+cur_vm_id+"')\" class=\"btn\">登录</button>";
                            $("span#vm_fc"+cur_vm_id).append(str);
                        }else{
                            $("div#controller_st"+cur_vm_id).empty();
                            str = "";
                            str = str + "<i class=\"icon-minus-sign\"></i>";
                            $("div#controller_st"+cur_vm_id).append(str);
                            
                            $("span#controller_fc"+cur_vm_id).empty();
                            str = "";
                            str = str + "<button type=\"button\" onclick=\"do_vm_action('/plugins/vt/do/vm/action/"+cur_vm_id+"/create')\" class=\"btn btn-success start_btn\">启动</button>&nbsp;"
                                + "<button type=\"button\" onclick=\"\" class=\"btn\" disabled>登录</button>";
                            $("span#controller_fc"+cur_vm_id).append(str);
                            
                            $("div#gw_st"+cur_vm_id).empty();
                            str = "";
                            str = str + "<i class=\"icon-minus-sign\"></i>";
                            $("div#gw_st"+cur_vm_id).append(str);
                            
                            $("span#gw_fc"+cur_vm_id).empty();
                            str = "";
                            str = str + "<button type=\"button\" onclick=\"do_vm_action('/plugins/vt/do/vm/action/"+cur_vm_id+"/create')\" class=\"btn btn-success start_btn\">启动</button>&nbsp;"
                                + "<button type=\"button\" onclick=\"\" class=\"btn\" disabled>登录</button>";
                            $("span#gw_fc"+cur_vm_id).append(str);
                            
                            $("div#dhcp_st"+cur_vm_id).empty();
                            str = "";
                            str = str + "<i class=\"icon-minus-sign\"></i>";
                            $("div#dhcp_st"+cur_vm_id).append(str);
                            
                            $("span#dhcp_fc"+cur_vm_id).empty();
                            str = "";
                            str = str + "<button type=\"button\" onclick=\"do_vm_action('/plugins/vt/do/vm/action/"+cur_vm_id+"/create')\" class=\"btn btn-success start_btn\">启动</button>&nbsp;"
                                + "<button type=\"button\" onclick=\"\" class=\"btn\" disabled>登录</button>";
                            $("span#dhcp_fc"+cur_vm_id).append(str);
                            
                            $("div#vm_st"+cur_vm_id).empty();
                            str = "";
                            str = str + "<i class=\"icon-minus-sign\"></i>";
                            $("div#vm_st"+cur_vm_id).append(str);
                            
                            $("span#vm_fc"+cur_vm_id).empty();
                            str = "";
                            str = str + "<button type=\"button\" onclick=\"do_vm_action('/plugins/vt/do/vm/action/"+cur_vm_id+"/create')\" class=\"btn btn-success start_btn\">启动</button>&nbsp;"
                                + "<button type=\"button\" onclick=\"\" class=\"btn\" disabled>登录</button>";
                            $("span#vm_fc"+cur_vm_id).append(str);
                        }//endif
                    }//endfor
                }//endif
                    
			}    
        	if (check){
                setTimeout("check_vm_status("+slice_id+")",5000);
            } 
        }
    });
}
