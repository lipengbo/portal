
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



for (var i=0; i<50; i++){
	cpu_values[i] = 0 + "";
    cpu_values_x_lable[i] = "";
}

for (var i=0; i<50; i++){
	mem_values[i] = 0 + "";
    mem_values_x_lable[i] = "";
}

for (var i=0; i<10; i++){
	net_values[i] = "";
	net_recv_values[i] = 0;
	net_send_values[i] = 0;
}

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
	scaleOverride : false
	//scaleStartValue : 0,
	//scaleSteps : 20,
	//scaleStepWidth : 20,
	
}

var net_chart_data = {
    labels : net_values,
    datasets : [
        {
            fillColor : "rgba(153,204,255,0)",
			strokeColor : "rgba(0,153,204,1)",
			pointColor : "rgba(0,153,204,1)",
            pointStrokeColor : "#fff",
            data : net_recv_values
        },
		{
            fillColor : "rgba(204,204,255,0)",
			strokeColor : "rgba(204,0,51,0.8)",
			pointColor : "rgba(204,0,51,0.8)",
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
	var ctx_disk = document.getElementById('disk_perf_chart').getContext("2d");






function data_process(data){
    unit = 'byte'
    data = data/8/1024 //byte
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
    return Math.round(data) + unit
}

//是否初始化net信息数组的标志位
var flag = true; 
var show_port_num = 0;
var net_info = "";
var net_info_content = ["", ""];
function switch_port(num){
	show_port_num = num;
}



function show_net_content(num){
	document.getElementById("id_net_send").innerHTML = data_process(net_info_content[num][0]);
	document.getElementById("id_net_send_bps").innerHTML = net_info_content[num][1];
	document.getElementById("id_net_recv").innerHTML = data_process(net_info_content[num][2]);
	document.getElementById("id_net_recv_bps").innerHTML = net_info_content[num][3];
}

function show_port(num){
	net_chart_data["datasets"][0]["data"] = ports[num][0];
	net_chart_data["datasets"][1]["data"] = ports[num][1];
	new Chart(ctx_net).Line(net_chart_data, net_options);
	//document.getElementById("net_info").innerHTML = net_info_content[num];
	show_net_content(num);
}

function change_port(option){
	show_port_num = option;
	show_port(option);
	//alert(net_info_content[arg.value]);
	
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
    //alert('['+pre_net_data.toString() + ']');
    $.ajax({
        url: url,
        type: 'POST',
        data: post_data,
        dataType: 'json',
        timeout: 1000,
        error: function(){
                //alert('Get performace data error!');
            },
        success: function(performace_data){
				cpu_values.shift();
				cpu_values.push(performace_data['cpu_use']);
                document.getElementById("cpu_percent").innerHTML = performace_data['cpu_use'];
				cpu_chart_data["datasets"][0]["data"] = cpu_values;
				new Chart(ctx_cpu).Line(cpu_chart_data);

				mem_values.shift();
				mem_values.push(performace_data['mem_use']);
                document.getElementById("mem_percent").innerHTML = performace_data['mem_use'];
				mem_chart_data["datasets"][0]["data"] = mem_values;
				new Chart(ctx_mem).Line(mem_chart_data, mem_options);

                disk_chart_data[0]["value"] = performace_data['disk_use']['free'];
                disk_chart_data[1]["value"] = performace_data['disk_use']['used'];
                new Chart(ctx_disk).Doughnut(disk_chart_data, disk_options)

                document.getElementById("disk_use").innerHTML = '<span style="background:#ff3366;"></span>已使用 : ' 
								+ performace_data['disk_use']['used'] + " MB";
                document.getElementById("disk_free").innerHTML ='<span style="background:#99cc66;"></span>未使用 : '
								+ performace_data['disk_use']['free'] + " MB";

                var port_info_content = "";//"<option selected>请选择网卡</option>";
				//var net_info_content = [];
                pre_net_data = [];
				var num = 0;
                $.each(performace_data.net, function(port, data){
					if(flag){
						ports.push([]);
						ports[num][0] = net_recv_values.slice(0);
						ports[num][1] = net_send_values.slice(0);
					}
					
					ports[num][0].shift();
					ports[num][0].push(data[2]);

					ports[num][1].shift();
					ports[num][1].push(data[3]);

                    pre_net_data.push(data[0]+':'+data[1]);
				
					
                    port_info_content = port_info_content + "<option value="+num+">"+port+"</option>"
					net_info_content[num] = [data[0], data[2], data[1], data[3]];

					num++;
                });
				flag = false;
                document.getElementById("ports_info").innerHTML = port_info_content;
				//alert(pre_net_data)
				//show_port(show_port_num);
				change_port(show_port_num);

				
            }
     });
}

function init(host_id, vm_id){
	get_performace_data(host_id, vm_id);
	setTimeout(function(){init(host_id, vm_id)}, 1000);
}







