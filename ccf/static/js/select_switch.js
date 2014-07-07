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

function post_unicom_info(slice_id){
    var $selectRows = $(".select_multi_l").children(".select_row");
    var unicom_slice_ids = ""
    var j = 0;
    $selectRows.each(function () {
        var this_id = $(this).attr("id");
        if(j==0){
            unicom_slice_ids = $(this).attr("id");
        }
        else{
            unicom_slice_ids = unicom_slice_ids + "," + $(this).attr("id");
        }
        j++;
    });
    check_url = "http://" + window.location.host + "/slice/edit_unicom/"+slice_id+"/";
    var flag = false;
    $.ajax({
            type: "POST",
            url: check_url,
            dataType: "json",
            data: {"unicom_slice_ids": unicom_slice_ids},
            async: false, 
            success: function(data) {
                if (data.result == 1){
                    flag = true;
                }
                else{
                    $("div#slice_alert_info").empty();
                    str = "" + "<p class=\"text-center\">"+data.error_info+"</p>";
                    $("div#slice_alert_info").append(str);
                    $('#slicealertModal').modal('show');
                    if(data.result == 2){
                        $('.edit-confirm').click(function(){location.href = "http://" + window.location.host + "/slice/detail/"+slice_id+"/";});
                    }
                }
            },
            error: function(data) {
                $("div#slice_alert_info").empty();
                str = "" + "<p class=\"text-center\">配置失败！</p>";
                $("div#slice_alert_info").append(str);
                $('#slicealertModal').modal('show');
            }
    });
    if(flag){
        location.href = "http://" + window.location.host + "/slice/detail/"+slice_id+"/";
    }
}