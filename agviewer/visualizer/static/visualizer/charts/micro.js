

var ajax_request1 = new XMLHttpRequest();

ajax_request1.open("GET", "http://172.16.68.10:8000/ambient_temp/", true);
ajax_request1.send();

AmCharts.ready(ajax_request1.onreadystatechange = function () {

			if (ajax_request1.readyState == 4) {
			    // line chart, with a bullet at the end
			    var chart = new AmCharts.AmSerialChart();
			    chart.dataProvider = JSON.parse(ajax_request1.responseText);
			    chart.categoryField = "year";
			    chart.autoMargins = false;
			    chart.marginLeft = 0;
			    chart.marginRight = 5;
			    chart.marginTop = 0;
			    chart.marginBottom = 0;
			    chart.dataDateFormat = "YYYY-MM-DD JJ:NN:SS";

			    var graph = new AmCharts.AmGraph();
			    graph.valueField = "value";
			    graph.bulletField = "bullet";
			    graph.showBalloon = false;
			    graph.lineColor = "#a9ec49";
			    chart.addGraph(graph);

			    var valueAxis = new AmCharts.ValueAxis();
			    valueAxis.gridAlpha = 0;
			    valueAxis.axisAlpha = 0;
			    chart.addValueAxis(valueAxis);

			    var categoryAxis = chart.categoryAxis;
			    categoryAxis.parseDate = true;
			    categoryAxis.minPeriod = "mm";
			    categoryAxis.gridAlpha = 0;
			    categoryAxis.axisAlpha = 0;
			    categoryAxis.startOnAxis = true;
			    chart.write("line1");
			}});
			    // line chart, with different line color below zero
var ajax_request2 = new XMLHttpRequest(); 

ajax_request2.open("GET", "http://172.16.68.10:8000/get_record/?station_name=0110282B&sensor=soil_temp_avg", true);
ajax_request2.send();

AmCharts.ready(ajax_request2.onreadystatechange = function (){
			if (ajax_request2.readyState == 4) {
			    var chart = new AmCharts.AmSerialChart();
			    chart.dataProvider = JSON.parse(ajax_request2.responseText);
			    chart.categoryField = "year";
			    chart.autoMargins = false;
			    chart.marginLeft = 0;
			    chart.marginRight = 5;
			    chart.marginTop = 0;
			    chart.marginBottom = 0;
			    chart.dataDateFormat = "YYYY-MM-DD JJ:NN:SS";


			    graph = new AmCharts.AmGraph();
			    graph.valueField = "value";
			    graph.showBalloon = false;
			    graph.lineColor = "#ffbf63";
			    graph.negativeLineColor = "#289eaf";
			    chart.addGraph(graph);

			    valueAxis = new AmCharts.ValueAxis();
			    valueAxis.gridAlpha = 0;
			    valueAxis.axisAlpha = 0;
			    chart.addValueAxis(valueAxis);

			    categoryAxis = chart.categoryAxis;
			    categoryAxis.parseDate = true;
			    categoryAxis.minPeriod = "mm";
			    categoryAxis.gridAlpha = 0;
			    categoryAxis.axisAlpha = 0;
			    categoryAxis.startOnAxis = true;
		

			    // using guide to show 0 grid
			    var guide = new AmCharts.Guide();
			    guide.value = 0;
			    guide.lineAlpha = 0.1;
			    valueAxis.addGuide(guide);
			    chart.write("line2");
			}
});
			    // line chart, with different line color below zero

var ajax_request3 = new XMLHttpRequest(); 

ajax_request3.open("GET", "http://172.16.68.10:8000/get_record/?station_name=0110282B&sensor=last_battery", true);
ajax_request3.send();

AmCharts.ready(ajax_request3.onreadystatechange = function (){
			if (ajax_request3.readyState == 4) {

			    chart = new AmCharts.AmSerialChart();
			    chart.dataProvider = JSON.parse(ajax_request3.responseText);
			    chart.categoryField = "year";
			    chart.autoMargins = false;
			    chart.marginLeft = 0;
			    chart.marginRight = 5;
			    chart.marginTop = 0;
			    chart.marginBottom = 0;
			   // chart.dataDateFormat = "YYYY-MM-DD JJ:NN:SS";


			    graph = new AmCharts.AmGraph();
			    graph.valueField = "value";
			    graph.showBalloon = false;
			    graph.lineColor = "#23b3ea";
			    //graph.negativeLineColor = "#289eaf";
			    chart.addGraph(graph);

			    valueAxis = new AmCharts.ValueAxis();
			    valueAxis.gridAlpha = 0;
			    valueAxis.axisAlpha = 0;
			    chart.addValueAxis(valueAxis);

			    categoryAxis = chart.categoryAxis;
			    categoryAxis.gridAlpha = 0;
			    categoryAxis.axisAlpha = 0;
			    categoryAxis.startOnAxis = true;
			    categoryAxis.minPeriod = "mm";


			    // using guide to show 0 grid
			    var guide = new AmCharts.Guide();
			    guide.value = 0;
			    guide.lineAlpha = 0.1;
			    valueAxis.addGuide(guide);
			    chart.write("line3");
			}
});

			    // line chart, with a bullet at the end
var ajax_request4 = new XMLHttpRequest(); 

ajax_request4.open("GET", "http://172.16.68.10:8000/get_record/?station_name=0110282B&sensor=solar_panel", true);
ajax_request4.send();

AmCharts.ready(ajax_request4.onreadystatechange = function (){
			if (ajax_request4.readyState == 4) {

			    var chart = new AmCharts.AmSerialChart();
			    chart.dataProvider = JSON.parse(ajax_request4.responseText);
			    chart.categoryField = "day";
			    chart.autoMargins = false;
			    chart.marginLeft = 0;
			    chart.marginRight = 5;
			    chart.marginTop = 0;
			    chart.marginBottom = 0;

			    var graph = new AmCharts.AmGraph();
			    graph.valueField = "value";
			    //graph.bulletField = "bullet";
			    graph.showBalloon = false;
			    graph.lineColor = "#e55ea2";
			    chart.addGraph(graph);

			    var valueAxis = new AmCharts.ValueAxis();
			    valueAxis.gridAlpha = 0;
			    valueAxis.axisAlpha = 0;
			    chart.addValueAxis(valueAxis);

			    var categoryAxis = chart.categoryAxis;
			    categoryAxis.gridAlpha = 0;
			    categoryAxis.axisAlpha = 0;
			    categoryAxis.startOnAxis = true;
			    chart.write("line4");

			    // line chart, with a bullet at the end
			    var chart = new AmCharts.AmSerialChart();
			    chart.dataProvider = [{
			        "day": 1,
			            "value": 128
			    }, {
			        "day": 2,
			            "value": 127
			    }, {
			        "day": 3,
			            "value": 126
			    }, {
			        "day": 4,
			            "value": 124
			    }, {
			        "day": 5,
			            "value": 126
			    }, {
			        "day": 6,
			            "value": 125
			    }, {
			        "day": 7,
			            "value": 124
			    }, {
			        "day": 8,
			            "value": 123
			    }, {
			        "day": 9,
			            "value": 120
			    }, {
			        "day": 10,
			            "value": 115,
			        bullet: "round"
			    }];
			    chart.categoryField = "day";
			    chart.autoMargins = false;
			    chart.marginLeft = 0;
			    chart.marginRight = 5;
			    chart.marginTop = 0;
			    chart.marginBottom = 0;

			    var graph = new AmCharts.AmGraph();
			    graph.valueField = "value";
			    //graph.bulletField = "bullet";
			    graph.showBalloon = false;
			    graph.lineColor = "#522575";
			    chart.addGraph(graph);

			    var valueAxis = new AmCharts.ValueAxis();
			    valueAxis.gridAlpha = 0;
			    valueAxis.axisAlpha = 0;
			    chart.addValueAxis(valueAxis);

			    var categoryAxis = chart.categoryAxis;
			    categoryAxis.gridAlpha = 0;
			    categoryAxis.axisAlpha = 0;
			    categoryAxis.startOnAxis = true;
			    chart.write("line5");

			     // line chart, with a bullet at the end
			    var chart = new AmCharts.AmSerialChart();
			    chart.dataProvider = [{
			        "day": 1,
			            "value": 110
			    }, {
			        "day": 2,
			            "value": 115
			    }, {
			        "day": 3,
			            "value": 120
			    }, {
			        "day": 4,
			            "value": 119
			    }, {
			        "day": 5,
			            "value": 121
			    }, {
			        "day": 6,
			            "value": 123
			    }, {
			        "day": 7,
			            "value": 124
			    }, {
			        "day": 8,
			            "value": 122
			    }, {
			        "day": 9,
			            "value": 125
			    }, {
			        "day": 10,
			            "value": 126,
			        bullet: "round"
			    }];
			    chart.categoryField = "day";
			    chart.autoMargins = false;
			    chart.marginLeft = 0;
			    chart.marginRight = 5;
			    chart.marginTop = 0;
			    chart.marginBottom = 0;

			    var graph = new AmCharts.AmGraph();
			    graph.valueField = "value";
			    //graph.bulletField = "bullet";
			    graph.showBalloon = false;
			    graph.lineColor = "#c3b0f9";
			    chart.addGraph(graph);

			    var valueAxis = new AmCharts.ValueAxis();
			    valueAxis.gridAlpha = 0;
			    valueAxis.axisAlpha = 0;
			    chart.addValueAxis(valueAxis);

			    var categoryAxis = chart.categoryAxis;
			    categoryAxis.gridAlpha = 0;
			    categoryAxis.axisAlpha = 0;
			    categoryAxis.startOnAxis = true;
			    chart.write("line6");
			}

});

var ajax_request5 = new XMLHttpRequest();

ajax_request5.open("GET", "http://172.16.68.10:8000/ambient_temp/", true);
ajax_request5.send();

var chart_ex;

AmCharts.ready(ajax_request5.onreadystatechange =function () {

    if (ajax_request5.readyState == 4) {

        	data = JSON.parse(ajax_request5.responseText);

        	// test data
        	data1 = [{"lineColor": "#7ca7e3", "value": 10, "year": "2016-02-07 05:45:00"},
        		{"lineColor": "#7ca7e3", "value": 11.2, "year": "2016-02-07 06:00:00"},
        		{"lineColor": "#e37ca7", "value": 12, "year": "2016-02-07 06:15:00"},
        		{"lineColor": "#e37ca7", "value": 12.2, "year": "2016-02-07 06:30:00"},
        		{"lineColor": "#e37ca7", "value": 12.5, "year": "2016-02-07 06:45:00"},
        		{"lineColor": "#a7e37c", "value": 13.2, "year": "2016-02-07 07:00:00"},
        		{"lineColor": "#a7e37c", "value": 14.2, "year": "2016-02-07 07:15:00"},
        		{"lineColor": "#7ca7e3", "value": 10, "year": "2016-02-07 07:30:00"},
        		{"lineColor": "#7ca7e3", "value": 11, "year": "2016-02-07 07:45:00"},
        		{"lineColor": "#a7e37c", "value": 14, "year": "2016-02-07 08:15:00"}];

			var chart = AmCharts.makeChart("chartdiv", {
			    "type": "serial",
			    "theme": "light",
			    "marginRight": 40,
			    "marginLeft": 40,
			    "autoMarginOffset": 20,
			    "dataDateFormat": "YYYY-MM-DD JJ:NN:SS",
			    "categoryField": "year",

			    "categoryAxis": {
			    	"parseDates": true,
			    	"minPeriod": "mm", 
			    	"axisAlpha": 0,
			    	"startOnAxis": true
			    },
			    "valueAxes": [{
			        "id": "v1",
			        "axisAlpha": 0,
			        "position": "left",
			        "ignoreAxisWidth":true
			    }],
			    "balloon": {
			        "borderThickness": 1,
			        "shadowAlpha": 0
			    },
			    "graphs": [{
			        "id": "g1",
			        "valueField": "value",
			        "balloon":{
			          "drop":true,
			          "adjustBorderColor":false,
			          "color":"#ffffff"
			        },
			        "bullet": "round",
			        "bulletBorderAlpha": 1,
			        "bulletColor": "#FFFFFF",
			        "bulletSize": 5,
			        "hideBulletsCount": 50,
			        "lineThickness": 2,
			        "title": "red line",
			        "useLineColorForBulletBorder": true,
			        "valueField": "value",
			        "lineColorField": "lineColor"
			        //"balloonText": "<span style='font-size:18px;'>[[value]]</span>"
			    }],
			    "chartScrollbar": {
			        "graph": "g1",
			        "oppositeAxis":false,
			        "offset":30,
			        "scrollbarHeight": 80,
			        "backgroundAlpha": 0,
			        "selectedBackgroundAlpha": 0.1,
			        "selectedBackgroundColor": "#888888",
			        "graphFillAlpha": 0,
			        "graphLineAlpha": 0.5,
			        "selectedGraphFillAlpha": 0,
			        "selectedGraphLineAlpha": 1,
			        "autoGridCount":true,
			        "color":"#AAAAAA"
			    },
			    "chartCursor": {
			        "pan": true,
			        "valueLineEnabled": true,
			        "valueLineBalloonEnabled": true,
			        "cursorAlpha":1,
			        "cursorColor":"#258cbb",
			        "limitToGraph":"g1",
			        "valueLineAlpha":0.2
			    },
			    "valueScrollbar":{
			      "oppositeAxis":false,
			      "offset":50,
			      "scrollbarHeight":10
			    },
			    "categoryValue": "value",
			    "categoryAxis": {
			        "parseDates": true,
			        "dashLength": 1,
			        "minorGridEnabled": true
			    },
			    "export": {
			        "enabled": true
			    },
			     "dataProvider": data,
			     "export": {
                    "enabled": true
                }

			});
			
			chart.dataDateFormat = "YYYY-MM-DD JJ:NN:SS";
			chart.categoryField = "year";

			var categoryAxis = chart.categoryAxis;
			categoryAxis.parseDates = true;
			categoryAxis.minPeriod = "mm";

			graph = new AmCharts.AmGraph();
			graph.valueField = "value1";
			graph.showBalloon = false;
			graph.lineColor = "#a9ec49";
			graph.lineColorField = "lineColor";
			    //graph.negativeLineColor = "#289eaf";
			chart.addGraph(graph);

			chart.validateData();

			chart_ex = chart;

			// function zoomChart() {
			//     chart.zoomToIndexes(chart.dataProvider.length - 40, chart.dataProvider.length - 1);
			// }

			//chart.addListener("rendered", zoomChart);

			//zoomChart();

			
		}
	});

function downloadPNG() {
  chart_ex.export.capture({}, function() {
    this.toPNG( {}, function( data ) {
      this.download( data, "image/png", "amCharts.png" );
    } );
  });
}



var options = [];
console.log('micro js');

$('.sensor-menu a').on('click', function(event) {
	console.log('inside check js');

  var $target = $(event.currentTarget),
    val = $target.attr('data-value'),
    $inp = $target.find('input'),
    idx;

  if ((idx = options.indexOf(val)) > -1) {
    options.splice(idx, 1);
    setTimeout(function() {
      $inp.prop('checked', false)
    }, 0);
  } else {
    options.push(val);
    setTimeout(function() {
      $inp.prop('checked', true)
    }, 0);
  }

  $(event.target).blur();

  console.log(options);
  return false;
});