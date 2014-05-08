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
    
    //全选全不选
    $(".checkall input").click(function(){
        $(".checkboxs input[type='checkbox']:not(:disabled)").prop("checked",$(this).prop("checked")).trigger('change');
    });
    $(".checkboxs input[type='checkbox']").each(function(){
        $(this).click(function(){
            if($(".checkboxs input[type='checkbox']:checked").length == $(".checkboxs input[type='checkbox']").length) {
                $(".checkall input").prop("checked",true);
            } else {
                $(".checkall input").prop("checked",false);
            }
        });
    });
    $('.glyphicon-search').click(function(){
        $('form.search_defined').submit();
        return false;
    });
    $('.checkboxs input').on('change', function(event){
        if($(this).prop('checked')){
            $('.action-btn').removeClass('disabled');
        } else {
            if($('.checkboxs input:checked').length == 0) {
                $('.action-btn').addClass('disabled');
            } else {
                $('.action-btn').removeClass('disabled');
            }
        }
    });
    
    //slice_detail
    $(".slice_detail_tab a").click(function(){
        var tabIndex = $(this).parent(".col-md-4").index();
        $(".slice_detail_tab .col-md-4").removeClass("on").eq(tabIndex).addClass("on");
        $(".slice_detail_block").children(".slice_detail_content").hide().eq(tabIndex).show();
    });
});
