var port_options = {
	animation : false
}
var port_chart_data = {
	labels : br_values,
	datasets : [
		{
			fillColor : "rgba(220,220,220,0.5)",
			strokeColor : "rgba(220,220,220,1)",
			data : port_recv_values
		},
		{
			fillColor : "rgba(151,187,205,0.5)",
			strokeColor : "rgba(151,187,205,1)",
			data : port_send_values
		}
	]
}


var ctx_port = document.getElementById('port_perf_chart').getContext("2d");
var port_chart = new Chart(ctx_port);

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

function update_port_data(host_id, br, port){
	$.ajax({
		url: '/slice/monitor/port/',
		method: 'POST',
		//data : "host_id = " + host_id,
		dataType : 'json',
		success : function(port_data){
		
			port_recv_values.shift();
			port_recv_values.push(port_data['port_recv_data']);
			port_chart_data["datasets"][0]["data"] = port_recv_values;

			port_send_values.shift();
			port_send_values.push(port_data['port_send_data']);
			port_chart_data["datasets"][1]["data"] = port_send_values;
			
			new Chart(ctx_port).Bar(port_chart_data, port_options);
		}
	});
}

var port_timer;
function get_port_info(host_id, br, port){
	clearTimeout(port_timer);
	update_port_data(host_id, br, port);
    port_timer = setTimeout(function(){get_port_info(host_id, br, port)}, 1000);
}
