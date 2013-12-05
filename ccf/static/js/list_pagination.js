function update_list(url){
    //alert("ok");
    check_url = "http://" + window.location.host + url;
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
                $("div#list_show").empty();
                $("div#list_show").append(data);
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
    update_list(href);
    return false;
});