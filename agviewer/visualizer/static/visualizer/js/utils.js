
$(document).ready(function(){
	$('.expandable').not('.gis').on('click', function  (e) {
		var ctnDiv =  $(this).closest('div');
		if(ctnDiv.hasClass('col-lg-6')){
			ctnDiv.removeClass('col-lg-6');
			ctnDiv.addClass('col-lg-12');
			$(this).removeClass('fa-expand');
			$(this).addClass('fa-compress');
			var elementId = $(ctnDiv.find('div.chart-container')).attr('id');
			$.ajax({
		      method: "POST",
		      url: 'resize-chart',
		      dataType: 'json',
		      data: JSON.stringify({widget_id:elementId, expand: true})
		    });
		}else if (ctnDiv.hasClass('col-lg-12')) {
			ctnDiv.removeClass('col-lg-12');
			ctnDiv.addClass('col-lg-6');
			$(this).removeClass('fa-compress');
			$(this).addClass('fa-expand');
			var elementId = $(ctnDiv.find('div.chart-container')).attr('id');
			$.ajax({
		      method: "POST",
		      url: 'resize-chart',
		      dataType: 'json',
		      data: JSON.stringify({widget_id:elementId, expand: false})
		    });
		};
	});

	$('.gis').on('click', function (e) {
		var gisContainer = $(this).closest('div')
		if(gisContainer.hasClass('col-lg-6')){
			gisContainer.removeClass('col-lg-6');
			gisContainer.addClass('col-lg-12');
			$(this).removeClass('fa-expand');
			$(this).addClass('fa-compress');
			gisContainer.find('div.gis-panel').addClass('extended-map');
			var map = $(gisContainer.find('div.gis-container')).data('map');
			map.updateSize();
			var elementId = $(gisContainer.find('div.gis-container')).attr('id');
			$.ajax({
		      method: "POST",
		      url: 'resize-map',
		      dataType: 'json',
		      data: JSON.stringify({wid:elementId, expand: true})
		    });

		}else if(gisContainer.hasClass('col-lg-12')){
			gisContainer.removeClass('col-lg-12');
			gisContainer.addClass('col-lg-6');
			$(this).removeClass('fa-compress');
			$(this).addClass('fa-expand');
			gisContainer.find('div.gis-panel').removeClass('extended-map');
			var map = $(gisContainer.find('div.gis-container')).data('map');
			map.updateSize();
			var elementId = $(gisContainer.find('div.gis-container')).attr('id');
			$.ajax({
		      method: "POST",
		      url: 'resize-map',
		      dataType: 'json',
		      data: JSON.stringify({wid:elementId, expand: false})
		    });
		}
	})

});
