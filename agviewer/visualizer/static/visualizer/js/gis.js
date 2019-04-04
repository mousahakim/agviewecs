//setup django csrftoken cookie for ajax
//get crsf token cookie
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
//setup ajax crsf header
function csrfSafeMethod(method) {
// these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

//globals
var lastInvokerWidget;

function getID() {
	id = getRandomColor();
	widget_lst = Object.keys(all_widgets);
	if (id.split('#')[1] in widget_lst) {
		return getID();
	}else{
		return id.split('#')[1];
	};
}

function getFileList(){
	$.ajax({
      method: "GET",
      url: 'file-list',
      dataType: 'json'
    }).done(function(fileList) {
        //update file select
        $('select#file-select').empty();
        $.each(fileList, function (index, file){
        	$('select#file-select').append('<option value="'+file.fid+'" url="'+file.url+'">'+file.name+'</option>');
        });
    }).fail(function(msg){
        alert('Failed to retreive files');
    });
}

function importFeatures(){
	var selectedFiles = $.map($('select#file-select option:selected'), function (el, i) {
        return $(el).attr("url");
    });
    if (selectedFiles.length > 1){
    	alert('Please select one file at a time.');
    	return;
    }
	//check for existing vector layers
	var vectorLayer = new ol.layer.Vector({
		source: new ol.source.Vector({
			format: new ol.format.KML({
				extractStyles:false
			}),
			url: selectedFiles[0]
		})
	});

	var map = lastInvokerWidget.data('map');

	map.addLayer(vectorLayer);

	var targetElement = $(map.getTargetElement());

	var parser = new ol.format.GeoJSON();

	vectorLayer.once('change', function (){

		var features = vectorLayer.getSource().getFeatures();
		
		features.forEach(function(feature, index, array){

			var GeoJSONFeature = parser.writeFeatureObject(feature);
			//add loading icon on import feature button
			$('#btn-import-features i').toggleClass('fa-map-marker', false);
			$('#btn-import-features i').toggleClass('fa-spin fa-spinner', true);
			$.ajax({
				method: "POST",
				url: 'save-feature',
				dataType: 'json',
				data: JSON.stringify({
					widget: targetElement.attr('id'),
					feature: GeoJSONFeature
				})
		    }).done(function(response) {

				//remove loading icon on import feature button
		    	$('#btn-import-features i').toggleClass('fa-spin fa-spinner', false);
		    	$('#btn-import-features i').toggleClass('fa-map-marker', true);

		    	//set feature id
		    	feature.setId(response.fid);

		    }).fail(function(msg){
		    	$('#btn-import-features i').toggleClass('fa-spin fa-spinner', false);
		    	$('#btn-import-features i').toggleClass('fa-map-marker', true);
		        alert('Failed to save features to database.');
		    });
		});
		//load features from database
    	loadMapFeatures(targetElement);
	});
}

var downloadMapAsPNG = function(){
	// console.log(lastInvokerWidget.attr('id'));
	var canvas = lastInvokerWidget.find('canvas').get(0);
	canvas.toBlob(function(blob){
		saveAs(blob, 'map.png');
	});
};
var downloadMapAsGJSON = function(){
	var map = lastInvokerWidget.data('map');
	var layers = map.getLayers();
	var vectorLayer;

	layers.forEach(function (layer) {
		
		if (layer instanceof ol.layer.Vector)
			vectorLayer = layer;
	});

	var features = vectorLayer.getSource().getFeatures();
	if (features.length < 1){
		alert('Map contains no features that can be exported as KML');
		return;
	}

	var parser = new ol.format.GeoJSON();

	var geojson = parser.writeFeatures(features);

	// console.log(geojson);

	var blob = new Blob([geojson], {type: "text/json;charset=utf-8"});

	saveAs(blob, 'map-features.geojson');
};
var downloadMapAsKML = function(){
	var map = lastInvokerWidget.data('map');
	var layers = map.getLayers();
	var vectorLayer;

	layers.forEach(function (layer) {
		
		if (layer instanceof ol.layer.Vector)
			vectorLayer = layer;
	});

	var features = vectorLayer.getSource().getFeatures();
	if (features.length < 1){
		alert('Map contains no features that can be exported as KML');
		return;
	}

	var parser = new ol.format.KML({
		writeStyles: false, 
		extractStyles:true

	});

	// var kml = '<?xml version="1.0" encoding="UTF-8"?>\n' + parser.writeFeaturesNode(features);
	var kml = parser.writeFeaturesNode(features);
	var kmlStyle = '<Style id="PolyStyle"><LineStyle><width>1.5</width></LineStyle><PolyStyle><color>7d0000ff</color></PolyStyle></Style>';

	$(kml).find('Document').prepend(kmlStyle);

	$(kml).find('styleUrl').replaceWith('<styleUrl>#PolyStyle</styleUrl>');
	// console.log(kml);

	var kmlString = (new XMLSerializer()).serializeToString(kml);
	// console.log(typeof kmlString);
	// console.log(kmlString);

	var blob = new Blob (['<?xml version="1.0" encoding="UTF-8"?>\n' + kmlString], {type: "text/xml;charset=utf-8"});
	saveAs(blob, 'map-features.kml');

};

function drawPolygon(){
	var map = lastInvokerWidget.data('map');

	var interactions = map.getInteractions();

	interactions.forEach(function(interaction, index, array){
		if(interaction instanceof ol.interaction.Draw)
			map.removeInteraction(interaction);
	});

	var source = new ol.source.Vector();

	var vectorLayer = new ol.layer.Vector({
		source: source,
		layerType: 'Drawing'
	});

	map.addLayer(vectorLayer);

	var draw = new ol.interaction.Draw({
		source: source, 
		type: 'Polygon'
	});

	map.addInteraction(draw);
}

function drawSquare(){
	var map = lastInvokerWidget.data('map');

	var interactions = map.getInteractions();

	interactions.forEach(function(interaction, index, array){
		if(interaction instanceof ol.interaction.Draw)
			map.removeInteraction(interaction);
	});

	var source = new ol.source.Vector();

	var vectorLayer = new ol.layer.Vector({
		source: source,
		layerType: 'Drawing'
	});

	map.addLayer(vectorLayer);

	var geomFunction = ol.interaction.Draw.createBox();

	var draw = new ol.interaction.Draw({
		source: source, 
		type: 'Circle',
		geometryFunction: geomFunction
	});

	map.addInteraction(draw);
}

function drawCircle(){
	var map = lastInvokerWidget.data('map');

	var interactions = map.getInteractions();

	interactions.forEach(function(interaction, index, array){
		if(interaction instanceof ol.interaction.Draw)
			map.removeInteraction(interaction);
	});

	var source = new ol.source.Vector();

	var vectorLayer = new ol.layer.Vector({
		source: source,
		layerType: 'Drawing'
	});

	map.addLayer(vectorLayer);

	var draw = new ol.interaction.Draw({
		source: source, 
		type: 'Circle',
	});

	map.addInteraction(draw);
}

function saveDrawings(){
	var map = lastInvokerWidget.data('map');

	var interactions = map.getInteractions();

	interactions.forEach(function(interaction, index, array){
		if(interaction instanceof ol.interaction.Draw)
			map.removeInteraction(interaction);
	});

	var layers = map.getLayers();

	var parser = new ol.format.GeoJSON();

	var mapWidgetId = map.getTarget();

	layers.forEach(function(layer, index, array){

		if(layer instanceof ol.layer.Vector){

			var features = layer.getSource().getFeatures();

			features.forEach(function(feature, i, a){

				if(feature.getId() == undefined){

					var GeoJSONFeature = parser.writeFeatureObject(feature);
					console.log(feature.getGeometry().getType());
					if(feature.getGeometry().getType() == 'Circle'){

						var circularPolygon = ol.geom.Polygon.fromCircle(feature.getGeometry());

						var geoJSONCircularPolygon = parser.writeGeometryObject(circularPolygon);

						GeoJSONFeature.properties = {name: 'Feature Circle ' + ol.proj.toLonLat(feature.getGeometry().getFirstCoordinate())};

						GeoJSONFeature.geometry = geoJSONCircularPolygon;

					}else{
						GeoJSONFeature.properties = {name: 'Feature Polygon ' + ol.proj.toLonLat(feature.getGeometry().getFirstCoordinate())};
					}
					
					console.log(GeoJSONFeature);

					$.ajax({
						method: "POST",
						url: 'save-feature',
						dataType: 'json',
						data: JSON.stringify({
							widget: mapWidgetId,
							feature: GeoJSONFeature
						})
				    }).done(function(response) {

				    	//set feature id
				    	feature.setId(response.fid);

				    }).fail(function(msg){

				        alert('Failed to save features to database.');

				    });

				}

			});

		}

	})

}

function clearDrawings(){

	var map = lastInvokerWidget.data('map');

	var interactions = map.getInteractions();

	interactions.forEach(function(interaction, index, array){
		if(interaction instanceof ol.interaction.Draw){
			map.removeInteraction(interaction);
		}
	});

	var layers = map.getLayers();
	var drawingLayers = [];
	layers.forEach(function(layer, index, array){
		if(layer.get('layerType') == 'Drawing')
			drawingLayers.push(layer);
	});

	for(var i = 0; i < drawingLayers.length; i++)
		map.removeLayer(drawingLayers[i]);
}

function createMapWidget(mapWidgetID, options){
	var newWidget = false;
	if (typeof mapWidgetID == 'undefined'){
		var mapWidgetID = getID();
		var html = '<div class="col-lg-6">\
			<section id="main-panel-" class="panel main-panel">\
				<header class="panel-heading">\
					<span class="title">New GIS widget &nbsp;<i id="map-widget-progress" class="fa fa-spin fa-cog"></i></span>\
					<span class="tools pull-right">\
						<a href="javascript:;" class="fa fa-chevron-down"></a>\
						<a href="#GISModal" data-toggle="modal" class="fa fa-wrench"></a>\
						<a href="javascript:;" class="fa fa-times" id="map-widget-delete-button"></a>\
					</span>\
				</header>\
				<div class="panel-body gis-panel" id="gis-panel-'+mapWidgetID+'">\
					<div id="'+mapWidgetID+'" class="gis-container chart-container">\
						<div class="nosupport">Loading map tiles please wait. <i class="fa fa-spin fa-spinner"></i> </div>\
					</div>\
					<div id="pieChart-'+mapWidgetID+'" class="map-pie-chart"></div>\
					<div id="map-popup-container" style="display: hidden;">\
                    </div>\
				</div>\
			</section>\
		</div>';
		$('.chart-row').append(html);
		options = {
			center: [0,0],
			zoom: 2,
			tile_source: 'XYZ',
			tile_url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}',
	        tile_attribution: '',
		};
		newWidget = true;
	}

	//create map tile source
	var tile_source;
	switch (options.tile_source){
		case 'ArcGIS':
			tile_source = new ol.source.XYZ({
				attributions: [new ol.Attribution({
					html: ''
				})],
				url: options.tile_url
			});
			break;
		case 'XYZ':
			tile_source = new ol.source.XYZ({
				attributions: options.tile_attribution,
				url: options.tile_url
			});
			break;
		case 'BingMapsAerial+Labels':
			tile_source = new ol.source.BingMaps({
				key: 'AnST1eDSeRY_VRrb86ud4B1Y_iS1OnD2NMs7EKYN8JvtRNoMt5ZjGWGsE8bNkTlJ', 
				imagerySet: 'AerialWithLabels'
			});
			break;
		default:
			tile_source = new ol.source.XYZ({
				attributions: options.tile_attribution,
				url: options.tile_url
			});
			break;
	}
	//create controls
	var DownloadMap = function(opt_options){

		var options = opt_options || {};

		var button = document.createElement('button');
		button.innerHTML = '<i class="fa fa-download"></i>';
		button.title = 'Download map as';

		var this_ = this;

		button.addEventListener('click', function(){
			lastInvokerWidget = $(this.closest('div.gis-container'));
			$('#map-dialog').data('kendoDialog').open();
		}, false);
		button.addEventListener('touchstart', function(){
			lastInvokerWidget = $(this.closest('div.gis-container'));
			$('#map-dialog').data('kendoDialog').open();
		}, false);

		var element = document.createElement('div');
		element.className = 'download-map ol-unselectable ol-control';
		element.appendChild(button);

		ol.control.Control.call(this, {
			element: element, 
			target: options.target
		});

	};
	ol.inherits(DownloadMap, ol.control.Control);
	var DrawPolygon = function(opt_options){

		var options = opt_options || {};

		var button = document.createElement('button');
		button.title = 'Draw polygon';
		button.innerHTML = '<img src="/static/visualizer/img/drawpolygon.png">';

		var this_ = this;

		button.addEventListener('click', function(){
			lastInvokerWidget = $(this.closest('div.gis-container'));
			drawPolygon();
		}, false);
		button.addEventListener('touchstart', function(){
			lastInvokerWidget = $(this.closest('div.gis-container'));
			drawPolygon();
		}, false);

		var element = document.createElement('div');
		element.className = 'draw-polygon ol-unselectable ol-control';
		element.appendChild(button);

		ol.control.Control.call(this, {
			element: element, 
			target: options.target
		});
	};
	ol.inherits(DrawPolygon, ol.control.Control);

	var DrawSquare = function(opt_options){

		var options = opt_options || {};

		var button = document.createElement('button');
		button.innerHTML = '<img src="/static/visualizer/img/drawsquare.png">';
		button.title = 'Draw rectangle';

		var this_ = this;

		button.addEventListener('click', function(){
			lastInvokerWidget = $(this.closest('div.gis-container'));
			drawSquare();
		}, false);
		button.addEventListener('touchstart', function(){
			lastInvokerWidget = $(this.closest('div.gis-container'));
			drawSquare();
		}, false);

		var element = document.createElement('div');
		element.className = 'draw-square ol-unselectable ol-control';
		element.appendChild(button);

		ol.control.Control.call(this, {
			element: element, 
			target: options.target
		});
	};
	ol.inherits(DrawSquare, ol.control.Control);

	var DrawCircle = function(opt_options){

		var options = opt_options || {};

		var button = document.createElement('button');
		button.innerHTML = '<img src="/static/visualizer/img/drawcircle.png">';
		button.title = 'Draw circle';

		var this_ = this;

		button.addEventListener('click', function(){
			lastInvokerWidget = $(this.closest('div.gis-container'));
			drawCircle();
		}, false);
		button.addEventListener('touchstart', function(){
			lastInvokerWidget = $(this.closest('div.gis-container'));
			drawCircle();
		}, false);

		var element = document.createElement('div');
		element.className = 'draw-circle ol-unselectable ol-control';
		element.appendChild(button);

		ol.control.Control.call(this, {
			element: element, 
			target: options.target
		});
	};
	ol.inherits(DrawCircle, ol.control.Control);

	var ClearDrawings = function(opt_options){

		var options = opt_options || {};

		var button = document.createElement('button');
		button.innerHTML = '<img src="/static/visualizer/img/erasedrawing.png">';
		button.title = 'Clear drawings';
		var this_ = this;

		button.addEventListener('click', function(){
			lastInvokerWidget = $(this.closest('div.gis-container'));
			clearDrawings();
		}, false);
		button.addEventListener('touchstart', function(){
			lastInvokerWidget = $(this.closest('div.gis-container'));
			clearDrawings();
		}, false);

		var element = document.createElement('div');
		element.className = 'clear-drawings ol-unselectable ol-control';
		element.appendChild(button);

		ol.control.Control.call(this, {
			element: element, 
			target: options.target
		});
	};
	ol.inherits(ClearDrawings, ol.control.Control);

	var SaveDrawings = function(opt_options){

		var options = opt_options || {};

		var button = document.createElement('button');
		button.innerHTML = '<img src="/static/visualizer/img/savedrawing.png">';
		button.title = 'Save drawings';
		var this_ = this;

		button.addEventListener('click', function(){
			lastInvokerWidget = $(this.closest('div.gis-container'));
			saveDrawings();
		}, false);
		button.addEventListener('touchstart', function(){
			lastInvokerWidget = $(this.closest('div.gis-container'));
			saveDrawings();
		}, false);

		var element = document.createElement('div');
		element.className = 'save-drawings ol-unselectable ol-control';
		element.appendChild(button);

		ol.control.Control.call(this, {
			element: element, 
			target: options.target
		});
	};
	ol.inherits(SaveDrawings, ol.control.Control);

	var map = new ol.Map({
        target: mapWidgetID,
        layers: [
            new ol.layer.Tile({
                source: tile_source
            }),
        ],
        controls: [
            //Define the default controls
            new ol.control.Zoom(),
            new ol.control.Rotate(),
            new ol.control.Attribution(),
            new ol.control.FullScreen({
            	source: 'gis-panel-'+mapWidgetID
            }),
            //Define some new controls
            new ol.control.ZoomSlider(),
            new DownloadMap(),
            new DrawPolygon(),
            new DrawSquare(),
            new DrawCircle(),
            new ClearDrawings(),
            new SaveDrawings(),
            // new ol.control.MousePosition({
            // 	coordinateFormat: function (coordinates){
            // 		var coordX = coordinates[0].toFixed(3);
            // 		var coordY = coordinates[1].toFixed(3);
            // 		return coordX + ', ' + coordY;
            // 	}
            // }),
            // new ol.control.ScaleLine({
            // 	units: 'degrees'
            // }),
            // new ol.control.OverviewMap()
        ],
        interactions: ol.interaction.defaults({
        	mouseWheelZoom: false, 
        	dragPan: false
        }).extend([
            new ol.interaction.Select({
                layers: [new ol.layer.Vector()]
            })
        ]),
        view: new ol.View({
            center: ol.proj.fromLonLat(options.center),
            zoom: options.zoom
        }), 
    });
    //change text size on zoom change
    // map.getView().on('propertychange', function (e) {

    // 	if(e.key == 'resolution'){
    // 		var layers = map.getLayers();

    // 		layers.forEach(function (layer, index, array) {

    // 			if(layer instanceof ol.layer.Vector){

    // 				var features = layer.getSource().getFeatures();
    // 				var fontSize = 10;
    // 				if (window.matchMedia("(min-width: 300px)").matches) {
				// 		/* the viewport is at least 400 pixels wide */
				// 		fontSize = 10;
				// 	} else if (window.matchMedia("(min-width: 370px)").matches) {
				// 		fontSize = 12;
				// 	} else if (window.matchMedia("(min-width: 400px)").matches) {
				// 		fontSize = 14;
				// 	} else if (window.matchMedia("(min-width: 700px)").matches) {
				// 		fontSize = 16;
				// 	} else if (window.matchMedia("(min-width: 1000px)").matches) {
				// 		fontSize = 18;
				// 	} else if (window.matchMedia("(min-width: 1400px)").matches) {
				// 		fontSize = 20;
				// 	}
				// 	console.log('font: ',fontSize);
    // 				features.forEach(function (feature, index, array) {
    // 					if(feature.getStyle() != null)
    // 						feature.getStyle().getText().setFont(fontSize + 'px Hind Madurai');
    // 				});
    // 			}
    // 		});
    // 	}
    // });
    //bring popover to front when feature is click on
    // map.on('click', function(e){
    // 	map.forEachFeatureAtPixel(e.pixel, function(feature, layer){
    // 		if (feature == null)
    // 			return;
    // 		var overlays = map.getOverlays();
    // 		overlays.forEach(function(overlay, index, array) {
    // 			var position = overlay.getPosition();
    // 			if(feature.getGeometry().intersectsCoordinate(position)){
    // 				//decrease z-index of all popovers with 'popover-front' class
    // 				$('.popover').removeClass("popover-front");
    // 				//increase z-index of clicked feature's popover.
    // 				//popover element is generated next to overlay's element.
    // 				$(overlay.getElement()).next('div.popover').addClass("popover-front");
    // 			}
    // 		})
    // 	});
    // });
    //associate map with element
    $('#'+mapWidgetID).data('map',map);
    //create pie chart
    var chart = AmCharts.makeChart("pieChart-"+mapWidgetID,{
		"type"    : "pie",
		"titleField"  : "range",
		"valueField"  : "value",
		"colorField"	: "color",
		"labelText"	: "[[percents]]%",
		"balloonText" : "[[title]]: [[value]]",
		"outlineAlpha": 0.5,
		"outlineThickness": 2,
		"labelRadius": -10,
		"radius": '40%',
		"dataProvider"  : [], 
		// "responsive": {
	 //    	"enabled": true
	 //  	}
	});
	//associate chart with element
	$('#pieChart-'+mapWidgetID).data('pieChart', chart);
    //save new widget
    if (newWidget){
    	options['wid'] = mapWidgetID;
    	$('#')
    	$.ajax({
    		method: 'POST', 
    		url: 'save-map-widget',
    		dataType: 'json',
    		data: JSON.stringify(options)
    	}).done(function(response){
    		$('#'+mapWidgetID).closest('section.main-panel').find('i#map-widget-progress').toggleClass('fa-spin fa-cog', false);
    	}).fail(function(response){
    		alert('Failed to save GIS widget to database. Please referesh page and try again.');
    	});
    }
}

function loadMapWidgets(){
	$.ajax({
		method: 'POST', 
		url: 'get-map-widgets',
		dataType: 'json',
	}).done(function(response){
		$.each(response, function(index, widget) {
			createMapWidget(widget.wid, widget);
			var widgetElement = $('#'+widget.wid);
			loadMapFeatures(widgetElement);
		});
	}).fail(function(response){
		alert('Failed to save GIS widget to database. Please referesh page and try again.');
	});
}

function loadMapFeatures(mapWidget){
	var mapWidgetID = mapWidget.attr('id');
	$.ajax({
		method: 'POST', 
		url: 'get-feature-list',
		dataType: 'json',
		data: JSON.stringify({'wid': mapWidgetID})
	}).done(function(response){
		//if no features return immediately
		if (response.features.length < 1)
			return;
		var map = mapWidget.data('map');
		var parser = new ol.format.GeoJSON();
		var mapLayers = map.getLayers();
		var features = parser.readFeatures(response);
		var existingVectorLayer = false;
		mapLayers.forEach(function (layer, index, array) {
			if(layer instanceof ol.layer.Vector){
				var source = layer.getSource();
				features.forEach(function (feature, index, array) {
					var existingFeature;
					existingFeature = source.getFeatureById(feature.getId());
					if(existingFeature == null)
						source.addFeature(feature);

				})
				existingVectorLayer = true;
			}
		})
		if(!existingVectorLayer){
			var vectorLayer = new ol.layer.Vector({
				style: styleMap(map),
				source: new ol.source.Vector({
					format: new ol.format.GeoJSON(),
					features: features
				})
			});
			map.addLayer(vectorLayer);	
		}

		features.forEach(function(feature, index, array){
			//asynchronously load and render stats for each feature
			loadMapFeatureStats(feature.getId(), mapWidget);
		});
	}).fail(function(response){
		alert('Failed to load feature list.');
	});
}

function loadMapFeatureStats(featureId, mapWidget){
	$.ajax({
		method: 'POST', 
		url: 'get-feature-stats',
		dataType: 'json',
		data: JSON.stringify({'fid': featureId})
	}).done(function(response){

		var map = mapWidget.data('map');
		var mapLayers = map.getLayers();
		var feature, source;
		mapLayers.forEach(function (layer, index, array) {
			if (layer instanceof ol.layer.Vector){
				source = layer.getSource();
				feature = source.getFeatureById(featureId);
			}
		});
		//remove paw stat from polygon
		// if(!response.paw.hasOwnProperty('fsid'))
		// 	feature.setStyle(null);
		//feature not found
		if (feature == null)
			return;
		// don't create popup for non-polygon features
		if (feature.getGeometry().getType() != 'Polygon')
			return;
		//style polygon according to paw value
		var style, color;
		// , featureStyle = feature.getStyle();
		//get chart object
		var pieChart = $('#pieChart-'+mapWidget.attr('id')).data('pieChart');
		var dataProvider = pieChart.dataProvider;
		var featureArea = feature.getGeometry().getArea();

		if (response.paw.value != null){
			if (response.paw.value <= 30){
				color = [254,180,186,0.9]
				var rangeExists = false;
				for (var i in dataProvider){
					if (dataProvider[i].range == 'Red range'){
						if (dataProvider[i].features.indexOf(featureId) < 0){
							dataProvider[i].value += featureArea;
							dataProvider[i].features.push(featureId);
						}
						rangeExists = true
					} 
				}
				if (rangeExists){
					pieChart.dataProvider = dataProvider;
				}else{
					pieChart.dataProvider.push({
						range: "Red range",
		    			value: featureArea,
		    			color: "#feb4ba",
		    			features: [featureId]
					});
				}
			}else if(response.paw.value > 30 && response.paw.value <= 70){
				color = [255,255,187,0.9]
				var rangeExists = false;
				for (var i in dataProvider){
					if (dataProvider[i].range == 'Yellow range'){
						if (dataProvider[i].features.indexOf(featureId) < 0){
							dataProvider[i].value += featureArea;
							dataProvider[i].features.push(featureId);
						}
						rangeExists = true
					} 
				}
				if (rangeExists){
					pieChart.dataProvider = dataProvider;
				}else{
					pieChart.dataProvider.push({
						range: "Yellow range",
		    			value: featureArea,
		    			color: "#ffffbb",
		    			features: [featureId]
					});
				}
			}else if(response.paw.value > 70 && response.paw.value <= 100){
				color = [186,255,202,0.9]
				var rangeExists = false;
				for (var i in dataProvider){
					if (dataProvider[i].range == 'Green range'){
						if (dataProvider[i].features.indexOf(featureId) < 0){
							dataProvider[i].value += featureArea;
							dataProvider[i].features.push(featureId);
						}
						rangeExists = true
					} 
				}
				if (rangeExists){
					pieChart.dataProvider = dataProvider;
				}else{
					pieChart.dataProvider.push({
						range: "Green range",
		    			value: featureArea,
		    			color: "#baffca",
		    			features: [featureId]
					});
				}
			}else{
				color = [109,192,255,0.9]
				var rangeExists = false;
				for (var i in dataProvider){
					if (dataProvider[i].range == 'Blue range'){
						if (dataProvider[i].features.indexOf(featureId) < 0){
							dataProvider[i].value += featureArea;
							dataProvider[i].features.push(featureId);
						}
						rangeExists = true
					} 
				}
				if (rangeExists){
					pieChart.dataProvider = dataProvider;
				}else{
					pieChart.dataProvider.push({
						range: "Blue range",
		    			value: featureArea,
		    			color: "#6dc0ff",
		    			features: [featureId]
					});
				}
			}
		}else{
			//update pie chart data to remove non-existing area values
			for(var i in dataProvider){
				if (dataProvider[i].features.indexOf(featureId) > -1){
					for(var j in dataProvider[i].features){
						if (dataProvider[i].features[j] == featureId)
							dataProvider[i].features.pop(j);
					}
					if (dataProvider[i].features.length < 1){
						dataProvider.pop(i);
					}else{
						dataProvider[i].value -= featureArea;
					}
				}
			}
			pieChart.dataProvider = dataProvider;
		}
		//redraw chart
		pieChart.validateData();
		var statsText, fill, stroke, text;
		for (var i in response.stats){
			//do not concatenate with 'undefined'
			if(statsText == null){
				statsText = response.stats[i].data +': '+ response.stats[i].value +'\n';
			}else{
				statsText += response.stats[i].data +': '+ response.stats[i].value +'\n';
			}
			
		}
		if (statsText == null)
			statsText = '';

		var fontSize = 10;
		if (window.matchMedia("(min-width: 300px)").matches) {
			/* the viewport is at least 400 pixels wide */
			fontSize = 10;
		}

		if (window.matchMedia("(min-width: 700px)").matches) {

			fontSize = 12;
		}

		if (window.matchMedia("(min-width: 1400px)").matches) {

			fontSize = 14;
		}

		if (window.matchMedia("(min-width: 2000px)").matches) {

			fontSize = 18;
		}

		style = new ol.style.Style({
			fill: new ol.style.Fill({
				color: color != null ? color : [255,255,255,0],

			}),
			stroke: new ol.style.Stroke({
				color: [51,153,204, 0.7]
			}),
			text: new ol.style.Text({
				font: fontSize + 'px Hind Madurai',
				overflow: true,
				// placement: 'line',
				rotateWithView: true,
				// textAlign: 'left',
				fill: new ol.style.Fill({
					color: [0,0,0,1]
				}),
				text: response.paw.value == null ? statsText :response.paw.widget + '\nPAW: ' + 
				response.paw.value + '\n' + statsText, 
			})
		});
		feature.setStyle(style);

	}).fail(function(response){
		alert('Failed to load feature list.');
	});
}

function changeMapWidget(mapWidget){
	var mapWidgetID = mapWidget.attr('id');
	$.ajax({
		method: 'POST', 
		url: 'get-map-widget',
		dataType: 'json',
		data: JSON.stringify({wid:mapWidgetID})
	}).done(function(response){
		var map = mapWidget.data('map');
		map.getView().setZoom(response.zoom);
		map.getView().setCenter(ol.proj.fromLonLat(response.center));
		var layers = map.getLayers();
		var tileSource;
		layers.forEach(function(layer, index, array){
			if(layer instanceof ol.layer.Tile){
				var tileSource = layer.getSource();
				switch (response.tile_source){
					case 'ArcGIS':
						tileSource = new ol.source.XYZ({
							attributions: [new ol.Attribution({
								html: ''
							})],
							url: response.tile_url
						});
						break;
					case 'XYZ':
						tileSource = new ol.source.XYZ({
							attributions: response.tile_attribution,
							url: response.tile_url
						});
						break;
					case 'BingMapsAerial+Labels':
						tileSource = new ol.source.BingMaps({
							key: 'AnST1eDSeRY_VRrb86ud4B1Y_iS1OnD2NMs7EKYN8JvtRNoMt5ZjGWGsE8bNkTlJ', 
							imagerySet: 'AerialWithLabels'
						});
						break;
					default:
						tileSource = new ol.source.XYZ({
							attributions: response.tile_attribution,
							url: response.tile_url
						});
						break;
				}
				layer.setSource(tileSource);
			}	
		});

	}).fail(function(response){
		alert('Failed to load GIS widget settings.');
	});

}

function getMapWidgetOptions(mapWidgetID){
	$.ajax({
		method: 'POST', 
		url: 'get-map-widget',
		dataType: 'json',
		data: JSON.stringify({wid:mapWidgetID})
	}).done(function(response){
		$('#map-widget-title').val(response.name);
		$('#map-index').val(response.index);
		$('#map-zoom').val(response.zoom);
		$('#map-center-lat').val(response.center[0]);
		$('#map-center-long').val(response.center[1]);
		$('select#map-tile-source-select').data('kendoMultiSelect').value([response.tile_source]);
	}).fail(function(response){
		alert('Failed to load GIS widget settings.');
	});
	$.ajax({
		method: 'POST', 
		url: 'get-feature-list',
		dataType: 'json',
		data: JSON.stringify({'wid': mapWidgetID})
	}).done(function(response){
		//parse response for dropdown widget
		var dataSource = [];
		$.each(response.features, function(index, item){
			dataSource.push({fid:item.id,name:item.properties.name})
		})
		var select = $('select#map-feature-select').data('kendoMultiSelect');
		select.setDataSource(dataSource);
		if (dataSource.length > 1){
			select.value(dataSource[0].fid);
			select.trigger('change');
		}
	}).fail(function(response){
		alert('Failed to load feature list.');
	});
}

function  getChartWidgetList(){
	$.ajax({
		method: 'POST', 
		url: 'get-chart-widget-list',
		dataType: 'json',
	}).done(function(response){

		var select = $('select#map-paw-select').data('kendoMultiSelect');
		select.setDataSource(response);

	}).fail(function(response){
		alert('Failed to chart widget list.');
	});
}

function getDataWidgetList(){
	$.ajax({
		method: 'POST', 
		url: 'get-data-widget-list',
		dataType: 'json',
	}).done(function(response){

		var select = $('select#map-stat-select').data('kendoMultiSelect');

		var dataSource = new kendo.data.DataSource({
			data: response,
			group: {field: 'widget'}
		})
		select.setDataSource(dataSource);

	}).fail(function(response){
		alert('Failed to load feature list.');
	});
}

function styleMap(map){
	var fontSize = 10; // arbitrary value
	if (window.matchMedia("(min-width: 300px)").matches) {
		/* the viewport is at least 400 pixels wide */
		fontSize = 10;
	}

	if (window.matchMedia("(min-width: 700px)").matches) {

		fontSize = 12;
	}

	if (window.matchMedia("(min-width: 1400px)").matches) {

		fontSize = 14;
	}

	if (window.matchMedia("(min-width: 2000px)").matches) {

		fontSize = 18;
	}
	
	return [
		new ol.style.Style({
		  text: new ol.style.Text({
		    font: fontSize + 'px Calibri,sans-serif'
		  })
		})
	];
}

$(function(){
	//setup django csrftoken cookie for ajax
	//get crsf token cookie
	var csrftoken = getCookie('csrftoken');
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    getFileList();

	$('#add-gis-widget').on('click', function(e){
		createMapWidget();
	});
	
    $("#fileUpload").kendoUpload({
        async: {
            saveUrl: "upload",
            removeUrl: "remove",
            autoUpload: true
        },
        upload: function(e){
	    	// insert csrftoken into form before upload
            e.data = {csrfmiddlewaretoken: csrftoken}	
        },
        success: function (response){
        	getFileList();
        }, 
        remove: function (event){
        	event.preventDefault();
            //remove uploaded file from UI
            this.clearFileByUid(event.files[0].uid);
        }, 
        localization: {
        	select: 'Upload files...'
        }
    });

    $('#btn-delete-file').on('click', function(e){
    	var selectedFiles = $.map($('select#file-select'), function (el, i) {
	        return $(el).val();
	    });

	    if (!confirm('Are you sure you want to delete '+ selectedFiles.length +' file(s) ?')){
	    	return;
	    }
    	$.ajax({
    		method: 'POST', 
    		url: 'remove',
    		dataType: 'json',
    		data: JSON.stringify(selectedFiles)
    	}).done(function(response){
    		getFileList();
    	}).fail(function(response){
    		alert('Delete operation failed.');
    	});
    });

    $('#btn-download-file').on('click', function(e){
    	var selectedFiles = $.map($('select#file-select option:selected'), function (el, i) {
	        return $(el).attr("url");
	    });
	    for (var i = 0; i < selectedFiles.length; i++)
	    	window.open(selectedFiles[i]);
    });

    

    $('#btn-import-features').on('click', function(e){
    	if (lastInvokerWidget == null){
    		alert('No GIS widget selected');
    		return;
    	}
    	importFeatures();
    });

    $('#GISModal').on('shown.bs.modal', function (e){
    	lastInvokerWidget = $(e.relatedTarget).closest('section.main-panel').find('div.gis-container');
    	//get map widget options
    	getMapWidgetOptions(lastInvokerWidget.attr('id'));
    });

    $('select#map-feature-select').kendoMultiSelect({
    	maxSelectedItems: 1,
    	dataTextField: "name",
    	dataValueField: "fid",
    	change: function (e){
    		var value = this.value();
    		if (value.length < 1)
    			return
    		$.ajax({
	    		method: 'POST', 
	    		url: 'get-feature-stat-widgets',
	    		dataType: 'json',
	    		data: JSON.stringify({'fid': value[0]})
	    	}).done(function(response){
	    		$('select#map-paw-select').data('kendoMultiSelect').value(response.paw);
	    		$('select#map-stat-select').data('kendoMultiSelect').value(response.stats);
	    	}).fail(function(response){
	    		alert('Failed to load feature stat.');
	    	});
    	},
    	filter: "contains",
    	filtering: function (e) {
	      //custom filtering logic
	      if (e.filter != null){
	        e.preventDefault();

	        var filterWords = e.filter.value.split(" ");

	        var filters = [];

	        for(var i = 0; i < filterWords.length; i++){

	          filters.push({field:"name", operator:"contains", value:filterWords[i]});

	        }

	        e.sender.dataSource.filter([
	          {"logic":"and",
	           "filters": filters
	          }]);  
	      } 
	    }
    }).data('kendoMultiSelect');
    $('select#map-paw-select').kendoMultiSelect({
    	maxSelectedItems: 1,
    	value: [],
    	dataValueField: 'value', 
    	dataTextField: 'text',
    	change: function (e){
    		var value = this.value();
    		var feature = $('select#map-feature-select').data('kendoMultiSelect').value();
    		$.ajax({
	    		method: 'POST', 
	    		url: 'change-paw-feature-stat',
	    		dataType: 'json',
	    		data: JSON.stringify({'widget': value, 'feature_id':feature[0]})
	    	}).done(function(response){
	    		changeMapWidget(lastInvokerWidget);
	    		loadMapFeatureStats(feature[0], lastInvokerWidget);
	    	}).fail(function(response){
	    		alert('Failed to change feature stat.');
	    	});
    	}, 
    	filter:"contains",
    	filtering: function (e) {
	      //custom filtering logic
	      if (e.filter != null){
	        e.preventDefault();

	        var filterWords = e.filter.value.split(" ");

	        var filters = [];

	        for(var i = 0; i < filterWords.length; i++){

	          filters.push({field:"text", operator:"contains", value:filterWords[i]});

	        }

	        e.sender.dataSource.filter([
	          {"logic":"and",
	           "filters": filters
	          }]);  
	      } 
	    }
    }).data('kendoMultiSelect');
    $('select#map-stat-select').kendoMultiSelect({
    	maxSelectedItems: 3,
    	value: [],
    	dataValueField: 'value', 
    	dataTextField: 'text',
    	change: function (e){
    		var value = this.value();
    		var feature = $('select#map-feature-select').data('kendoMultiSelect').value();
    		$.ajax({
	    		method: 'POST', 
	    		url: 'change-feature-stat',
	    		dataType: 'json',
	    		data: JSON.stringify({'data_ids': value, 'feature_id': feature[0]})
	    	}).done(function(response){
	    		changeMapWidget(lastInvokerWidget);
	    		loadMapFeatureStats(feature[0], lastInvokerWidget);
	    	}).fail(function(response){
	    		alert('Failed to change feature stat.');
	    	});
    	}, 
    	filter:"contains",
    	filtering: function (e) {
	      //custom filtering logic
	      if (e.filter != null){
	        e.preventDefault();

	        var filterWords = e.filter.value.split(" ");

	        var filters = [];

	        for(var i = 0; i < filterWords.length; i++){

	          filters.push({field:"text", operator:"contains", value:filterWords[i]});

	        }

	        e.sender.dataSource.filter([
	          {"logic":"and",
	           "filters": filters
	          }]);  
	      } 
	    }
    }).data('kendoMultiSelect');
    //initialize paw and stat selects
    getChartWidgetList();
    getDataWidgetList();
    $('select#map-tile-source-select').kendoMultiSelect({
    	maxSelectedItems: 1, 
    	change: function(e){
    		var value = this.value();
    		var widget = lastInvokerWidget.attr('id');
    	}, 
    	filter: "contains",
    	filtering: function (e) {
	      //custom filtering logic
	      if (e.filter != null){
	        e.preventDefault();

	        var filterWords = e.filter.value.split(" ");

	        var filters = [];

	        for(var i = 0; i < filterWords.length; i++){

	          filters.push({field:"text", operator:"contains", value:filterWords[i]});

	        }

	        e.sender.dataSource.filter([
	          {"logic":"and",
	           "filters": filters
	          }]);  
	      } 
	    }

    }).data('kendoMultiSelect');

    $('#map-dialog').kendoDialog({
		width: "250px",
        // title: "Download format",
        closable: true,
        modal: false,
        content: "Please choose a format.",
        actions: [
            { text: 'PNG', action: downloadMapAsPNG },
            { text: 'GeoJSON', action: downloadMapAsGJSON },
            { text: 'KML', action: downloadMapAsKML },
            // { text: 'Cancel', primary: true }
        ],
        // close: onClose
	}).data('kendoDialog').close();

    //customize tooltips with bootstrap
    $('.ol-zoom-in, .ol-zoom-out').tooltip({
        placement: 'right'
	});

	$('.ol-rotate-reset, .ol-attribution button[title]').tooltip({
	  placement: 'left'
	});



    $('div.chart-row').on('click', 'a#map-widget-delete-button', function(e){
    	if(!confirm("Are you sure you want to delete map widget ?")){
    		return
    	}
    	var main_panel = $(this).closest('section.main-panel') 
    	var widget_id = main_panel.find('div.gis-container').attr('id');
    	$.ajax({
    		method: 'POST', 
    		url: 'delete-map-widget',
    		dataType: 'json',
    		data: JSON.stringify({'wid': widget_id})
    	}).done(function(response){
    		main_panel.parent().remove();
    	}).fail(function(response){
    		alert('Delete operation failed.');
    	});
    });

    $('#GISModal').find('button#save-map-changes').on('click', function(e){
    		var title = $('#map-widget-title').val();
    		var index = $('#map-index').val();
    		var zoom = $('#map-zoom').val();
    		var lat = $('#map-center-lat').val();
    		var long = $('#map-center-long').val();
    		var tile_source = $('select#map-tile-source-select').data('kendoMultiSelect').value();
    		var data = {
    			'wid': lastInvokerWidget.attr('id'),
    			'name': title,
    			'index': index,
    			'zoom': zoom,
    			'lat': lat,
    			'long': long,
    			'tile_source': tile_source[0],
    		}
    		$.ajax({
	    		method: 'POST', 
	    		url: 'change-map-widget',
	    		dataType: 'json',
	    		data: JSON.stringify(data)
	    	}).done(function(response){
	    		$('#GISModal').modal('hide');
	    		changeMapWidget(lastInvokerWidget);
	    	}).fail(function(response){
	    		alert('Failed. Widget not modified.');
	    	});
    });
    loadMapWidgets();
}); // end of $(function)
