var ports_series_data = [];
var pre_port_data;
var switch_id;
var chart;
$(function(){
	Highcharts.setOptions({
		            global: {
		                useUTC: false
		            }
				});

});

function update_port_info(pre_port_data){
	setInterval(function() {
		$.ajax({
			url: '/monitor/get_switch_port_info/'+switch_id+'/',
			type: 'POST',
			data: 'pre_port_data='+pre_port_data,
			dataType: 'json',
			success: function(ports_data){
				if(ports_data.result == 1){
					document.getElementById('alert_info').innerHTML = ports_data.error;//"获取网桥信息失败， 请检查agent是否启动并设置了ovs服务！";
					$('#alert_modal').modal('show');
					return;
				}
				var i=0;
				var content = '';
				$.each(ports_data, function(port, data){
					content = content + '<tr>';
					var recv_total = data_process_chart(data[0], 'bit');
					var send_total = data_process_chart(data[1], 'bit');
					var recv_bps = data_process_chart(data[2], 'bit');
					var send_bps = data_process_chart(data[3], 'bit');
					content = content + '<td>' + port + '</td>'
									  + '<td>' + recv_total[0] + recv_total[1] +'</td>' 
									  + '<td>' + send_total[0] + send_total[1] +'</td>'
									  + '<td>' + recv_bps[0] + recv_bps[1] +'/s</td>'
									  + '<td>' + send_bps[0] + send_bps[1] +'/s</td></tr>';
					var x = (new Date()).getTime();
					chart.series[i].addPoint([x, data[2]], true, true);
					chart.series[++i].addPoint([x, data[3]], true, true); 
					i++;
				});
				$("#switch_port_info").find('tbody').empty();
				$("#switch_port_info").find('tbody').append(content);
			}
		});
    }, 1000);
}

function draw_highchart(){
	$('#container').highcharts({
            		chart: {
                		type: 'spline',
                		animation: Highcharts.svg, // don't animate in old IE
                		marginRight: 10,
                		events: {
                    		load: function() {
								chart = this;
                        		update_port_info(pre_port_data);
                    }
                }
            },
            title: {
                text: '网络流量监控(bit/s)'
            },
            xAxis: {
                type: 'datetime',
                tickPixelInterval: 150
            },
            yAxis: {
                title: {
                    text: ''
                },
                plotLines: [{
                    value: 0,
                    width: 1,
                    color: '#808080'
                }]
            },
            tooltip: {
                formatter: function() {
                        return '<b>'+ this.series.name +':</b>'+
                        Highcharts.numberFormat(data_process(this.y), 0) + data_process_unit(this.y, 'bit') ;
                }
            },
            legend: {
                enabled: true
            },
            exporting: {
                enabled: false
            },
			plotOptions: {
				series: {
					marker: {
						enabled: true
					}
				}
			},
            series: ports_series_data
        });
			
}

function Initdata(id){
			//根据端口的数量设置series初始化数据
			
			$.ajax({
				url: "/monitor/get_switch_port_info/"+id+"/",
				type: 'GET',
				dataType: 'json',
				success: function(ports_data){
					var init_data = [], time = (new Date()).getTime(), i;
                    for (i = -19; i <= 0; i++) {
	                    init_data.push({ x: time + i * 1000, y: 0});
					}
					$.each(ports_data, function(port, data){
						pre_port_data = JSON.stringify(ports_data);
						ports_series_data.push({
							name: port+'-接收',
							data: init_data
						});
						ports_series_data.push({
							name: port+'-发送',
							data: init_data
						});
					});
					draw_highchart();
					switch_id = id;
				}
			});
				
		}

