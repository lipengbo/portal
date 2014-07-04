$(function(){
    $(".select_switch").find("label").click(function(){
        $(this).parent(".radio_tab").siblings(".radio_tab").find(".radio_select_form").attr("disabled","disabled");
        var obj = $(this).parent(".radio_tab").siblings(".radio_tab");
        if(obj.hasClass('has-error')){
            obj.removeClass('has-error');
        }
        $(this).parent(".radio_tab").siblings(".radio_tab").find("button").addClass("disabled");
        $(this).parent(".radio_tab").siblings(".radio_tab").find("input[type='file']").attr("disabled","disabled");
        $(this).siblings().find(".radio_select_form").removeAttr("disabled");
        $(this).siblings().find("button").removeClass("disabled");
        $(this).siblings().find("input[type='file']").removeAttr("disabled");
    });
});
