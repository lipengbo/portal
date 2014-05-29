function update_list(url){
    var list_show = "list_show"
    var is_slice_detail = false;
    urls = url.split("?");
    if(urls.length == 2){
        f_urls = urls[0].split("/");
        //alert(f_urls);
        //alert(f_urls.length);
        if(f_urls.length >= 7){
            //alert(f_urls[3]);
            //alert(f_urls[4]);
            if(f_urls[3]=="slice" && f_urls[4]=="detail"){
                is_slice_detail = true;
                objs = $(".slice_index");
                for(var i=0;i<objs.length;i++){
                    if($(objs[i]).hasClass("on")){
                        if($(objs[i]).hasClass("xnj")){
                            list_show = "list_vm";
                            urls[1] = "div_name=list_vm&" + urls[1];
                        }
                        if($(objs[i]).hasClass("zjr")){
                            list_show = "list_port";
                            urls[1] = "div_name=list_port&" + urls[1];
                        }
                    }
                }
                url = urls[0] + "?" + urls[1];
            }
        }
    }
    //check_url = "http://" + window.location.host + url;
    check_url = url;
    //alert(check_url);
    var ret = false;
    $.ajax({
        type: "GET",
        url: check_url,
        dataType: "html",
        cache: false,
        async: false,  
        success: function(data) {
            if (data)
             {
                //alert("ok");
                $("div#"+list_show).empty();
                $("div#"+list_show).append(data);
                if(is_slice_detail && list_show!="list_port") {
                     show_uuid($("[id='uuid']"));
                     update_vm_status();
                     $('.uuid').tooltip();
                }
                
             } 
             else
             {
                //alert("false");
             }
        }
    });
    //alert('ju');
    return false;
}

function update_list_content(url, div_name){
    url = "" + url + "";
    urls = url.split("?");
    check_url = urls[0] + "?div_name=" + div_name;
    var ret = false;
    $.ajax({
        type: "GET",
        url: check_url,
        dataType: "html",
        cache: false,
        async: false,  
        success: function(data) {
            if (data)
             {
                //alert("ok");
                $("div#"+div_name).empty();
                $("div#"+div_name).append(data);
             } 
             else
             {
                //alert("false");
             }
        }
    });
    //alert('ju');
    return false;
}



$('a.endless_page_link').live("click", function(){
    var href = $(this).attr('href');
    update_list("http://" + window.location.host + href);
    return false;
});