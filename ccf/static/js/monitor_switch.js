var test_data;
var clock = null;
var switch_id;
$(function(){
	Highcharts.setOptions({
		            global: {
		                useUTC: false
		            }
				});

});
$(document).ready(function(){
    var switch_name = $("#switch_port").attr('switch_name');
    switch_id = $("#switch_port").attr('switch_id');
    //alert(switch_id);
    $("#switch_port").change(function(){
        if($(this).val() == -1){
            if(clock){
                clock = clearInterval(clock); 
            }
            $(".none_tip").html('当前无监控数据，请选择端口。');
            $('#container').highcharts().destroy();
        }else{
            $(".none_tip").html('');
            show_chart(switch_name); 
        }       
           
    });
    $.ajax({
        url: '/monitor/sflow_list_ports/'+ switch_id +'/',
        type: 'GET',
        dataType: 'json',
        async: false,
        success:function(ports){
            if(ports.data == 1){
                $("#monitor_info").html('交换机连接出错！');
                $(".alert_monitor").show(); 
            }else{
                var context = '<option value="-1">------</option>';
                $.each(ports, function(key, value){
                    if(value[0] == 'up'){
                        var option = '<option value="'+ key +'">eth-0-'+key+'</option>';
                        context += option;
                    }
                });
                $("#switch_port").html(context);
            }
        }
    });
    
});


function show_chart(switch_name){
    //清除之前的调用
    if(clock){
        clock = clearInterval(clock); 
    }
       
    //ajax获取数据
    test_data = [];
    test_data.push({name:'接收', color: '#99CCFF', data: gen_data()});
    test_data.push({name:'发送', color: '#99CC66', data: gen_data()});
    draw_highchart();
    
     
    $(".port_mean").html('<span class="port_green"><i class="glyphicon glyphicon-stop"></i>发送流量</span><span class="port_blue"><i class="glyphicon glyphicon-stop"></i>接收流量</span>');
    $(".port_fill").html('<span class="call_out">单位：Kbps</span>');
   //alert(test_data);
}

function draw_highchart(){
	$('#container').highcharts({
            chart: {
                type: 'spline',
                animation: Highcharts.svg, // don't animate in old IE
                marginRight: 1,
                events: {
                    load: function() {
                        // set up the updating of the chart each second
                        var series1 = this.series[0];
                        //series1.data[19].color ='#99CCFF';
                        var series2 = this.series[1];
                        //series2.color = '#ff0000';
                        clock = setInterval(function() {
                            var x = (new Date()).getTime(); // current time
                            var in_bps = 0, out_bps = 0;
                            $.ajax({
                                url: '/monitor/sflow_get_bps/'+ switch_id +'/'+$("#switch_port").val()+'/',
                                type: 'GET',
                                dataType: 'json',
                                async: false,
                                cache: false,
                                success:function(data){
                                    if(data.result == 0){
                                        in_bps = data.in_bps/1024;
                                        out_bps = data.out_bps/1024;
                                    }else{
                                        if(clock){
                                            clock = clearInterval(clock); 
                                        }
                                        $("#monitor_info").html('交换机连接出错！');
                                        $(".alert_monitor").show();    
                                    }
                                }
                            });
                                series1.addPoint([x, in_bps], true, true);
                                series2.addPoint([x, out_bps], true, true);
                        }, 3000);
                    }
                }
            },
            title: {
                text: ''
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
                    color: '#FF6666'
                }]
            },
            tooltip: {
                formatter: function() {
                        return '<b>'+ this.series.name +':</b>'+
                        Highcharts.numberFormat(this.y);
                }
            },
            legend:  {
                layout: 'vertical',
                align: 'left',
                borderWidth: 0
            },
            exporting: {
                enabled: false
            },
			plotOptions: {
				series: {
					marker: {
						enabled: false
					}
				}
			},
            series: test_data
        });
			
}

function gen_data(){
    var t_data = [];
    var time = (new Date()).getTime();
    var i;
    for (i = -190; i <= 0; i++) {
        t_data.push({
            x: time + i * 3000,
            y: 0
        });
    }
    return t_data;
}
