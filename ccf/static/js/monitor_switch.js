
var br_values = [];
var port_recv_values = [];
var port_send_values = [];
var br_ports = [];
var port_timer;

for (var i=0; i<21; i++){
	br_values[i] = "";
	port_send_values[i] = 0;
	port_recv_values[i] = 0;
}
br_values[20]="0s";
br_values[15]="5s";
br_values[10]="10s";
br_values[5]="15s";
br_values[0]="20s";


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

var ctx_port = document.getElementById('port_perf_chart').getContext("2d");
var port_chart = new Chart(ctx_port);

function change_port(switch_id, flag){
	//clearTimeout(port_timer);
	get_port_info(switch_id, $('#brs_info').find("option:selected").text(), $('#ports_info').val(), flag);
}
function change_br(switch_id, val, flag){
	$('#ports_info').empty()
	for (var i=0; i<br_ports[val].length; i++){
		$('#ports_info').append("<option value="+br_ports[val][i]+">"+br_ports[val][i]+"</option>");
	}
	//clearTimeout(port_timer);
	get_port_info(switch_id, $('#brs_info').find("option:selected").text(), $('#ports_info').val(), flag);
	
}



function get_br_info(switch_id, flag){
	var default_show_br;
	var default_show_port;	 
    $.ajax({
        url: '/monitor/get_br_info/' + switch_id + '/',
        type : 'GET',
        dataType : 'json',
        error : function(){
            //alert("获取网桥信息失败， 请检查agent是否启动并设置了ovs服务！");
			document.getElementById('alert_info').innerHTML = "获取网桥信息失败， 请检查agent是否启动并设置了ovs服务！";
			$('#alert_modal').modal('show');
        },
        success : function(br_info){
            var context = '';
			var brs='';
			
            for(var i=0; i<br_info.length; i++){
                var br = br_info[i]["br_name"];
                //context = context + "<li class='dropdown active'><a class='dropdown-toggle' data-toggle='dropdown' href='#'>"+ br +"</a><ul class='dropdown-menu'>";

				brs = brs + "<option value="+ i +">" + br +"</option>"
				var ports = [];
                for (var j=0; j<br_info[i]["ports"].length; j++){
                    var port = br_info[i]["ports"][j];
					//default_show_br = br;
					//default_show_port = port;
					//args = switch_id + ",\"" +br +"\",\"" + port +"\",\"" + flag + "\"";
                    //context = context + "<li><a href='#' onclick='get_port_info(" + args + ")'>"+ port + "</a></li>";
			
					ports.push(port);

                }
				br_ports.push(ports);
                //context = context + "</ul></li>";
            }
			if(flag){
				document.getElementById('br_info').innerHTML = context;
				document.getElementById('brs_info').innerHTML = brs;
				$('#brs_info').val(0);
				for (var i=0; i<br_ports[0].length; i++){
					$('#ports_info').append("<option value="+br_ports[0][i]+">"+br_ports[0][i]+"</option>");
				}
			}
			//get_port_info(switch_id, default_show_br, default_show_port, flag);
			//初始时设置默认网桥和端口
			change_br(switch_id, 0, flag);
			

        }
		
    });
		
	
}

var pre_recv_data = 0;
var pre_send_data = 0;
var return_data = true;
function update_port_data(switch_id, br, port, flag){
	return_data = false;
	$.ajax({
		url: '/monitor/port/',
		type : 'POST',
		data : "switch_id=" + switch_id + "&br=" + br + "&port=" + port 
				+ "&pre_recv_data=" + pre_recv_data +"&pre_send_data=" + pre_send_data,
		dataType : 'json',
		timeout : 1000,
		success : function(port_data){
			if(port_data.result == 1){
				document.getElementById('alert_info').innerHTML = port_data.error;
				$('#alert_modal').modal('show');
			}else{
			process_data = data_process_for_Y([port_data['recv_bps'], port_data['send_bps'], 'bit']);
			port_options['scaleOverride'] = false;
			port_recv_values.shift();
			port_recv_values.push(process_data[0]);
			port_chart_data["datasets"][0]["data"] = port_recv_values;
			pre_recv_data = port_data['port_recv_data']

			port_send_values.shift();
			port_send_values.push(process_data[1]);
			port_chart_data["datasets"][1]["data"] = port_send_values;
			pre_send_data = port_data['port_send_data'];
			if(count(port_recv_values) == 0 && count(port_send_values) == 0){
				port_options['scaleOverride'] = true;
			}
			
			new Chart(ctx_port).Line(port_chart_data, port_options);
			if(flag){
				document.getElementById('id_port_send').innerHTML = data_process(port_data['port_send_data']) + data_process_unit(port_data['port_send_data'], 'bit');
				document.getElementById('id_port_recv').innerHTML = data_process(port_data['port_recv_data']) + data_process_unit(port_data['port_recv_data'], 'bit');
			}
			document.getElementById('id_port_send_bps').innerHTML = data_process(port_data['send_bps']) + data_process_unit(port_data['send_bps'], 'bit');
			document.getElementById('id_port_recv_bps').innerHTML = data_process(port_data['recv_bps']) + data_process_unit(port_data['recv_bps'], 'bit');
			document.getElementById('net_unit').innerHTML = process_data[2];
			}
			return_data = true;
			
		}
		
	});
}


function get_port_info(switch_id, br, port, flag){
	//alert(br+"::"+port)
	//document.getElementById('current_br').innerHTML = " 网桥" + br;
	//document.getElementById('current_port').innerHTML = " 端口" + port;
	if(return_data){
		clearTimeout(port_timer);
		update_port_data(switch_id, br, port, flag);
    	port_timer = setTimeout(function(){get_port_info(switch_id, br, port, flag)}, 1000);
	}
	
}


