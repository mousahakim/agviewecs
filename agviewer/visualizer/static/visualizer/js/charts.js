

// test data 
data = [];


	var chart = AmCharts.makeChart("main-panel-chart", {
			    "type": "serial",
			    "theme": "light",
			    "marginRight": 15,
			    "marginLeft": 20,
			    "marginTop" : 5,
			    "marginBottom" : 0,
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
			        "scrollbarHeight": 20,
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
			    // "valueScrollbar":{
			    //   "oppositeAxis":false,
			    //   "offset":50,
			    //   "scrollbarHeight":10
			    // },
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
			// graph = new AmCharts.AmGraph();
			// graph.valueField = "value1";
			// graph.showBalloon = false;
			// graph.lineColor = "#a9ec49";
			    //graph.negativeLineColor = "#289eaf";
			// chart.addGraph(graph);
			chart.validateData();

			chart.addListener("rendered", zoomChart);

zoomChart();

function zoomChart() {
    chart.zoomToIndexes(chart.dataProvider.length - 40, chart.dataProvider.length - 1);
}