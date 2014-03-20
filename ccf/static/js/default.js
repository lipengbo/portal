// JavaScript Document

$(function(){	
	//project
	$(".project_list_block").hover(function(){
		$(this).children(".close").show();
	},function(){
		$(this).children(".close").hide();
	});
	
	//slice
	$(".slice_list_block").hover(function(){
		$(this).children(".close").show();
	},function(){
		$(this).children(".close").hide();
	});	
	
	//用户管理首页
	$(".manage_index_block").hover(function(){
		$(this).children(".manage_index_block_r").children("img").animate({"opacity":"0.6"});
	},function(){
		$(this).children(".manage_index_block_r").children("img").animate({"opacity":"1"});
	});
	
	//虚网详情
	$(".slice_name i").click(function(){
		if($(".panel_defined").is(":hidden")){
			$(".panel_defined").slideDown();
			$(".slice_name i").removeClass("icon-caret-down").addClass("icon-caret-up");
		} else {
			$(".panel_defined").slideUp();
			$(".slice_name i").removeClass("icon-caret-up").addClass("icon-caret-down");
		}
	});
	$(".tuopu_btn .switch_btn").click(function(){
		if($(this).hasClass("checked")) {
			$(this).removeClass("checked");
			$(this).children(".switch_content").html("停止");
		}else {
			$(this).addClass("checked");
			$(this).children(".switch_content").html("启动");
		}
	});
	
	//全选全不选
    $("#checkAll").click(function(){
		$("input[name='subbox']").prop("checked",$(this).prop("checked"));
    });
	$("input[name='subbox']").each(function(){
		$(this).click(function(){
			if($("input[name='subbox']:checked").length == $("input[name='subbox']").length) {
				$("#checkAll").prop("checked",true);
			} else {
				$("#checkAll").prop("checked",false);
			}
		});	
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
});
