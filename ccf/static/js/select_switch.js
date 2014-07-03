$(function(){
    $(".select_row").live("click",function(){
        if($(this).hasClass("active")) {
            $(this).removeClass("active");
        } else {
            $(this).addClass("active");
        }
    });
    $(".select_btn_l").click(function(){
        var $selectRows = $(".select_multi_r").children(".select_row.active");
        var $remove = $selectRows.remove();
        $remove.appendTo(".select_multi_l").removeClass("active");
    });
    $(".select_btn_r").click(function(){
        var $selectRows = $(".select_multi_l").children(".select_row.active");
        var $remove = $selectRows.remove();
        $remove.appendTo(".select_multi_r").removeClass("active");
    });    
});
