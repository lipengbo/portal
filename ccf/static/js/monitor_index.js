
var index_ctx_server = document.getElementById('manage_server_chart').getContext("2d");
var index_ctx_switch = document.getElementById('port_perf_chart').getContext("2d");

var cpu_values = [];
var mem_values = [];
var cpu_values_x_lable = [];

var pre_net_data = [0+":"+0];

for (var i=0; i<50; i++){
	cpu_values[i] = 0 + "";
	mem_values[i] = 0 + "";
    cpu_values_x_lable[i] = "";
}
var server_options = {
	bezierCurve : true
}

var server_index_chart_data = {
    labels : cpu_values_x_lable,
    datasets : [
        {
            fillColor : "rgba(153,204,153,0.3)",
			strokeColor : "rgba(153,204,0,1)",
			pointColor : "rgba(220,220,220,1)",
            pointStrokeColor : "#fff",
            data : cpu_values
        },
		{
            fillColor : "rgba(255,204,204,0.5)",
			strokeColor : "rgba(204,0,51,1)",
			pointColor : "rgba(220,220,220,1)",
            pointStrokeColor : "#fff",
            data : mem_values
        }
    ]
}





function get_host_data(host_id){
	var post_data = 'host_id=' + host_id;
	$.ajax({
		url: '/monitor/update_index_data/',
        type: 'POST',
        data: post_data,
        dataType: 'json',
        timeout: 1000,
        error: function(){
            alert('Get performace data error!');
        },
        success: function(performace_data){
			cpu_values.shift();
			cpu_values.push(performace_data['cpu_use']);
            //document.getElementById("cpu_percent").innerHTML = performace_data['cpu_use'];
			server_index_chart_data["datasets"][0]["data"] = cpu_values;
			document.getElementById("id_cpu_index").innerHTML = performace_data['cpu_use'];

			mem_values.shift();
			mem_values.push(performace_data['mem_use']);
            //document.getElementById("mem_percent").innerHTML = performace_data['mem_use'];
			server_index_chart_data["datasets"][1]["data"] = mem_values;
			new Chart(index_ctx_server).Line(server_index_chart_data, server_options);
			document.getElementById("id_mem_index").innerHTML = performace_data['mem_use'];
		}
	})
}


function monitor_host(host_id){	
	get_host_data(host_id);
	setTimeout(function(){monitor_host(host_id)}, 1000);
}


