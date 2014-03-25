// JavaScript Document
$(function () {
        return;
        //alert("in");
        var target = $("#target").text();
        var type = $("#type").text();
        var stype = $("#stype").text();
        var total_num = 0;
        var show_dates = [];
        var show_nums = [];
        var title = "";
        var name = "";
        var coler = ['#2f7ed8', '#0d233a', '#8bbc21'];
        var check_url = "/slice/get_count_show/?target="+target+"&type="+type+"&total_num="+total_num+"&stype="+stype;
        $.ajax({
            type: "GET",
            url: check_url,
            dataType: "json",
            cache: false,
            async: false,  
            success: function(data) {
                if (data.result == 1)
                 {
                    show_dates = data.show_dates;
                    show_nums = data.show_nums;
                 } 
                 else
                 {
                    //show_dates = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30];
                    //show_nums = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0];
                 }
            }
        });
        //show_dates = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30];
        //show_nums = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,100000,101555];
        if(target == "project"){
            name = "项目";
        }else{
            name = "虚网";
        }
        var showtype = "新增";
        if(stype == 0){
            showtype = "新增";
        }else if(stype == 1){
            showtype = "删除失败";
        }else{
            showtype = "删除";
        }
        var date=new Date;
        var year=date.getFullYear().toString();
        var month=(date.getMonth()+1).toString();
        var titshow = '<small>{point.key}</small><br>'
        if(type == "year"){
            total_num = 5;
            coler = ['#8bbc21', '#0d233a', '#2f7ed8'];
            if(target == "project"){
                title = show_dates[0]+"-"+show_dates[9]+"每年新增项目数";
            }else{
                title = show_dates[0]+"-"+show_dates[9]+"每年"+showtype+"虚网数";
            }
        }else if(type == "month"){
            total_num = 12;
            coler = ['#0d233a', '#8bbc21', '#2f7ed8'];
            if(target == "project"){
                title = year + "年每月新增项目数";
            }else{
                title = year + "年每月"+showtype+"虚网数";
            }
        }else{
            titshow = '<small>{point.key}日</small><br>'
            total_num = 15;
            coler = ['#2f7ed8', '#0d233a', '#8bbc21'];
            if(target == "project"){
                title = year + "年" + month + "月每日新增项目数";
            }else{
                title = year + "年" + month + "月每日"+showtype+"虚网数";
            }
        }
        $("div#chart_title").empty();
        str = title;
        $("div#chart_title").append(str);
        
        $('#container').highcharts({
        chart: {
            type: 'line',
            marginRight: 25,
            marginBottom: 25
        },
        colors: coler,
        title: {
            text: '',
            x: -20 //center
        },
        subtitle: {
            text: '',
            x: -20
        },
        xAxis: {
            categories: show_dates,
        },
        yAxis: {
            title: {
                text: name + '数(个)'
            },
            plotLines: [{
                value: 0,
                width: 1,
                color: ''
            }]
        },
        tooltip: {
            valueSuffix: '个'
        },
        legend: {
            layout: 'vertical',
            align: 'right',
            verticalAlign: 'top',
            x: -10,
            y: 100,
            borderWidth: 0
        },
        series: [{
            name: name,
            data: show_nums,
        }]
    });
        
});

function fu() {	
//highcharts	
	$('#container').highcharts({
		chart: {
			type: 'line',
			marginRight: 25,
			marginBottom: 25
		},
		title: {
			text: '',
			x: -20 //center
		},
		subtitle: {
			text: '',
			x: -20
		},
		xAxis: {
			categories: ['1月', '2月', '3月', '4月', '5月', '6月',
				'7月', '8月', '9月', '10月', '11月', '12月']
		},
		yAxis: {
			title: {
				text: '虚网数（个）'
			},
			plotLines: [{
				value: 0,
				width: 1,
				color: ''
			}]
		},
		tooltip: {
			valueSuffix: '个'
		},
		legend: {
			layout: 'vertical',
			align: 'right',
			verticalAlign: 'top',
			x: -10,
			y: 100,
			borderWidth: 0
		},
		series: [{
			name: '项目数',
			data: [2.0, 7.0, 9.0, 2.0, 5.0, 3.0, 2.0, 4.0, 8.0, 1.0, 1.0, 9.0]
		}]
	});
}