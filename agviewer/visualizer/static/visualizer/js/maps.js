
function getID() {
	id = getRandomColor();
	widget_lst = Object.keys(all_widgets);
	if (id.split('#')[1] in widget_lst) {
		return getID();
	}else{
		return id.split('#')[1];
	};
}



$(function(){
	$('#add-gis-widget').on('click', function(e){
		
		var gisWidgetID = getID();
		var html = '<div class="col-lg-6">\
						<section id="main-panel-" class="panel main-panel">\
							<header class="panel-heading">\
								<span class="title">New chart panel &nbsp;<i id="main-panel-{{forloop.counter}}-i" class=""></i></span>\
								<span class="tools pull-right">\
									<a href="javascript:;" class="fa fa-chevron-down"></a>\
									<a href="#main-chart-modal" data-toggle="modal" class="fa fa-wrench"></a>\
									<a href="javascript:;" class="fa fa-times"></a>\
								</span>\
							</header>\
							<div class="panel-body">\
								<div id="'+gisWidgetID+'" class="gis-container chart-container">\
								</div>\
							</div>\
						</section>\
					</div>';
		$('.chart-row').append(html);
		var map = new google.maps.Map(document.getElementById(gisWidgetID), {
	      center: {lat: -34.397, lng: 150.644},
	      zoom: 8
	    });
	});
});