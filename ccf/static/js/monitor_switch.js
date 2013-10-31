var br_values = [];
var port_recv_values = [];
var port_send_values = [];

for (var i=0; i<10; i++){
	br_values[i] = "";
	port_send_values[i] = 0;
	port_recv_values[i] = 0;
}

var port_options = {
	animation : false,
	bezierCurve : true,
	scaleOverride : false
}


var port_chart_data = {
    labels : br_values,
    datasets : [
        {
            fillColor : "rgba(153,204,255,0.5)",
			strokeColor : "rgba(0,153,204,1)",
			pointColor : "rgba(0,153,204,1)",
            pointStrokeColor : "#fff",
            data : port_recv_values
        },
		{
            fillColor : "rgba(204,204,255,0.5)",
			strokeColor : "rgba(204,0,51,0.8)",
			pointColor : "rgba(204,0,51,0.8)",
            pointStrokeColor : "#fff",
            data : port_send_values
        }
    ]
}

function data_process(data){    
    if (data > 1024){
		data = data/1024 //KB
        if (data > 1024){
			data = data/1024 //MB
            if (data >1024){
				data = data/1024 //GB
			}
                
		}
            

	}
    return Math.round(data);
}

function data_process_unit(data, unit){
    if (data > 1024){
		data = data/1024 //KB
        unit = 'KB'
        if (data > 1024){
			data = data/1024 //MB
            unit = 'MB'
            if (data >1024){
				data = data/1024 //GB
                unit = 'GB'
			}
                
		}
            

	}
    return unit
}


var ctx_port = document.getElementById('port_perf_chart').getContext("2d");
var port_chart = new Chart(ctx_port);


function get_br_info(switch_id, flag){
	var default_show_br;
	var default_show_port;	 
    $.ajax({
        url: '/monitor/get_br_info/' + switch_id + '/',
        type : 'GET',
        dataType : 'json',
        error : function(){
            //alert("get bridge information error!");
        },
        success : function(br_info){
            var context = '';
            for(var i=0; i<br_info.length; i++){
                var br = br_info[i]["br_name"];
                context = context + "<li class='dropdown active'><a class='dropdown-toggle' data-toggle='dropdown' href='#'>"+ br +"</a><ul class='dropdown-menu'>";
                for (var j=0; j<br_info[i]["ports"].length; j++){
                    var port = br_info[i]["ports"][j];
					default_show_br = br;
					default_show_port = port;
					args = switch_id + ",\"" +br +"\",\"" + port +"\"";
                    context = context + "<li><a href='#' onclick='get_port_info(" + args + ")'>"+ port + "</a></li>";

                }
                context = context + "</ul></li>";
            }
			if(flag){
				document.getElementById('br_info').innerHTML = context;
			}
            
			get_port_info(switch_id, default_show_br, default_show_port, flag)
        }
		
    });
		
	
}

var pre_recv_data = 0;
var pre_send_data = 0;
function update_port_data(switch_id, br, port, flag){
	$.ajax({
		url: '/monitor/port/',
		type : 'POST',
		data : "switch_id=" + switch_id + "&br=" + br + "&port=" + port 
				+ "&pre_recv_data=" + pre_recv_data +"&pre_send_data=" + pre_send_data,
		dataType : 'json',
		success : function(port_data){
		
			port_recv_values.shift();
			port_recv_values.push(port_data['recv_bps']/1024);
			port_chart_data["datasets"][0]["data"] = port_recv_values;
			pre_recv_data = port_data['port_recv_data']

			port_send_values.shift();
			port_send_values.push(port_data['send_bps']/1024);
			port_chart_data["datasets"][1]["data"] = port_send_values;
			pre_send_data = port_data['port_send_data']
			new Chart(ctx_port).Line(port_chart_data, port_options);
			if(flag){
				document.getElementById('id_port_send').innerHTML = data_process(port_data['port_send_data']) + data_process_unit(port_data['port_send_data'], 'bit');
				document.getElementById('id_port_recv').innerHTML = data_process(port_data['port_recv_data']) + data_process_unit(port_data['port_recv_data'], 'bit');
			}
			document.getElementById('id_port_send_bps').innerHTML = data_process(port_data['send_bps']) + data_process_unit(port_data['send_bps'], 'bit');
			document.getElementById('id_port_recv_bps').innerHTML = data_process(port_data['recv_bps']) + data_process_unit(port_data['recv_bps'], 'bit');
			
			
		}
	});
}

var port_timer;
function get_port_info(switch_id, br, port, flag){
	
	clearTimeout(port_timer);
	update_port_data(switch_id, br, port, flag);
    port_timer = setTimeout(function(){get_port_info(switch_id, br, port, flag)}, 1000);
}
