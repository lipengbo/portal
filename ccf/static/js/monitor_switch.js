function get_br_info(switch_id){
	 
    $.ajax({
        url: '/monitor/get_br_info/' + switch_id + '/',
        type : 'GET',
        dataType : 'json',
        error : function(){
            alert("get bridge information error!");
        },
        success : function(br_info){
            //alert(br_info[0]["ports"].length);
            //alert(br_info.length);
            var context = '';
            for(var i=0; i<br_info.length; i++){
                var br = br_info[i]["br_name"];
                context = context + "<li class='dropdown active'><a class='dropdown-toggle' data-toggle='dropdown' href='#'>"+ br +"</a><ul class='dropdown-menu'>";
                for (var j=0; j<br_info[i]["ports"].length; j++){
                    var port = br_info[i]["ports"][j];
					args = switch_id + ",\"" +br +"\",\"" + port +"\"";
                    context = context + "<li><a href='#' onclick='get_port_info(" + args + ")'>"+ port + "</a></li>";

                }
                context = context + "</ul></li>";
            }

            document.getElementById('br_info').innerHTML = context;
        }
    });
}
