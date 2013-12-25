
// 各个图的初始化数据
var cpu_values = [];
var cpu_values_x_lable = [];
var mem_values = [];
var mem_values_x_lable = [];
var net_values = [];
var ports = [];
var net_recv_values = [];
var net_send_values = [];
var disk_free;
var disk_used
var isScaleOverride = false;
var data_y = [];



for (var i=0; i<11; i++){
	cpu_values[i] = 0 + "";
    cpu_values_x_lable[i] = "";
}
cpu_values_x_lable[10] = "0s";
cpu_values_x_lable[5] = "5s";
cpu_values_x_lable[0] = "10s";

for (var i=0; i<11; i++){
	mem_values[i] = 0 + "";
    mem_values_x_lable[i] = "";
}

mem_values_x_lable[10] = "0s";
mem_values_x_lable[5] = "5s";
mem_values_x_lable[0] = "10s";

for (var i=0; i<11; i++){
	net_values[i] = "";
	net_recv_values[i] = 0;
	net_send_values[i] = 0;
	
}

net_values[10] = "0s";
net_values[5] = "5s";
net_values[0] = "10s"

var cpu_chart_data = {
    labels : cpu_values_x_lable,
    datasets : [
        {
            fillColor : "rgba(153,204,153,0.3)",
			strokeColor : "rgba(153,204,0,1)",
			pointColor : "rgba(220,220,220,1)",
            pointStrokeColor : "#fff",
            data : cpu_values
        }
    ]
};

var mem_options = {
	bezierCurve : true
}

var mem_chart_data = {
    labels : mem_values_x_lable,
    datasets : [
        {
            fillColor : "rgba(255,204,204,0.3)",
			strokeColor : "rgba(204,0,51,1)",
			pointColor : "rgba(220,220,220,1)",
            pointStrokeColor : "#fff",
            data : mem_values
        }
    ]
}


var net_options = {
	pointDot : true,
	bezierCurve : true,
	scaleOverride : false,
	scaleFontSize: 11
	
}

var net_chart_data = {
    labels : net_values,
    datasets : [
        {
            fillColor : "rgba(204,204,255,0)",
			strokeColor : "rgba(204,0,51,1)",
			pointColor : "rgba(204,0,51,1)",
            pointStrokeColor : "#fff",
            data : net_recv_values
        },
		{
            fillColor : "rgba(153,204,255,0)",
			strokeColor : "rgba(0,153,204,0.5)",
			pointColor : "rgba(0,153,204,0.5)",
            pointStrokeColor : "#fff",
            data : net_send_values
        }
    ]
}


var disk_options = {
    animation : false
}
var disk_chart_data = [
	{
		value: disk_free,
		color: "#99CC66"
	},
	{
		value : disk_used,
		color : "#FF3366"
	}
];


 	var ctx_cpu = document.getElementById('cpu_perf_chart').getContext("2d");
	var ctx_mem = document.getElementById('mem_perf_chart').getContext("2d");
	var ctx_net = document.getElementById('net_perf_chart').getContext("2d");
	//var ctx_disk = document.getElementById('disk_perf_chart').getContext("2d");
	var disk_plot = jQuery.jqplot ('disk_perf_chart', [[['已使用', 0], ['未使用', 1]]], 
					{
						seriesColors: ['#0099FF', '#EEEE00'],
		  				seriesDefaults: {
							renderer: jQuery.jqplot.PieRenderer, 
							rendererOptions: {
			  					showDataLabels: true
							}
		  				}, 
		  				legend: { show: false, placement: 'insideGrid', location: 'e' },
						grid: {
							borderWidth: 0,
							gridLineColor: '#cdcdcd',
							background: 'rgba(255,255,255,0)',
							shadow: false		
						}			
					});



//是否初始化net信息数组的标志位
var flag = true; 
var show_port_num = 0;
var net_info = "";
var net_info_content = ["", ""];
function switch_port(num){
	show_port_num = num;
}



function show_net_content(num){
	document.getElementById("id_net_send").innerHTML = data_process(net_info_content[num][0]) 
													 + data_process_unit(net_info_content[num][0], 'bit');
	//alert(data_y[0]+" "+data_y[1]+" "+data_y[2]);

	document.getElementById("id_net_send_bps").innerHTML = math_round(data_y[num][0]) + data_y[num][2];//net_info_content[num][1];
	document.getElementById("id_net_recv").innerHTML = data_process(net_info_content[num][2])
												 + data_process_unit(net_info_content[num][2], 'bit');
	document.getElementById("id_net_recv_bps").innerHTML = math_round(data_y[num][1]) + data_y[num][2];//net_info_content[num][3];
	document.getElementById("net_unit").innerHTML = data_y[num][2];
}

function show_port(num){
	if(count(ports[num][0]) == 0 && count(ports[num][1]) == 0){
		net_options['scaleOverride'] = true;
	}
	net_chart_data["datasets"][0]["data"] = ports[num][0];
	net_chart_data["datasets"][1]["data"] = ports[num][1];
	new Chart(ctx_net).Line(net_chart_data, net_options);
	show_net_content(num);
}

function change_port(option){
	show_port_num = option;
	$('#ports_info').val(option);
	//$('#ports_info').change();
	$('#ports_info option[value=' + option + ']').attr("selected", "true");
	show_port(option);
	
}
var pre_net_data = [];
function get_performace_data(host_id, vm_id){
    var url;
    var post_data = 'host_id=' + host_id + '&pre_net_data=' + pre_net_data;
    if (vm_id == undefined){
        url = '/monitor/update_performace_data/host/';
    }else{ 
        url = '/monitor/update_performace_data/vm/';
        post_data = post_data + '&vm_id=' + vm_id;
    }
    $.ajax({
        url: url,
        type: 'POST',
        data: post_data,
        dataType: 'json',
		//async: false,
        timeout: 1000,
        success: function(performace_data){
				if(performace_data.result == 1){
					document.getElementById('alert_info').innerHTML = performace_data.error;
					$('#alert_modal').modal('show');
					//alert(performace_data.error)
				}else{
				
				net_options['scaleOverride'] = false;
				cpu_values.shift();
				cpu_values.push(performace_data['cpu_use']);
                document.getElementById("cpu_percent").innerHTML = Math.round(performace_data['cpu_use']*100)/100;
				cpu_chart_data["datasets"][0]["data"] = cpu_values;
				new Chart(ctx_cpu).Line(cpu_chart_data);

				mem_values.shift();
				mem_values.push(performace_data['mem_use']);
                document.getElementById("mem_percent").innerHTML = Math.round(performace_data['mem_use']*100)/100;
				mem_chart_data["datasets"][0]["data"] = mem_values;
				new Chart(ctx_mem).Line(mem_chart_data, mem_options);

                disk_chart_data[0]["value"] = performace_data['disk_use']['free'];
                disk_chart_data[1]["value"] = performace_data['disk_use']['used'];
                //new Chart(ctx_disk).Pie(disk_chart_data, disk_options)

                document.getElementById("disk_use").innerHTML = '<span style="background:#0099FF;"></span>已使用 : ' 
								+ data_process(performace_data['disk_use']['used']) + data_process_unit(performace_data['disk_use']['used'], 'byte');
                document.getElementById("disk_free").innerHTML ='<span style="background:#EEEE00;"></span>未使用 : '
								+ data_process(performace_data['disk_use']['free']) + data_process_unit(performace_data['disk_use']['free'], 'byte');

				disk_plot.series[0].data = [['已使用', data_process(performace_data['disk_use']['used'])],
											['未使用', data_process(performace_data['disk_use']['free'])]];
				disk_plot.replot();

                var port_info_content = "";
                pre_net_data = [];
				var num = 0;

				/*
				net_values.shift();
				if(get_seconds()%2 == 0){
					//alert(get_seconds());
					net_values.push(clock());
				}else{
					net_values.push("");
				}*/
				

                $.each(performace_data.net, function(port, data){
					if(flag){
						ports.push([]);
						data_y.push([]);
						ports[num][0] = net_recv_values.slice(0);
						ports[num][1] = net_send_values.slice(0);
					}
					data_y[num] = data_process_for_Y([data[2], data[3], 'bit'])
					ports[num][0].shift();
					ports[num][0].push(data_y[num][0]);

					ports[num][1].shift();
					ports[num][1].push(data_y[num][1]);

                    pre_net_data.push(data[0]+':'+data[1]);
				
					if(num == show_port_num){
						port_info_content = port_info_content + "<option value="+num+" selected>"+port+"</option>";
					}else{
						port_info_content = port_info_content + "<option value="+num+">"+port+"</option>";
					}
		            
					net_info_content[num] = [data[0], data[2], data[1], data[3]];

					num++;
                });

				flag = false;
                document.getElementById("ports_info").innerHTML = port_info_content;
				//alert(pre_net_data)
				//show_port(show_port_num);
				change_port(show_port_num);
				}
				
            }
     });
}

function init(host_id, vm_id){
	get_performace_data(host_id, vm_id);
	setTimeout(function(){init(host_id, vm_id)}, 1000);
}







