function post_sliceinfo(slice_id){
    ret1 = check_slice_description('slice_description',1)
    var has_virtual_switch = false;
    var slice_type = $("#slice_type").text();
    if(slice_type == "baseslice"){
        for(dpid in window.selected_dpids) {
            if (dpid.indexOf('00:ff:') != 0) {
                has_virtual_switch = true;
            }
        }
    }else{
        for(dpid in window.selected_dpids) {
            if (dpid.indexOf('00:ff:') == 0) {
                has_virtual_switch = true;
            }
        }
    }
    if (!has_virtual_switch) {
        $('.no-virtual-switch').removeClass('hide').show();
    }else{
        $('.no-virtual-switch').addClass('hide').show();
    }
    if(ret1 && has_virtual_switch){
        var obj = document.getElementById('slice_description');
        check_url = "http://" + window.location.host + "/slice/edit_slice/"+slice_id+"/";
        var flag = false;
        var j = 0;
        var switch_dpids = "";

        for(dpid in window.selected_dpids){
            if(j==0){
                switch_dpids = dpid;
            }
            else{
                switch_dpids = switch_dpids + "," + dpid;
            }
            j++;
        }  
        $.ajax({
                type: "POST",
                url: check_url,
                dataType: "json",
                data: {"slice_description": obj.value, "switch_dpids": switch_dpids},
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
                    str = "" + "<p class=\"text-center\">编辑失败！</p>";
                    $("div#slice_alert_info").append(str);
                    $('#slicealertModal').modal('show');
                }
        });
        if(flag){
            location.href = "http://" + window.location.host + "/slice/detail/"+slice_id+"/";
        }
    }else{
        return false;
    }
}