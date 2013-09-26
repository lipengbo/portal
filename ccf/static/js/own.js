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
		$(".sec_block").first().clone(true).appendTo(".vm_info_list");		
		$(".sec_block").last().find("input[type='text']").val("");
		$(".sec_block").last().find("input[type='checkbox']").attr("checked","true");
		$(".sec_block").last().find(".del").css("visibility","visible");
		$(".sec_block:odd").css("background","#d9edf7");
	});
	$(".del").click(function(){
       $(this).parent(".operate_btn").parent(".sec_block").remove();
       $(".sec_block").css("background","#dff0d8");
       $(".sec_block:odd").css("background","#d9edf7");
    });
    
    //创建slice第3步，选择控制器配置方式
    $(".tab_radio1").click(function(){
        $(this).parent("td").siblings("td").children("select").removeAttr("disabled");
        $(".tab_radio2").parent("td").siblings("td").children("input").attr("disabled","disabled");
    });
    $(".tab_radio2").click(function(){
        $(this).parent("td").siblings("td").children("input").removeAttr("disabled");
        $(".tab_radio1").parent("td").siblings("td").children("select").attr("disabled","disabled");
    });
    $(".tab_radio3").click(function(){
        $(this).parent("td").parent("tr").siblings("tr").children("td").children("input").attr("disabled","disabled");
    });
    $(".tab_radio4").click(function(){
        $(this).parent("td").parent("tr").siblings("tr").children("td").children("input").removeAttr("disabled");
    });
    
    //slice详情启动停止按钮
    $(".start_btn").click(function(){
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
    });
    // show topology
    $('.btn-step1').click(function () {
        var island_id = $('select[name="island_id"]').val();
        $('#topology-iframe').attr('src', '/topology/?no_parent=true&show_virtual_switch=true&hide_filter=true&island_id=' + island_id);
    });
    
    $('.btn-step4').click(function () {
        $('.switch-manifest tbody').html('');
        $.each($('.switch-table tbody tr'), function (index, tr) {
            var checked_ports = $(tr).find('input[name="switch_port_ids"][checked]');
            if (checked_ports.length > 0) {
                var clone = $(tr).clone();
                clone.find('input[name="switch_port_ids"]').remove();
                clone.find('label').addClass('label label-success');
                $('.switch-manifest tbody').append(clone);
            }
        });
        $('.switch-manifest tbody input').attr('disabled', '');
    });
    //slice步骤切换
    $(".tab_part:not(:first)").hide();
    $(".next_btn").click(function(){
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
           page_function3();
       }
       if(thisIndex == 4){
           page_function4();
       }
       $(".tab_part").hide();
       $(".tab_part").eq(nowIndex).show();
       $(".nav-pills .span2").eq(thisIndex).children(".step").children(".desc").removeClass("active");
       $(".nav-pills .span2").eq(nowIndex).addClass("visit");
       $(".nav-pills .span2").eq(nowIndex).children(".step").children(".desc").addClass("active");
    });
    $(".prev_btn").click(function(){
       $("html, body").scrollTop(0);
       var thisIndex = $(".prev_btn").index(this) + 1;
       var nowIndex = thisIndex - 1;
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
           $(".icheckbox_square-blue").addClass("checked");
       } else {
           $(".icheckbox_square-blue").removeClass("checked");
       }
    });
         
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
	ret1 = check_nw_num();
	if (ret1){
		return true;
	}
	else{
		return false;
	}
}
function page_function2(){
	ret1 = check_slice_controller('controller_type');
	if (ret1){
		return true;
	}
	else{
		return false;
	}
}
function page_function3(){
	var slice_nw = document.getElementById("slice_nw");
	var list_slice_nw = document.getElementById("list_slice_nw");
	list_slice_nw.innerHTML = slice_nw.innerHTML;
	
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
			        + "<td width=\"100\">默认创建</td>"
			        + "<td></td>"
			        + "</tr>"
			        + "<tr>"
			        + "<td width=\"100\">控制器类型：</td>"
			        + "<td>" + controller_sys + "</td>"
			        + "</tr>"                     
			        + "</tbody>"
			        + "</table>";
			    
			}  
			if(controller_type_obj[i].value=="user_defined"){
				var controller_ip_obj = document.getElementById("controller_ip");
				var controller_port_obj = document.getElementById("controller_port");
				var controller_ip = controller_ip_obj.value;
				var controller_port = controller_port_obj.value;
				var str = "";
				str = str + "<table class=\"table\">"
			        + "<tbody>"
			        + "<tr>"
			        + "<td width=\"100\">自定义</td>"
			        + "<td></td>"
			        + "</tr>"
			        + "<tr>"
			        + "<td width=\"100\">控制器IP端口：</td>"
			        + "<td>" + controller_ip + ":" + controller_port + "</td>"
			        + "</tr>"                     
			        + "</tbody>"
			        + "</table>";        
	  		}  
		}   
	}
	$("div#list_controller").append(str); 
	
}
function page_function4(){
	
}
