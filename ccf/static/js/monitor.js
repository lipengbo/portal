
// 各个图的初始化数据
var cpu_values = [];
var mem_values = [];
var net_values = [];
var ports = [];
var net_recv_values = [];
var net_send_values = [];
var br_values = [];
var port_recv_values = [];
var port_send_values = [];
var disk_free;
var disk_used

for (var i=0; i<150; i++){
    cpu_values[i] = 0 + "";
}

for (var i=0; i<50; i++){
	mem_values[i] = 0 + "";
}

for (var i=0; i<10; i++){
	net_values[i] = "";
	net_recv_values[i] = 0;
	net_send_values[i] = 0;
	br_values[i] = "";
	port_send_values[i] = 0;
	port_recv_values[i] = 0;
}

var cpu_chart_data = {
    labels : cpu_values,
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
    labels : mem_values,
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

 	var ctx_cpu = document.getElementById('cpu_perf_chart').getContext("2d");
    var cpu_chart = new Chart(ctx_cpu);
    

	var ctx_mem = document.getElementById('mem_perf_chart').getContext("2d");
    var mem_chart = new Chart(ctx_mem);
    

	var ctx_net = document.getElementById('net_perf_chart').getContext("2d");
    var net_chart = new Chart(ctx_net);

	var ctx_disk = document.getElementById('disk_perf_chart').getContext("2d");
	//new Chart(ctx_disk).Doughnut(disk_chart_data);   

	var ctx_port = document.getElementById('port_perf_chart').getContext("2d");

    var port_chart = new Chart(ctx_port);

function switch_port(num){
	alert(ports[num][0]);
	net_chart_data["datasets"][0]["data"] = ports[num][0];
	net_chart_data["datasets"][1]["data"] = ports[num][1];
	new Chart(ctx_net).Line(net_chart_data, net_options);
}

function get_performace_data(host_id, vm_id){
    var url;
    if (vm_id == undefined){
        url = '/slice/update_performace_data/host/' + host_id +'/';
    }else{
        url = '/slice/update_performace_data/vm/' + host_id + '/' + vm_id + '/';
    }
    $.ajax({
        url: url,
        type: 'GET',
        dataType: 'json',
        timeout: 1000,
        error: function(){
                alert('Get performace data error!');
            },
        success: function(performace_data){
				cpu_values.shift();
				cpu_values.push(performace_data['cpu_use']);
				cpu_chart_data["datasets"][0]["data"] = cpu_values;
				new Chart(ctx_cpu).Line(cpu_chart_data);

				mem_values.shift();
				mem_values.push(performace_data['mem_use']);
				mem_chart_data["datasets"][0]["data"] = mem_values;
				new Chart(ctx_mem).Line(mem_chart_data, mem_options);
                disk_chart_data[0]["value"] = performace_data['disk_use']['free']
                disk_chart_data[1]["value"] = performace_data['disk_use']['used']
                new Chart(ctx_disk).Doughnut(disk_chart_data, disk_options)
                /*
				net_recv_values.shift();
				net_recv_values.push(performace_data['net_recv_data']);
		
				net_send_values.shift();
				net_send_values.push(performace_data['net_send_data']);
				net_chart_data["datasets"][0]["data"] = net_recv_values;
				net_chart_data["datasets"][1]["data"] = net_send_values;
				new Chart(ctx_net).Line(net_chart_data, net_options);
                */

                var net_info_content = "";
				
				var num = 0;
				
                $.each(performace_data.net, function(port, data){
					send_data[num].shift();
					send_data[num].push(data[0]);

					recv_data[num].shift();
					recv_data[num].push(data[1]);

					ports[num][0] = send_data;
					ports[num][1] = recv_data;

                    net_info_content = net_info_content + "<button id='id_port' onclick='switch_port(" + num + ")'>" + port + "</button>【send: "+ data[0] +", recv:"+ data[1] +"】<br/>";
					num++;
                });
                document.getElementById("net_info").innerHTML = net_info_content;

                //默认显示第一个网卡的信息
				net_chart_data["datasets"][0]["data"] = ports[1][0];
				net_chart_data["datasets"][1]["data"] = ports[1][1];
				new Chart(ctx_net).Line(net_chart_data, net_options);


            }
     });
}

function init(host_id, vm_id){
	get_performace_data(host_id, vm_id);
	setTimeout(function(){init(host_id, vm_id)}, 1000);
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

function get_br_info(host_id){
	 
    $.ajax({
        url: '/slice/monitor/ovs/' + host_id + '/',
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
					args = host_id + ",\"" +br +"\",\"" + port +"\"";
                    context = context + "<li><a href='#' onclick='get_port_info(" + args + ")'>"+ port + "</a></li>";

                }
                context = context + "</ul></li>";
            }

            document.getElementById('br_info').innerHTML = context;
        }
    });
}

