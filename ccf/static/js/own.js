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
    
    //slice步骤切换
    $(".tab_part:not(:first)").hide();
    $(".next_btn").click(function(){
       $("html, body").scrollTop(0);
       var thisIndex = $(".next_btn").index(this);
       var nowIndex = thisIndex + 1;
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
        if(!$(this).attr("checked")){
            $(".hide_form").slideUp();                     
        } else {
            $(".hide_form").slideDown();            
        }

    });
});

   
