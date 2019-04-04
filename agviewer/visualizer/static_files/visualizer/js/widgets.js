
//Globals
var user_settings = null;




//crsf handler 
$(function() {


    // This function gets cookie with a given name
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');

    /*
    The functions below will create a header with csrftoken
    */

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    function sameOrigin(url) {
        // test that a given url is a same-origin URL
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    }

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
                // Send the token to same-origin, relative URLs only.
                // Send the token only if the method warrants CSRF protection
                // Using the CSRFToken value acquired earlier
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

});

function Widget(id, type, options, data) {
	this.id = id; 
	this.type = type;
	this.options = options;
	this.data = data;

}

function addWidget(){

	widget = new Widget('stat', 'stat1', {'station':''});
	widget.create();  
}

function ajax_request(callback, widget) {
	var request = $.ajax({
		  method: "POST",
		  url: url,
		  data: JSON.stringify(widget), 
		  dataType: 'json'
		}).done(function(data) {
    		callback(data);
  		}).fail(function(msg){
  			alert('failed');
  		});
	};

function render_stat(widget){
	$id = '#'+widget.id+' div.value h1';
	$($id).text(widget.data.calc.value);
};

function makeGraph(data, chart) {

};

function getRandomColor() {
    var letters = '0123456789ABCDEF'.split('');
    var color = '#';
    for (var i = 0; i < 6; i++ ) {
        color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
}

function load_user_settings() {
	function render(settings) {
				user_settings = settings;
		};	

	var request = $.ajax({
		  method: "GET",
		  url: url_get_settings,
		  dataType: 'json'
		}).done(function(data) {
    		render(data);
  		}).fail(function(msg){
  			alert('Failed to load user settings please reload page.');
  	});
		
};


function load_widgets() {
	function render(widgets){
		var widget_lst = Object.keys(widgets);
		for (var i in widget_lst){
			if (widgets[widget_lst[i]]['widget']['type'] != 'stat') {
				render_chart($.parseJSON(widgets[widget_lst[i]].w_json));
			};
		};

	}
	var request = $.ajax({
		  method: "GET",
		  url: url_get_widgets,
		  dataType: 'json'
		}).done(function(data) {
    		render(data);
  		}).fail(function(msg){
  			alert('failed');
  	});
}

load_widgets();
load_user_settings();

function getNonNull(widget) {
	if (widget.data.paw != null){
		return widget.data.paw;
	}else if(widget.data.raw_sensors != null){
		return widget.data.raw_sensors;
	}else if(widget.data.chilling_portions != null){
		return widget.data.chilling_portions;
	}else if(widget.data.chilling_hours != null){
		return widget.data.chilling_hours;
	}else if(widget.data.dew_point != null){
		return widget.data.dew_point;
	}else if(widget.data.evapo != null){
		return widget.data.evapo;
	}
}

function makeData(widget) {
	nonNullData = getNonNull(widget);
	var chartDataArray = [];
	var counter; 
	if (nonNullData.name == 'raw_sensors'){
		counter = nonNullData.value[0].length - 1;
		console.log('counter: '+counter);
	}else{
		counter = nonNullData.value.length - 1;
		console.log('counter: '+counter);
	};
	for (var i = 0; i <= counter; i++) {
		chartData = {};
		if (widget.data.raw_sensors != null && widget.data.raw_sensors.name == nonNullData.name){
			chartData['date'] = nonNullData.value[0][i].date;
			if (widget.data.raw_sensors.value.length > 0){
				for (var j = 0; j <= widget.data.raw_sensors.value.length - 1; j++) {
					chartData[widget.data.raw_sensors.name+'-'+j] = widget.data.raw_sensors.value[j][i].value;	
				};
			 }; 
		}else{
			chartData['date'] = nonNullData.value[i].date;
			chartData[nonNullData.name] = nonNullData.value[i].value;
		}
		if (widget.data.paw != null && widget.data.paw.name != nonNullData.name){
			chartData[widget.data.paw.name] = widget.data.paw.value[i].value;
		}
		if (widget.data.raw_sensors != null && widget.data.raw_sensors.name != nonNullData.name){
			console.log('nonNullData length: '+nonNullData.value.length);
			console.log('raw_sensors length: '+widget.data.raw_sensors.value[0].length);
			if (widget.data.raw_sensors.value.length > 0){
				for (var j = 0; j <= widget.data.raw_sensors.value.length - 1; j++) {
					console.log(widget.data.raw_sensors.value[j][i]);
					console.log(widget.data.raw_sensors.value[j].length);
					chartData[widget.data.raw_sensors.name+'-'+j] = widget.data.raw_sensors.value[j][i].value;	
				};
			};
		}
		if (widget.data.chilling_portions != null && widget.data.chilling_portions.name != nonNullData.name){
			chartData[widget.data.chilling_portions.name] = widget.data.chilling_portions.value[i].value;
		}
		if (widget.data.chilling_hours != null && widget.data.chilling_hours.name != nonNullData.name){
			if (widget.data.chilling_hours.value[i] != null) {
				chartData[widget.data.chilling_hours.name] = widget.data.chilling_hours.value[i].value;
			};
		}
		if (widget.data.dew_point != null && widget.data.dew_point.name != nonNullData.name){
			if (widget.data.dew_point.value[i] != null) {
				chartData[widget.data.dew_point.name] = widget.data.dew_point.value[i].value;
			};
		}
		if (widget.data.evapo != null && widget.data.evapo.name != nonNullData.name){
			if (widget.data.evapo.value[i] != null) {
				chartData[widget.data.evapo.name] = widget.data.evapo.value[i].value;
			};
		}
		chartDataArray.push(chartData);
	};

	return chartDataArray
}

AmCharts.checkEmptyData = function(chart) {
  if (0 == chart.dataProvider.length) {
    // set min/max on the value axis
    var valueAxis = new AmCharts.ValueAxis();
    valueAxis.minimum = 0;
    valueAxis.maximum = 100;
    valueAxis.title = 'new chart';
    chart.addValueAxis(valueAxis);
    // chart.valueAxes[0].minimum = 0;
    // chart.valueAxes[0].maximum = 100;

    // add dummy data point
    var dataPoint = {
      dummyValue: 0
    };
    dataPoint[chart.categoryField] = '';
    chart.dataProvider = [dataPoint];

    // add label
    chart.addLabel(0, '30%', 'No data! please check the following:', 'center', '12');
    chart.addLabel('28%', '35%', '- Data is available for selected range', 'left', '10');
    chart.addLabel('28%', '38%', '- Parameters are correct', 'left', '10');

    // set opacity of the chart div
    chart.chartDiv.style.opacity = 0.5;

    // redraw it
    chart.validateNow();
    return true;
  }
  return false;
}


function render_chart(widget){
	var data
	data = makeData(widget);
	console.log(widget);
	var chart = AmCharts.makeChart("main-panel-chart", {
	    "type": "serial",
	    "theme": "light",
	    "marginRight": 15,
	    "marginLeft": 40,
	    "marginTop" : 10,
	    "marginBottom" : 0,
	    "autoMarginOffset": 20,
	    "dataDateFormat": "YYYY-MM-DD JJ:NN",
	    "categoryField": "date",
	    "precision": 2,

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
	        "borderThickness": 2,
	        "shadowAlpha": 0
	    },
	    // "graphs": [{
	    //     // "id": "g1",
	    //     // "valueField": "value",
	    //     // "balloon":{
	    //     //   "drop":true,
	    //     //   "adjustBorderColor":false,
	    //     //   "color":"#ffffff"
	    //     // },
	    //     "bullet": "round",
	    //     "bulletBorderAlpha": 1,
	    //     "bulletColor": "#FFFFFF",
	    //     "bulletSize": 5,
	    //     "hideBulletsCount": 50,
	    //     "lineThickness": 2,
	    //     "title": "red line",
	    //     "useLineColorForBulletBorder": true,
	    //     "valueField": "value",
	    //     //"balloonText": "<span style='font-size:18px;'>[[value]]</span>"
	    // }],
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
	        "enabled": true,
	        "position": "bottom-right",
	    },
	     "dataProvider": data,
	     "legend": {
	         "useGraphSettings": true,
	         "position": "bottom",
	         "marginTop": 0,
	         "marginBottom": 0 
	  
	       },
	     "guides": [
       		{
       			"fillAlpha": 1,
       			"value": 0,
       			"toValue": 30,
       			"fillColor": "#ff7766",
       			// "lineColor": "#FF0000",
       			// "lineAlpha": "1"
       		},
       		{
       			"fillAlpha": 1,
       			"value": 30,
       			"toValue": 50,
       			"fillColor": "#ffff7f",
       			// "lineColor": "#FFA500",
       			// "lineAlpha": "1"
       		},
       		{
       			"fillAlpha": 1,
       			"value": 50,
       			"toValue": 80,
       			"fillColor": "#66ffb3",
       			// "lineColor": "#008000",
       			// "lineAlpha": "1"
       		},
       		{
       			"fillAlpha": 1,
       			"value": 80,
       			"toValue": 200,
       			"fillColor": "#7f8cff",
       			// "lineColor": "#0000FF",
       			// "lineAlpha": "1"
       		}

        ]

	});
	
	//if empty gracefully handle

	if(AmCharts.checkEmptyData(chart)){
		return
	};
	
	
	chart.dataDateFormat = "YYYY-MM-DD JJ:NN";
	chart.categoryField = "date";

	var categoryAxis = chart.categoryAxis;
	categoryAxis.parseDates = true;
	categoryAxis.minPeriod = "mm";
	min = null;
	max = null;
	position = 'left';
	if (data.length > 0) {
		var prop_lst = Object.keys(data[0]);
		for (var i in prop_lst){
			if (prop_lst[i] != 'date' && prop_lst[i] != 'lineColor') {
				graph = new AmCharts.AmGraph();
				graph.valueField = prop_lst[i];
				graph.showBalloon = true;
				graph.lineColor = "#a9ec49";
				graph.fixedColumnWidth = 5;
				if (widget.data[prop_lst[i]] != null) {
					graph.title = widget.data[prop_lst[i]].title;

					graph.lineColor = widget.data[prop_lst[i]].lineColor;
					graph.balloonText = "[[title]]<br/><b style='font-size: 100%'>[[value]]</b>"
					if (prop_lst[i] == 'paw') {
						min = 0;
						max = 100;
						console.log('its paw');
					};
					chart.valueAxes.push({
						'id':i,
						'title':widget.data[prop_lst[i]].title,
						'position':'left',
						'axisColor': widget.data[prop_lst[i]].lineColor,
						'mininum': min,
						'maximum': max, 
						'strictMinMax': true
					});
					if (prop_lst[i] == 'eto'){
						graph.type = 'column';
					};
					graph.valueAxis= prop_lst[i];
				};
				if (prop_lst[i].split("-")[0] == 'raw_sensors'){
					graph.title = widget.data.raw_sensors.value[prop_lst[i].split('-')[1]][0].name;
					graph.balloonText = "[[title]]<br/><b style='font-size: 100%'>[[value]]</b>"
					factor = chart.valueAxes.length -1;
					graph.lineColor = getRandomColor();
					chart.valueAxes.push({
						'id':prop_lst[i],
						'title':graph.title,
						'position':'left', 
						'gridAlpha': 0, 
						'axisAlpha': 1, 
						'offset': 50*factor,
						'axisColor': graph.lineColor

					});
					graph.type = widget.data.raw_sensors.value[prop_lst[i].split('-')[1]][0].type;
					graph.behindColumns = false;
					if (graph.type == 'column'){
						graph.fillAlphas = 1;
					};
					graph.valueAxis = prop_lst[i];
				};
				
				chart.addGraph(graph);
			};
		};
		chart.validateData();
	};
	$(widget['id']+'-i').removeClass('fa fa-spinner fa-spin');

};

$('#ms-main-sensors').multiSelect({
		afterSelect: function(values){
			$sensors = $.map($("#ms-main-sensors option:selected"), function (el, i) {
         		return $(el).val();
    		 });
			
		},
		afterDeselect: function(values){
			$sensors = $.map($("#ms-main-sensors option:selected"), function (el, i) {
         		return $(el).val();
    		 });
		}

	});


// stat configuration modal 

$('#statmodal').on('show.bs.modal', function (e) {
	$invoker = $(e.relatedTarget);
	$station_id = $('#statmodal select.station').val();
	$station_name = $($invoker).text();
	$db = $('#statmodal select.station option').attr('db');
	$stat_data = $('#statmodal select.sensor').val();
	$station_elem = $('#statmodal select.station');
	$stat_data_elem = $('#statmodal select.sensor');
	$('#statmodal select.station').on('change', function (e) {
		e.stopImmediatePropagation();
		$station_elem = $(this);
		$station_id = $(this).val();
		$station_name = $(this).find('option:selected').text();

	});

	$('#statmodal select.sensor').on('change', function (e) {
		e.stopImmediatePropagation();
		$stat_data_elem = $(this);
		$stat_data = $(this).val();
	});

	$('#statmodal button.submit').on('click', function  (e) {
		e.stopImmediatePropagation();
		$invoker.children().first().text($station_elem.find('option:selected').text());
		$invoker.parent().next().children('p').text($stat_data_elem.find('option:selected').text());
		$db = $station_elem.find('option:selected').attr('db');
		data = {'calc':{'params':{'db':$db, 'station_id':$station_id, 'station_name':$station_name, 'sensor':$stat_data}, 'value':null}}
		widget = new Widget($invoker.parent().parent().attr('id'), 'stat', 'None', data);
		ajax_request(render_stat, widget);

		$('#statmodal').modal('hide');
	});

	return;
});

$sensors = ["Las Mercedes-30", "Las Mercedes-16385", "Las Mercedes-16897", "00203580-1201"];
$main_sensors_check_sensors = true;
$main_sensors_check_paw = true;
$main_sensors_check_cp = true; 
$main_sensors_check_dd = true;
$main_sensors_check_ch = true;
$main_sensors_check_eto = true; 
$main_sensors_check_dp = true; 

$('#main-chart-modal').on('show.bs.modal', function (e){

	$invoker = $(e.relatedTarget);
	$title = $('#main-panel header span.title').text();
	$title_e = $('#main-panel header span.title');
	$ms_sensors = [];
	 
	$('#main-general').find('#inputTitle').on('change', function (e){
		$title = $(this).val();
	});

	if($main_sensors_check_sensors){
		$('#ms-main-sensors').removeAttr('disabled');
	}else{
		$('#ms-main-sensors').attr('disabled', 'disabled');
	};
	if ($main_sensors_check_paw) {
		$('#ms-main-paw').removeAttr('disabled');
	}else{
		$('#ms-main-paw').attr('disabled', 'disabled');
	};
	if ($main_sensors_check_cp) {
		$('#s-main-cp').removeAttr('disabled');
	}else{
		$('#s-main-cp').attr('disabled', 'disabled');
	};
	if ($main_sensors_check_dd) {
		$('#s-main-dd').removeAttr('disabled');
	}else{
		$('#s-main-dd').attr('disabled', 'disabled');
	};
	if ($main_sensors_check_ch) {
		$('#s-main-ch').removeAttr('disabled');
	}else{
		$('#s-main-ch').attr('disabled', 'disabled');
	};
	if ($main_sensors_check_eto) {
		$('#ms-main-eto').removeAttr('disabled');
	}else{
		$('#ms-main-eto').attr('disabled', 'disabled');
	};
	if ($main_sensors_check_dp) {
		$('#ms-main-dp-t').removeAttr('disabled');
		$('#ms-main-dp-rh').removeAttr('disabled');
	}else{
		$('#ms-main-dp-t').attr('disabled', 'disabled');
		$('#ms-main-dp-rh').attr('disabled', 'disabled');
	};

	$('#checkbox-main-sensors').on('change', function(e){
		e.stopImmediatePropagation();
		if($(this).prop('checked')){
			$main_sensors_check_sensors = true;
			$('#ms-main-sensors').removeAttr('disabled');
			$('#ms-main-sensors').multiSelect('refresh');
		}else{
			$main_sensors_check_sensors = false; 
			$('#ms-main-sensors').attr('disabled', 'disabled');
			$('#ms-main-sensors').multiSelect('refresh');
		}
	});

	$('#checkbox-main-paw').on('change', function(e){
		e.stopImmediatePropagation();
		if($(this).prop('checked')){
			$main_sensors_check_paw = true;
			$('#ms-main-paw').removeAttr('disabled');
			$('#main-paw-fc').removeAttr('disabled');
			$('#main-paw-wp').removeAttr('disabled');
			$('#ms-main-paw').multiSelect('refresh');
		}else{
			$main_sensors_check_paw = false; 
			$('#ms-main-paw').attr('disabled', 'disabled');
			$('#main-paw-fc').attr('disabled', 'disabled');
			$('#main-paw-wp').attr('disabled', 'disabled');
			$('#ms-main-paw').multiSelect('refresh');
		}
	});

	$('#checkbox-main-cp').on('change', function(e){
		e.stopImmediatePropagation();
		if($(this).prop('checked')){
			$main_sensors_check_cp = true;
			$('#s-main-cp').removeAttr('disabled');
		}else{
			$main_sensors_check_cp = false; 
			$('#s-main-cp').attr('disabled', 'disabled');
		}
	});

	$('#checkbox-main-dd').on('change', function(e){
		e.stopImmediatePropagation();
		if($(this).prop('checked')){
			$main_sensors_check_dd = true;
			$('#s-main-dd').removeAttr('disabled');
			$('#main-dd-th').removeAttr('disabled');
		}else{
			$main_sensors_check_dd = false; 
			$('#s-main-dd').attr('disabled', 'disabled');
			$('#main-dd-th').attr('disabled', 'disabled');
		}
	});
	$('#checkbox-main-ch').on('change', function(e){
		e.stopImmediatePropagation();
		if($(this).prop('checked')){
			$main_sensors_check_ch = true;
			$('#s-main-ch').removeAttr('disabled');
			$('#main-ch-th').removeAttr('disabled');
		}else{
			$main_sensors_check_ch = false; 
			$('#s-main-ch').attr('disabled', 'disabled');
			$('#main-ch-th').attr('disabled', 'disabled');
		}
	});

	$('#checkbox-main-eto').on('change', function(e){
		e.stopImmediatePropagation();
		if($(this).prop('checked')){
			$main_sensors_check_eto = true;
			$('#ms-main-eto').removeAttr('disabled');
			$('#ms-main-eto').multiSelect('refresh');
		}else{
			$main_sensors_check_eto = false; 
			$('#ms-main-eto').attr('disabled', 'disabled');
			$('#ms-main-eto').multiSelect('refresh');
		}
	});
	$('#checkbox-main-dp').on('change', function(e){
		e.stopImmediatePropagation();
		if($(this).prop('checked')){
			$main_sensors_check_dp = true;
			$('#s-main-dp-t').removeAttr('disabled');
			$('#s-main-dp-rh').removeAttr('disabled');
		}else{
			$main_sensors_check_dp = false; 
			$('#s-main-dp-t').attr('disabled', 'disabled');
			$('#s-main-dp-rh').attr('disabled', 'disabled');
		}
	});

	// raw sensor values
	$main_sensors = $.map($("#ms-main-sensors option:selected"), function (el, i) {
         	return $(el).val();
    	});
	$('#ms-main-sensors').on('change', function(e){
		e.stopImmediatePropagation();
		$main_sensors = $.map($("#ms-main-sensors option:selected"), function (el, i) {
         	return $(el).val();
    	});
	});
	// paw parameters
	$main_paw_sensors = $.map($("#ms-main-paw option:selected"), function (el, i) {
         	return $(el).val();
    	});
	$('#ms-main-paw').on('change', function(e){
		e.stopImmediatePropagation();
		$main_paw_sensors = $.map($("#ms-main-paw option:selected"), function (el, i) {
         	return $(el).val();
    	});
	});
	$main_paw_fc = $('#main-paw-fc').val();
	$('#main-paw-fc').on('change', function(e){
		e.stopImmediatePropagation();
		$main_paw_fc = $('#main-paw-fc').val();
	});
	$main_paw_wp = $('#main-paw-wp').val();
	$('#main-paw-wp').on('change', function(e){
		e.stopImmediatePropagation();
		$main_paw_wp = $('#main-paw-wp').val();
	});

	// Chilling portions parameters
	$main_cp = $("#s-main-cp option:selected").val();
	$('#s-main-cp').on('change', function(e){
		e.stopImmediatePropagation();
		$main_cp = $("#s-main-cp option:selected").val();
	});	

	// Degree days parameters
	$main_dd = $("#s-main-dd option:selected").val();
	$main_dd_th = $('#main-dd-th').val();
	$('#s-main-dd').on('change', function(e){
		e.stopImmediatePropagation();
		$main_dd = $("#s-main-dd option:selected").val();		
	});
	$('#main-dd-th').on('change', function(e){
		e.stopImmediatePropagation();
		$main_dd_th = $('#main-dd-th').val();
	});

	//Chilling hours parameters
	$main_ch = $("#s-main-ch option:selected").val();
	$main_ch_th = $('#main-ch-th').val();
	$('#s-main-ch').on('change', function(e){
		e.stopImmediatePropagation();
		$main_ch = $("#s-main-ch option:selected").val();		
	});
	$('#main-ch-th').on('change', function(e){
		e.stopImmediatePropagation();
		$main_ch_th = $('#main-ch-th').val();
	});	

	//ETO parameters
	$main_eto_t = $("#s-main-eto-t option:selected").val();
	$main_eto_rh = $("#s-main-eto-rh option:selected").val();
	$main_eto_sr = $("#s-main-eto-sr option:selected").val();
	$main_eto_ws = $("#s-main-eto-ws option:selected").val();
	$main_eto_lat = $("#main-eto-lat").val();
	$main_eto_alt = $("#main-eto-alt").val();
 	$('#s-main-eto-t').on('change', function(e){
 		e.stopImmediatePropagation();
		$main_eto_t = $("#s-main-eto-t option:selected").val();		
	});
	$('#s-main-eto-rh').on('change', function(e){
 		e.stopImmediatePropagation();
		$main_eto_rh = $("#s-main-eto-sr option:selected").val();		
	});
	$('#s-main-eto-sr').on('change', function(e){
 		e.stopImmediatePropagation();
		$main_eto_sr = $("#s-main-eto-sr option:selected").val();		
	});
	$('#s-main-eto-ws').on('change', function(e){
 		e.stopImmediatePropagation();
		$main_eto_ws = $("#s-main-eto-ws option:selected").val();		
	});
	$('#s-main-eto-t').on('change', function(e){
 		e.stopImmediatePropagation();
		$main_eto_t = $("#s-main-eto-t option:selected").val();		
	});
	$('#main-eto-lat').on('change', function(e){
 		e.stopImmediatePropagation();
		$main_eto_lat = $("#main-eto-lat").val();		
	});
		$('#main-eto-alt').on('change', function(e){
 		e.stopImmediatePropagation();
		$main_eto_alt = $("#main-eto-alt").val();		
	});
	// Dew Point Parameters

	$main_dp_t = $("#s-main-dp-t option:selected").val();
	$main_dp_rh = $('#s-main-dp-rh').val();
	$('#s-main-dp-t').on('change', function(e){
		e.stopImmediatePropagation();
		$main_dp_t = $("#s-main-dp-t option:selected").val();		
	});
	$('#s-main-dp-rh').on('change', function(e){
		e.stopImmediatePropagation();
		$main_dp_rh = $('#s-main-dp-rh').val();
	});


	$('#main-chart-modal button.submit').on('click', function  (e) {
		// body...
		e.stopImmediatePropagation();
		main_sensors = [];
		raw_sensors = null;
		if ($main_sensors_check_sensors){
			main_sensors = $main_sensors;
			raw_sensors = {'params':{'sensors':main_sensors}, 'value':'', 'name':'raw_sensors', 'title':'Raw Sensor', 'lineColor':'#33ff00', 'unit':'C'};

		};
		main_paw_sensors = [];
		main_paw_fc = '';
		main_paw_wp = '';
		paw = null;
		if ($main_sensors_check_paw) {
			main_paw_sensors = $main_paw_sensors
			main_paw_fc = $main_paw_fc;
			main_paw_wp = $main_paw_wp;
			paw = {'params':{'fc':main_paw_fc, 'wp':main_paw_wp, 'sensors':main_paw_sensors}, 'value':'', 'name':'paw', 'title':'PAW', 'lineColor':'#00fff7', 'unit':''};
		};
		main_cp = '';
		chilling_portions = null;
		if ($main_sensors_check_cp) {
			main_cp = $main_cp;
			chilling_portions = {'params':{'sensors':main_cp}, 'value':'', 'name':'chilling_portions', 'title':'Chilling Portions', 'lineColor':'#33ff00'};
		};

		main_dd = '';
		main_dd_th = '';
		degree_days = null; 
		if ($main_sensors_check_dd) {
			main_dd = $main_dd;
			main_dd_th = $main_dd_th;
			degree_days = {'params': {'sensors':main_dd, 'th':main_dd_th}, 'value':'', 'name':'degree_days', 'title':'Degree Days', 'lineColor':'#33ff00'};
		};
		main_ch = '';
		main_ch_th = '';
		chilling_hours = null;
		if ($main_sensors_check_ch) {
			main_ch = $main_ch;
			main_ch_th = $main_ch_th;
			chilling_hours = {'params': {'sensors':main_ch, 'th':main_ch_th}, 'value':'', 'name':'chilling_hours', 'title':'Chilling Hrs.', 'lineColor':'#33ff00'}
		};

		//eto 
		main_eto_t = '';
		main_eto_rh = '';
		main_eto_sr = '';
		main_eto_ws = '';
		main_eto_lat = '';
		main_eto_alt = '';
		evapo = null;
		if ($main_sensors_check_eto) {
			main_eto_t = $main_eto_t;
			main_eto_rh = $main_eto_rh;
			main_eto_sr = $main_eto_sr;
			main_eto_ws = $main_eto_ws;
			main_eto_lat = $main_eto_lat;
			main_eto_alt = $main_eto_alt;
			evapo = {'params': {
				'sensors':'', 'temp':main_eto_t,
				'rh':main_eto_rh,
				'sr':main_eto_sr,
				'ws':main_eto_ws,
				'lat':main_eto_lat, 
				'alt':main_eto_alt},
			'value':'',
			'name':'evapo',
			'title':'ETO'
		}
		};

		//dew point
		main_dp_t = '';
		main_dp_rh = '';
		dew_point = null;
		if ($main_sensors_check_dp) {
			main_dp_t = $main_dp_t;
			main_dp_rh = $main_dp_rh;
			dew_point = {'params':{'sensors':'', 'rh':main_dp_rh, 'temp': main_dp_t}, 'value':'', 'name':'dew_point', 'title':'Dew Point', 'lineColor': '#0077ff'}
		};


		$id = '#main-panel';
		$type = 'main-chart';
		$options = '';
		$date_from = $('#dt_from').val();
		$date_to = $('#dt_to').val();
		$data = {
			'raw_sensors':raw_sensors,
			'paw':paw,
			'chilling_portions':chilling_portions,
			'degree_days':degree_days,
			'chilling_hours':chilling_hours,
			'evapo':evapo,
			'dew_point':dew_point,
			'calc': {'params':{'sensor':'temp_min'}},
			'range': {'from':$date_from, 'to':$date_to}
		}

		widget = new Widget($id, $type, $options, $data);
		$($id+'-i').addClass('fa fa-spinner fa-spin');
		ajax_request(render_chart, widget);

		$title_e.text($title);

		$('#main-chart-modal').modal('hide');

	});
});
