/**
 * Grid theme for Highcharts JS
 * @author Torstein Hønsi
 */

Highcharts.theme = {
	colors: ['#3366ff', '#50B432', '#ED561B', '#DDDF00', '#24CBE5', '#64E572', '#FF9655', '#FFF263', '#6AF9C4'],
	chart: {
		backgroundColor: {
			linearGradient: { x1: 0, y1: 0, x2: 1, y2: 1 },
			stops: [
				[0, '#ccc'],
				[1, '#ccc']
			]
		},
		borderWidth: 0,
		plotBackgroundColor: '#ccc',
		plotShadow: false,
		plotBorderWidth: 1
	},
	title: {
		style: {
			color: '#fff',
			font: 'bold 18px "Microsoft YaHei", Verdana, sans-serif'
		}
	},
	subtitle: {
		style: {
			color: '#fff',
			font: 'bold 12px "Trebuchet MS", Verdana, sans-serif'
		}
	},
	xAxis: {
		gridLineWidth: 1,
		lineColor: '#dfdfdf',
		tickColor: '#dfdfdf',
		labels: {
			style: {
				color: '#666',
				font: '11px Trebuchet MS, Verdana, sans-serif'
			}
		},
		title: {
			style: {
				color: '#666',
				fontWeight: 'bold',
				fontSize: '12px',
				fontFamily: 'Trebuchet MS, Verdana, sans-serif'

			}
		}
	},
	yAxis: {
		minorTickInterval: 'auto',
		lineColor: '#dfdfdf',
		lineWidth: 1,
		tickWidth: 1,
		tickColor: '#dfdfdf',
		labels: {
			style: {
				color: '#666',
				font: '11px Trebuchet MS, Verdana, sans-serif'
			}
		},
		title: {
			style: {
				color: '#666',
				fontWeight: 'bold',
				fontSize: '12px',
				fontFamily: 'Trebuchet MS, Verdana, sans-serif'
			}
		}
	},
	legend: {
		itemStyle: {
			font: '9pt Trebuchet MS, Verdana, sans-serif',
			color: '#666'

		},
		itemHoverStyle: {
			color: '#666'
		},
		itemHiddenStyle: {
			color: '#666'
		}
	},
	labels: {
		style: {
			color: '#666'
		}
	},

	navigation: {
		buttonOptions: {
			theme: {
				stroke: '#666'
			}
		}
	}
};

// Apply the theme
var highchartsOptions = Highcharts.setOptions(Highcharts.theme);
