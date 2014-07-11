$(document).ready(function(){
	$.ajax({
		url : '/plugins/vt/get_flavor_msg/',
		type : 'GET',
		dataType: 'json',
        async: false,
		success:function(data){
			var cpu_context = '';
            $.each(data.cpus, function(i, val){
                cpu_context += '<a href="javascript:void(0);" id="cpu_'+val+'" value="'+val+'">'+val+' 核</a>';
            });
            $(".cpu_chose").html(cpu_context);
            $(".cpu_chose>:first-child").addClass("vm_active");
            rams = data.rams;
            var ram_json = '{';
            $.each(rams, function(i, val){
                var j = i + 1;
                if(j == rams.length){
                    ram_json += '"' + val + '":'+ j +"}"
                }else{
                    ram_json += '"' + val + '":'+ j +","
                }    
                
            });
            ram_flavor = $.parseJSON(ram_json);
            $(".value_s").html(rams[0]+" MB");
            var max_rams = rams[data.rams.length - 1];
            if(max_rams >= 1024){
                $(".value_e").html(max_rams/1024 +" GB");
            }else{
                $(".value_e").html(max_rams +" MB");
            }
            $(".micro").addClass("vm_active");

		}
	});
    //创建虚拟机页面类型、cpu选择
	$(".type_chose a").click(function(){
	    $(".type_chose a").removeClass("vm_active");
	    $(this).addClass("vm_active");
		var flavor_id = $(this).attr("value");
		$(".cpu_chose a").removeClass("vm_active");
		select_flavor(flavor_id);
		
	});
	$(".cpu_chose a").click(function(){
	    if(!$(this).hasClass("disabled")){
	        $(this).siblings().removeClass("vm_active");
            $(".type_chose a").removeClass("vm_active");
            $(this).addClass("vm_active");
	    }        
    });
	$( "#ram_slider" ).slider({
		stop:function(event, ui){
			$(".type_chose a").removeClass("vm_active");
		}
	});
    $("[style='display: block;']").children("div:first").children("a:first").addClass('active'); 

    $('#edit_vm').click(function(){
        var vm_id = $('.tr.active').find('.vm').attr('vm_id');
        if($('#'+vm_id+'_qt').children('img').attr('title') == '停止' && $('#'+vm_id+'_qt').attr('style') == 'cursor: pointer;'){
            $('#alert_info').text('虚拟机运行时无法修改性能参数，请先关闭虚拟机！');
            $('#alert_modal').modal();
        }else if($('#'+vm_id+'_qt').attr('style') == 'cursor: not-allowed;'){
            
        }else{
            $('#para_pz').modal();
        }

    });

    $('.edit-vm-submit').click(function(){
        var s_cpu = $(".cpu_chose").children("a.vm_active").attr("value");
        var s_ram = rams[$("#ram_slider").slider( "option", "value" ) - 1];
        var vm_id = $('.tr.active').find('.vm').attr('vm_id');
        $.ajax({
            type: 'POST',
            url: "/plugins/vt/edit_vm/",
            dataType: "json",
            data:{
                vm_id: vm_id,
                cpu: s_cpu,
                mem: s_ram
            },
            cache: false,
            success: function(data){
                $('#para_pz').modal('hide');
                if(data.result == 0){
                    $('#alert_info').text('虚拟机性能参数设置成功！');
                }else{
                    $('#alert_info').text('虚拟机性能参数设置失败！');
                }
                $('#alert_modal').modal();
            }
        });
    });
});


//验证vm名称是否是字母数字下划线
function check_vminfo(){
        //image = check_vm_select('image');
        server = check_vm_select('server');
        return server
}

/*function check_vm_name(obj){
    var objs = document.getElementsByName(obj);
	var infos = document.getElementsByName(obj+"Info"); 
	var reg = /^[a-zA-Z_]\w*$/;
        var results = new Array();
        var result = true;
        for(var i=0; i < objs.length; i++)
        {
                obj = objs[i];
                info = infos[i];
                if(obj.value.length > 0){
                        if(!reg.test(obj.value))
                        {
                                showMsg(info,"请输入字母数字下划线的组合（不以数字开头）","err");
                                results[i] = false;
                        }
                        else
                        {
                                showMsg(info,"","ok");
                                results[i] = true;
                        }
                
                }
                else
                {
                        showMsg(info,"该项为必填项","err");
                        results[i] = false;
                }	
        }

        for(var i=0; i < objs.length; i++)
        {
                result = result && results[i];
        }
        return result
}*/

//验证vm的flavor,image,server等以select形式提供的选项不能为空
function check_vm_select(ele){
	var field = ele;
	var objs = document.getElementsByName(ele);
	//var infos = document.getElementsByName(ele+"Info"); 
    var infos = $('[name="'+ele+'Info"]');
        var results = new Array();
        var result = true;
        for(var i=0; i < objs.length; i++)
        {
               obj = objs[i];
               info = infos[i];
               if(obj.selectedIndex == 0){
						$("."+ele+"").addClass("has-error");
                        showMsg(info,"该项为必填项","err")
                        results[i] = false;
               }
               else
               {
					   $("."+ele+"").removeClass("has-error");
                       showMsg(info,"","ok");
                       results[i] = true
					   
					   if(field == 'flavor'){
						}
						else if(field == 'image'){
						}
						else if(field == 'server'){
						}
               }	
        }
        for(var i=0; i < objs.length; i++)
        {
                result = result && results[i]
        }
        return result
}


/*function get_text_from_select(obj)
{
	var objs = document.getElementsByName(obj);
        //var obj = document.getElementById(obj);
        var results = new Array();
        for(var i=0; i < objs.length; i++)
        {
                obj = objs[i];
                //alert(obj.selectedIndex)
                text = obj.options[obj.selectedIndex].text
                results[i] = text
        }
        return results
}

function get_value_from_select(obj)
{
	var objs = document.getElementsByName(obj);
        //var obj = document.getElementById(obj);
        var results = new Array();
        for(var i=0; i < objs.length; i++)
        {
                obj = objs[i];
                value = obj.value
                results[i] = value
        }
        return results
}

function get_checked_from_checkbox(obj)
{
	var objs = document.getElementsByName(obj);
        //var obj = document.getElementById(obj);
        var results = new Array();
        for(var i=0; i < objs.length; i++)
        {
                obj = objs[i];
                if(obj.checked)
                {
                        results[i] = '是';
                }else{
						 results[i] = '否';
				}
               
        }
        return results
}

function get_checked_value_from_checkbox(obj)
{
	var objs = document.getElementsByName(obj);
        //var obj = document.getElementById(obj);
        var results = new Array();
        for(var i=0; i < objs.length; i++)
        {
                obj = objs[i];
                results[i] = obj.checked
        }
        return results
}

function get_value_from_obj(obj)
{
	var objs = document.getElementsByName(obj);
        //var obj = document.getElementById(obj);
        var results = new Array();
        for(var i=0; i < objs.length; i++)
        {
                obj = objs[i];
                results[i] = obj.value
        }
        return results
}

function insert_content_to_obj(obj, content)
{
        var obj = document.getElementById(obj);
        obj.innerHTML = content;
}

function insert_content_to_obj1(obj, content)
{
        var obj = document.getElementById(obj);
        obj.innerHTML = obj.innerHTML + content;
}
*/
//逐一提交vm的创建请求
/*var post_vm_result = true;
var quota = true;
function submit_vms(sliceid)
{
		vms_info().each(function(vm){
			post_vminfo(sliceid);
		});
        
}*/


function post_vminfo(sliceid){
    $("#submit_vm").attr("disabled", "disabled");
    if(!check_vminfo()){
        return;
    }
    var s_flavor = $(".type_chose").children("a.vm_active").attr("value");
    if(s_flavor == undefined){
        s_flavor = 0;
    }
    var s_cpu = $(".cpu_chose").children("a.vm_active").attr("value");
    var s_ram = rams[$("#ram_slider").slider( "option", "value" ) - 1];

    var image_uuid = $(".clearfix.active").children(".pull-right").text();
    /*var enable_dhcp_checked;
	if($('.switch_btn.dhcp.vm').hasClass("checked")){
		enable_dhcp_checked = 1;
	}else{
		enable_dhcp_checked = 0;
	} */   
    $.ajax({
        type: "POST",
        url: "/plugins/vt/create/vm/"+sliceid+"/",
        dataType: "json",
        cache: false,
        async: false,  
        data: {
				flavor: s_flavor,
				cpu: s_cpu,
				ram: s_ram,
				hdd: 10,
                image: image_uuid,
                server: $("#id_server").val(),
                enable_dhcp: 1
        },
        success: function(data) {
            if(data.result==1)
            {
                $("div#slice_alert_info").empty();
                str = "" + "<p class=\"text-center\">" + data.error + "</p>";
                $("div#slice_alert_info").append(str);
                $('#slicealertModal').modal('show');
                $("#submit_vm").removeAttr("disabled");
            }else if(data.result == -1){
                //quota = false;
                $("#quota_info").html(data.error);
                $(".alert_quota").show();
                $("#submit_vm").removeAttr("disabled");
            }else{
                window.location.href='/slice/detail/' + sliceid + '/1/';
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

function showMsg(_info, msg, state){
	var info=_info;
	if(state == 'ok'){
		info.innerHTML = "";
	}else{
		info.innerHTML = msg;
		info.style.color = "red";
	}
}


//获取被用户选择的server
function fetch_serverinfo(id){
    server_names = get_select_server_name();
    server_ids = get_select_server_id();
    content = '<option value="" selected="selected">---------</option>';
    for(var i=0; i < server_ids.length; i++)
    {
        content = content + '<option value="' + server_ids[i];
        content = content +  '">';
        content = content + server_names[i];
        content = content + '</option>';
    }
    var objs = $("[id='"+id+"']");
    for (var i=0; i<objs.length; i++){
        objs[i].innerHTML = "" + content;
    }
}

function fetch_gw_ip(slice_name){
    var ret = false;
    $.ajax({
        url : "/plugins/vt/get_slice_gateway_ip/" + slice_name + "/",
        type : "GET",
        contentType: "application/json; charset=utf-8",
        dataType : "json",
        error : function(e){
			document.getElementById('alert_info').innerHTML = "获取网关IP出错！";
			$('#alert_modal').modal('show');
        },
        success : function(gw_ips){
            document.getElementById("gateway_ip").value = gw_ips["ipaddr"];
            ret = true;
        }
    });
    return ret;
}
/*var ovs_check_flag = false;
function check_ovs_gw(){
	return ovs_check_flag;
}*/

function get_select_server_name(){
    var tp_mod = $('select[name="tp_mod"]').val();
    var j =0
    var results = new Array();
    ovs_check_flag = false;
    if(tp_mod == 2){
        for(dpid in window.selected_dpids) {
            if (dpid.indexOf('00:ff:') == 0) {
                ovs_check_flag = true;
                switch_ids_obj = document.getElementsByName("switch"+dpid);
                servername = switch_ids_obj[0].getAttribute("servername");
                if( servername && not_contains(results, servername))
                {
                    results[j] = servername;
                    j++;
                }
            }
        }
    }else{
        var switch_port_ids_obj = document.getElementsByName("switch_port_ids");
        for(var i=0;i<switch_port_ids_obj.length;i++){
            obj = switch_port_ids_obj[i];
            if(!obj.disabled){
    			if(obj.getAttribute("switchtype") == 3){
    				ovs_check_flag = true;
    			}
                servername = obj.getAttribute("servername");
                if( servername && not_contains(results, servername))
                {
                    results[j] = servername;
                    j++;
                }
            }
        }
    }   
    return results
}
function get_select_ports(){
	var port_ids = ""
    var switch_port_ids_obj = document.getElementsByName("switch_port_ids");
    var results = new Array();
    var j =0
    for(var i=0;i<switch_port_ids_obj.length;i++){
        obj = switch_port_ids_obj[i];
        if(!obj.disabled){
			port_ids = port_ids + obj.value + ",";
        }
    }
	port_ids = port_ids.substr(0,port_ids.length-1);
    return port_ids;
}
function get_select_switches(){
    var switch_ids = ""
    for(dpid in window.selected_dpids) {
        switch_ids_obj = document.getElementsByName("switch"+dpid);
        switchid = switch_ids_obj[0].getAttribute("value");
        if( switchid ){
            switch_ids = switch_ids + switchid + ",";
        }
    }
    switch_ids = switch_ids.substr(0,switch_ids.length-1);
    return switch_ids;
}
function get_select_server_id(){
    var tp_mod = $('select[name="tp_mod"]').val();
    var j =0
    var results = new Array();
    if(tp_mod == 2){
        for(dpid in window.selected_dpids) {
            if (dpid.indexOf('00:ff:') == 0) {
                switch_ids_obj = document.getElementsByName("switch"+dpid);
                serverid = switch_ids_obj[0].getAttribute("serverid");
                if( serverid && not_contains(results, serverid))
                {
                    results[j] = serverid;
                    j++;
                }
            }
        }
    }else{
        var switch_port_ids_obj = document.getElementsByName("switch_port_ids");
        for(var i=0;i<switch_port_ids_obj.length;i++){
            obj = switch_port_ids_obj[i];
            if(!obj.disabled){
                serverid = obj.getAttribute("serverid");
                if( serverid && not_contains(results, serverid))
                {
                    results[j] = serverid;
                    j++;
                }
            }
        }      
    } 
    return results; 
}

/*function not_contains(a, obj) {
    for (var i = 0; i < a.length; i++) {
        if (a[i] === obj) {
            return false;
        }
    }
    return true;
}*/

/*function create_vms(sliceid, flag)
{
	/*if(vms_info().count() == 0){
		document.getElementById('alert_info').innerHTML = "请先添加虚拟机配置信息！";
		$('#alert_modal').modal('show');
		return;
	}
    var enable_dhcp_checked;
	if($('.switch_btn.dhcp.vm').hasClass("checked")){
		enable_dhcp_checked = 1;
		dhcp_checked = "是";
	}else{
		enable_dhcp_checked = 0;
		dhcp_checked = "否";
	}
    vms_info.insert({id:vm_id, flavor:flavor_selected, cpu:cpu_selected, 
						 ram:ram_selected, hdd:hdd_selected, image_id:$("#id_image").val(),
						 image_text:$("#id_image").find("option:selected").text(),
						 server_id:$("#id_server").val(), server_text:$("#id_server").find("option:selected").text(),
						 enable_dhcp:enable_dhcp_checked,
						 show_dhcp:dhcp_checked})
    if(check_vminfo())
    {
		submit_vms(sliceid)
        if (!quota) {
            //window.location.href='/quota_admin/apply/'
            return;
        };
		//if(flag != 1 || post_vm_result){
			window.location.href='/slice/detail/' + sliceid + '/1/';
		//}        
    }
}*/

function open_vnc(url)
{
    window.open(url,'','width=968,height=552')
}

function do_vm_action(url)
{
        $.ajax({
        type: "GET",
        url: url,
        dataType: "json",
        cache: false,
        async: false,  
        success: function(data) {
            if(data.result==1)
            {
				document.getElementById('alert_info').innerHTML = data.error;
				$('#alert_modal').modal('show');
            }else{
                window.location.reload();
			}
        }
        });
}

/*function delete_vm_from_list(url) {
	$.ajax({
		type: 'GET',
		url: url,
		dataType: 'json',
		success: function(data) {
			if(data.result == 1) {
				document.getElementById('vm_alert').innerHTML = data.error_info;
				$('.vm_alert').show();
			}else{
				window.location.reload();
			}
		}
	});
}*/

function show_topology(){
	$('#topologyModal').modal('show');
}

function check_gw_select(){
	var info = document.getElementById('gwInfo');
	if($('#id_server_gw').get(0).selectedIndex == 0){
		$(".gw_ip").addClass("has-error");
		showMsg(info,"该项为必填项","err");
		return false;
	}else{
		info.innerHTML = '';
		$(".gw_ip").removeClass("has-error");
		return true;
	}
}




/*function flavor_init(){
	vm_id = 0;
	flavor_selected = 1;
	cpu_selected = 1;
	ram_selected = 256;
	hdd_selected = 10;
	//vm_info_flag = "save";
	//update_vm = null;
	
}*/

/*
function update_vms_info(){
	var enable_dhcp_checked;
	if(!check_vminfo()){
		return
	}
	if($('.switch_btn.dhcp.vm').hasClass("checked")){
		enable_dhcp_checked = 1;
		dhcp_checked = "是";
	}else{
		enable_dhcp_checked = 0;
		dhcp_checked = "否";
	}
	if (vm_info_flag == "save"){
		//var vm_info = {id:vm_id, flavor:flavor_selected,};
		vms_info.insert({id:vm_id, flavor:flavor_selected, cpu:cpu_selected, 
						 ram:ram_selected, hdd:hdd_selected, image_id:$("#id_image").val(),
						 image_text:$("#id_image").find("option:selected").text(),
						 server_id:$("#id_server").val(), server_text:$("#id_server").find("option:selected").text(),
						 enable_dhcp:enable_dhcp_checked,
						 show_dhcp:dhcp_checked})
		vm_id++;
		
	}else if (vm_info_flag == "update"){
		if(update_vm != null){
			update_vm.update({flavor:flavor_selected, cpu:cpu_selected, 
						 ram:ram_selected, hdd:hdd_selected, image_id:$("#id_image").val(),
						 image_text:$("#id_image").find("option:selected").text(),
						 server_id:$("#id_server").val(), server_text:$("#id_server").find("option:selected").text(),
						 enable_dhcp:enable_dhcp_checked,
						 show_dhcp:dhcp_checked});
			vm_info_flag = "save";
		}
	}
	show_vm_info_table();
}


function edit_vm(vm_id){
	var vm = vms_info({id:vm_id}).first();
	vm_info_flag = "update";
	//替换上面的数据
	update_vm = vms_info({id:vm_id});
	$(".type_chose a").removeClass("vm_active");
	$("a[value="+vm.flavor+"]").addClass("vm_active");
	$(".cpu_chose a").removeClass("vm_active");
	$("#cpu_"+vm.cpu).addClass("vm_active");
	$("#ram_slider").slider("value", ram_flavor[vm.ram]);
	//$("#disk_slider").slider("value", disk_flavor[vm.hdd]);
}

function delete_vminfo(vm_id){
	vms_info({id:vm_id}).remove();
	show_vm_info_table();
}

function show_vm_info_table(){
	$("#vms_info_table").find("tbody").empty();
	vms_info().each(function(vm){
		var ram = vm.ram, unit = 'MB';
		if(ram >= 1024){
			ram = ram/1024;
			unit = 'GB';
		}
		$("#vms_info_table").find("tbody").append("<tr>"
                            +"<td>"+flavor_text[vm.flavor]+"</td>"
                            +"<td>"+vm.cpu+" 核</td>"
                            +"<td>"+ram+" "+unit+"</td>"
                            //+"<td>"+vm.hdd+" GB</td>"
                            +"<td>"+vm.image_text+"</td>"
                            +"<td>"+vm.server_text+"</td>"
							+"<td>"+vm.show_dhcp+"</td>"
                            +"<td class='btn_operation'>"
                            +"   <a href='javascript:;' onclick='javascript:delete_vminfo("+vm.id+")'>"
                            +"    <img src='"+STATIC_URL+"img/btn_sc.png' title='删除'>"
                            +"    </a>"
                            +"</td>"
                          +"</tr> ");
	});
}
*/
function select_flavor(flavor_id){
	var data = "name=flavor" + "&obj_id="+flavor_id;
	$.ajax({
		url : '/plugins/vt/get_flavor_msg/',
		type : 'POST',
		data: data,
		dataType: 'json',
		success:function(data){
			$("#cpu_"+data['cpu']).addClass("vm_active");
			$("#ram_slider").slider("value", ram_flavor[data['ram']]);
		}
	});
}

/*function set_value(obj, value){
    vms_info().remove();
    quota = true;
	if(obj == "flavor"){
		flavor_selected = value;
	}else if(obj == "ram"){
		flavor_selected = 0;
		ram_selected = rams[value-1];
	}else if(obj == "hdd"){
		flavor_seleted = 0;
		hdd_selected = disks[value-1];
	}else if(obj == "cpu"){
		flavor_selected = 0;
		cpu_selected = value;
	}
}*/
/*
$('.switch_btn.dhcp').on("click", function(){
			if($(this).hasClass("checked")) {
                $(this).removeClass("checked");
                $(this).children(".switch_content").html("否");
            }else{
				$(this).addClass("checked");
                $(this).children(".switch_content").html("是");
			}
		});

*/

