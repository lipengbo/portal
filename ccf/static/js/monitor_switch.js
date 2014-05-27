var test_data = [];

$(document).ready(function(){
    $("#switch_port").change(function(){
        show_chart($(this).attr('switch_name'));    
    });
    test_data.push({name:'接收', color: '#99CCFF', data: gen_data()});
    test_data.push({name:'发送', color: '#99CC66', data: gen_data()});
});


function show_chart(switch_name){
    //ajax获取数据
    draw_highchart();
   //alert(test_data);
}

function draw_highchart(){
	$('#container').highcharts({
            chart: {
                //type: 'spline',
                animation: Highcharts.svg, // don't animate in old IE
                //marginRight: 10,
                events: {
                    load: function() {
                        // set up the updating of the chart each second
                        var series1 = this.series[0];
                        var series2 = this.series[1];
                        setInterval(function() {
                            var x = (new Date()).getTime(), // current time
                                y = Math.random(),
                                z = Math.random();
                                series1.addPoint([x, y], true, true);
                                series2.addPoint([x, z], true, true);
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
