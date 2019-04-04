
//Globals
var user_settings = null;
var widget_lst;
var $date_from;
var $date_to;
var all_widgets = {};
var $pawFields = {};
var satExECLst = [];
var voltageSensors=[], voltageLst=[], voltageCheckbox, voltageAxes = {};
var $sat_ex_ec_sensors = [];
var $options;
var selects = {};
var $ex_ec_checkbox;
var $widget_id, $main_paw_fc, $main_paw_wp;
var pickers = {};



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

function ajax_setup(){


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

};

function Widget(id, index, title, type, options, data) {
	this.id = id;
	this.index = index; 
	this.type = type;
	this.options = options;
	this.data = data;
	this.title = title;

}

function addWidget(){

	widget = new Widget('stat', '99', 'stat1', 'stat1', {'station':''});
	widget.create();  
}

// expand chart



function ajax_request(callback, widget, notify_el) {
	var request = $.ajax({
		  method: "POST",
		  url: url,
		  data: JSON.stringify(widget), 
		  dataType: 'json'
		}).done(function(data) {
    		callback(data);
    		notify_remove(notify_el);

  		}).fail(function(msg){
  			notify_remove(notify_el);
  			if (widget.type == 'main-chart') {
  				notify_auto('danger', 5, 'Chart failed to load. Please check parameters and try again.')
  			}else if (widget.type == 'stat') {
  				notify_auto('danger', 5, 'Stat Widget failed to load. Please try again.');
  			};;
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

function notify_auto(type, delay, msg) {
              var alert = jQuery("<div>").addClass("alert alert-" + type).on("click", function () {
                  jQuery(this).remove();
              }).prependTo(".growl");
              jQuery("<p>").text(msg).appendTo(alert);
              jQuery(alert).animate({
                  opacity: 0
              }, 1000 * delay, function () {
                  jQuery(this).remove();   
              });
    }

function notify_man(type, msg) {
              var alert = jQuery("<div>").addClass("alert alert-" + type).on("click", function () {
                  jQuery(this).remove();
              }).prependTo(".growl");
              jQuery("<p>").text(msg).appendTo(alert);
			return alert;
    }

function notify_remove(element){
	jQuery(element).animate({
                  opacity: 0
              }, 1000, function () {
              	$(this).remove();   
              });
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

function a_request(callback, url, data, s_msg, f_msg){
	var request = $.ajax({
				method: 'POST',
				url: url,
				data: JSON.stringify(data),
				dataType: 'json'
			}).done(function(data) {
				widget = data.widget;
//				all_widgets[widget.id] = widget;
				callback(widget);
			}).fail(function(msg){
				notify_auto('danger', 5, f_msg)
	});
}

// function load_widgets() {
// 	function render(widget_lst){
// 		for (var i in widget_lst){
// 			ajax_setup();
// 			a_request(render_chart, url_widget, {'widget':widget_lst[i]},'','Failed to load chart(s).');
// 		};

// 	}
// 	var request = $.ajax({
// 		  method: "GET",
// 		  url: url_widget_lst,
// 		  dataType: 'json'
// 		}).done(function(data) {
//     		render(data);
//   		}).fail(function(msg){
//   			alert('failed');
//   	});
// }

function alert_action(params){
  //update alert table
  // GET, ADD_NEW, MODIFY, REMOVE, MARK_NEW, MARK_OFF_NEW, MARK_READ
  var method = 'POST';
  var action = params.action;
  var invoker_id = params.uid;
  if (action == 'GET'){
    method = 'GET';
    params = {params: JSON.stringify(params)}
  }else{
    params = JSON.stringify(params)
  }
  var request = $.ajax({
      method: method,
      url: '/alert_action',
      data: params,
      dataType: 'json'
    }).done(function(data){
      console.log(data);
      if (action == 'GET')
        populate_alert_modal(data);
      if (action == 'DELETE'){
        if(data.success)
          $('#'+invoker_id).parent().parent().remove();
      }
      if (action == 'ADD_NEW'){
        if(data.success){
          params = $.parseJSON(params);
          var uid = data.uid;
          var type_label = 'label-info fa fa-info-circle';
          if (params.type == 'warning')
            type_label = 'label-warning fa fa-exclamation-circle';
          if (params.type == 'critical')
            type_label = 'label-danger fa fa-warning';
          $('.alerts-table table tbody').prepend('<tr>\
            <td>'+params.name+'</td>\
            <td class="hidden-xs">'+params.description+'</td>\
            <td><span class="label '+type_label+' label-mini"> </span></td>\
            <td>\
              <button class="btn btn-primary btn-xs" data-toggle="modal" data-target="#add-alert-modal" id="'+uid+'">\
              <i class="fa fa-pencil"></i></button>\
              <button class="btn btn-danger btn-xs delete-alert" id="'+uid+'"><i class="fa fa-trash-o "></i></button>\
            </td>\
          </tr>');
        }else{
          notify_auto('danger', 5, data.message);
        }

      }
      if (action == 'MARK_NEW'){
        if(data.success){
          if(data.new_count > 0){
            $('#alert-badge').html(data.new_count);
            notify_auto('success', 5, 'You have new notifications.');
          }else{
            $('#alert-badge').html('');
          }
          render_alerts(data.alerts, data.unread);
        }
      }
      if (action == 'MARK_OFF_NEW'){
        if (data.success)
          $('#alert-badge').html('');
      }

      if (action == 'GET_EVENT'){
        if (data.success)
          render_event(data);
      }

    }).fail(function(data){
      notify_auto('danger', 5, data.message);
    });
}
function render_alerts(alerts, unread){
  $('#alert-list').empty();
  
  $('#alert-list').prepend('\
      <li>\
        <a href="#">See all notifications</a>\
      </li>\
    ');
  for(var i = alerts.length-1; i >= 0; i--){
    var type_icon = 'fa-info-circle';
    var type_label = 'label-info';
    if(alerts[i].type == 'warning'){
      type_icon = 'fa-warning';
      type_label = 'label-warning';
    }else if(alerts[i].type == 'critical'){
      type_icon = 'fa-exclamation-circle';
      type_label = 'label-danger';
    }
    var title = alerts[i].name;
    var message = alerts[i].message;
    var time = alerts[i].t_notify;
    var uid = alerts[i].uid;
    var widgetTitle = alerts[i].widget;
    var readClass = 'message-unread';
    if (alerts[i].read)
      readClass = 'message-read';
    $('#alert-list').prepend('\
      <li>\
          <a href="#" class="alert-event" data-toggle="modal" data-target="#show-event-modal" id="'+uid+'">\
          	  <span class="image label '+type_label+'"><i class="fa '+type_icon+'"></i></span>\
              <span class="station '+readClass+'">'+widgetTitle+'</span>\
              <span class="subject">\
              <span class="from '+readClass+'">'+title+'</span>\
              <span class="time">'+time+'</span>\
              </span>\
              <span class="message">'+message+'</span>\
          </a>\
      </li>\
    ');
  }
  
    $('#alert-list').prepend('\
      <div class="notify-arrow notify-arrow-grey"></div>\
        <li>\
          <p class="grey">You have '+unread+' unread notifications</p>\
        </li>\
  ');
}

function render_event(event){
  $('#show-event-modal .name').html(event.name);
  $('#show-event-modal .description').html(event.description);
  $('#show-event-modal .message').html(event.message);
  $('#show-event-modal .station').html(event.station);
  $('#show-event-modal .widget').html(event.widget);
  $('#show-event-modal .calc').html(event.calc);
  $('#show-event-modal .sensor').html(event.sensor);
  $('#show-event-modal .time').html(event.t_notify);
  $('#show-event-modal .value').html(event.value);

}

function mark_new_alert(count){
  count = (typeof b !== 'undefined') ? b : 5;
  var params = {
    'action': 'MARK_NEW', 
    'count': count
  };
  alert_action(params);
}

function markoff_new_alert(){
  var params = {
    'action': 'MARK_OFF_NEW'
  }
  alert_action(params);
}

function mark_read(uid){
  var params = {
    'action': 'MARK_READ',
    'uid': uid
  }
  alert_action(params);
}

function addDashboard(name){
  var params = {
    name: name
  }
  var request = $.ajax({
    method: 'POST',
    url: '/adddashboard',
    data: JSON.stringify(params),
    dataType: 'json'
  }).done(function(data){
    var uid = data.uid;
    // console.log(uid);
    $('#sidebar .sidebar-menu .sub-menu .sub').append('\
      <li class="sub-menu">\
        <a class="dashboard-item" id="'+uid+'"  href="/?dashboard='+uid+'">\
          '+name+'\
        </a>\
      </li>\
    ');

  }).fail(function(data){
    notify_auto('danger', 5, data.message);
  });
}

function load_widgets() {
	function render(widgets){
		widget_lst = Object.keys(widgets);
		all_widgets = widgets;
		for (var i in widget_lst){
			if (widgets[widget_lst[i]]['widget']['type'] != 'stat') {
				widget = widgets[widget_lst[i]].widget;
				render_chart(widget);
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

$(function() {
  //initialize date range variables
	var dt_start = moment().subtract(30, 'days').startOf('day'); 
	var dt_end = moment().add(1, 'hour').startOf('hour');
  //date range for stat widget
  var stat_dt_start = moment().subtract(24, 'hour').startOf('hour');
  var stat_dt_end = moment().add(1, 'hour').startOf('hour');

  function cb(start, end) {
    $date_from = start.format('YYYY-MM-DD') + ' ' + String(moment().hour())+':00';
    $date_to = end.format('YYYY-MM-DD') + ' ' + String(moment().hour()+1)+':00';

    if (moment($date_from).hour() == 0) {
    	$date_from = start.format('YYYY-MM-DD') + ' ' + '00:00';	
    };
    if (moment($date_to).hour() == 0) {
    	$date_to = end.format('YYYY-MM-DD') + ' ' + '00:00';	
    };
     
    $('#reportrange span').html($date_from + ' - ' + $date_to);
  }
  cb(dt_start, dt_end);

  $('#reportrange').daterangepicker({
  	locale: {
  		format: 'YYYY-MM-DD'
  	},
  	timePicker: false,
  	startDate: dt_start,
  	endDate: dt_end,
      ranges: {
       '48 Hours': [moment().subtract(2, 'days'), moment()],
       '2 Weeks': [moment().subtract(14, 'days'), moment()],
       '30 Days': [moment().subtract(30, 'days'), moment()],
       '3 Months': [moment().subtract(3, 'month'), moment()],
       '6 Months': [moment().subtract(6, 'month'), moment()],
       '12 Months': [moment().subtract(12, 'month'), moment()]
      }
  }, cb);

  // chart title bar daterange picker
  $('.daterange').daterangepicker({
    locale: {
      format: 'YYYY-MM-DD'
    }, 
    timePicker: false,
    startDate: dt_start, 
    endDate: dt_end,
    ranges: {
     '48 Hours': [moment().subtract(2, 'days'), moment()],
     '2 Weeks': [moment().subtract(14, 'days'), moment()],
     '30 Days': [moment().subtract(30, 'days'), moment()],
     '3 Months': [moment().subtract(3, 'month'), moment()],
     '6 Months': [moment().subtract(6, 'month'), moment()],
     '12 Months': [moment().subtract(12, 'month'), moment()]
    }
  }, cb);

  $('.daterange').on('apply.daterangepicker', function(e, picker){
    var invoker = $(e.target);
    var chartID = invoker.parent().parent().parent().children('div').children('div').attr('id');
    invoker.parent().parent().parent().children('div').append('<div class="curtain">\
      <span><i class="fa fa-spin fa-spinner"></i> Loading...</span>\
      </div>');
    var params = {
      widgetID: chartID,
      dateFrom: $date_from, 
      dateTo: $date_to
    }
    var request = $.ajax({
      method: 'POST',
      url: '/changedaterange',
      data: JSON.stringify(params),
      dataType: 'json'
    }).done(function (data){
      render_chart(data.widget);
    }).fail(function (message){
      notify_auto('danger', 5, message.message);
    });
  });

  //add stat data modal daterange initialization
  function cb_stat(start, end) {
    stat_dt_start = start.format('YYYY-MM-DD') + ' ' + String(moment().hour())+':00',
    stat_dt_end = end.format('YYYY-MM-DD') + ' ' + String(moment().hour()+1)+':00';

    if (moment(stat_dt_start).hour() == 0) {
      stat_dt_start = start.format('YYYY-MM-DD') + ' ' + '00:00';  
    };
    if (moment(stat_dt_end).hour() == 0) {
      stat_dt_end = end.format('YYYY-MM-DD') + ' ' + '00:00';  
    };
     
    $('#statdaterange span').html(stat_dt_start + ' - ' + stat_dt_end);
  }

  cb_stat(stat_dt_start, stat_dt_end);

  $('#statdaterange').daterangepicker({
    locale: {
      format: 'YYYY-MM-DD'
    },
    timePicker: false,
    startDate: stat_dt_start,
    endDate: stat_dt_end,
      ranges: {
       '24 Hours': [moment().subtract(1, 'days'), moment()],
       '48 Hours': [moment().subtract(2, 'days'), moment()],
       '2 Weeks': [moment().subtract(14, 'days'), moment()],
       '30 Days': [moment().subtract(30, 'days'), moment()],
       '3 Months': [moment().subtract(3, 'month'), moment()],
       '6 Months': [moment().subtract(6, 'month'), moment()]
      }
  }, cb_stat);

  //mark off new notification icon
  $('.notification-dropdown').on('click', function(e){
    markoff_new_alert();
  });
  //load notifications after load
  mark_new_alert();
  setTimeout(mark_new_alert, 300000);

  $('#show-event-modal').on('show.bs.modal', function(e){
    var event_id = $(e.relatedTarget).attr('id');
    params = {
      'action': 'GET_EVENT',
      'uid': event_id
    }
    alert_action(params);
    mark_read(event_id);
	});
  //load widgets after document.ready()
	load_widgets();
	// load user_settings
	load_user_settings();

  //add dashboard
  $('#add-dashboard-modal button.submit').on('click', function(e){
    var dashboardName = $('#add-dashboard-modal input.dashboard-name').val()

    addDashboard(dashboardName);
    $('#add-dashboard-modal').modal('hide');

  });

  // new stat widgets

  $('#stat-sensor-select').kendoMultiSelect({
    maxSelectedItems: 1,
    filter: 'contains',
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

  $('#stat-data-select').kendoMultiSelect({
    maxSelectedItems: 1,
    filter: 'contains',
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

  $('#add-stat-widget-modal').on('show.bs.modal', function(e){
    statWidgetModalInvoker = $(e.relatedTarget);
    var statColorCTN = $('#stat-widget-color-ctn');
    if (statColorCTN.children().length < 1 ){
      var colorInputElement = document.createElement('INPUT');
      statWidgetModalColorPicker = new jscolor(colorInputElement, {'zIndex':1052});
      colorInputElement.setAttribute('id', 'stat-widget-modal-color-input');
      colorInputElement.className = 'form-control input-sm stat-widget-color ';
      statWidgetModalColorPicker.fromString('0DC2E9');
      $('#stat-widget-color-ctn').append($(colorInputElement));
    }

    //change button label and title
    if (statWidgetModalInvoker.attr('operation') == 'MODIFY'){
      $('#add-stat-widget-modal button.submit').html('Change');
      $('#add-stat-widget-modal div.modal-header h4.modal-title').html('Edit widget');
      //fetch stat widget details
      var params = {
        'widget': statWidgetModalInvoker.parents('div.stat-widget').attr('id')
      }
      var request = $.ajax({
        method: "POST",
        url: '/fetch_stat_widget',
        data: JSON.stringify(params), 
        dataType: 'json'
      }).done(function(data) {
        if (data.success){
          //populate model fields
          $('#add-stat-widget-modal input.stat-widget-name').val(data.name),
          statWidgetModalColorPicker.fromString(data.color);
          $('#add-stat-widget-modal input.stat-widget-index').val(data.index);

        }else{
          notify_auto('danger', 10, data.message);
        }
      }).fail(function(msg){
        notify_auto('danger', 10, 'Operation Failed.');
      });

    }else{
      $('#add-stat-widget-modal button.submit').html('Add');
      $('#add-stat-widget-modal div.modal-header h4.modal-title').html('New widget');
    }

    

  });

  //delete stat widget
  $('div.stat-row').on('click','div.stat-widget span.actions a.fa-times', function(e){
    e.stopImmediatePropagation();
    if(!confirm('Are you sure you want to delete widget permenantly ?')){
      return
    };
    
    var params = {
      'widget': $(this).parents('div.stat-widget').attr('id')
    }

    var request = $.ajax({
      method: "POST",
      url: '/delete_stat_widget',
      data: JSON.stringify(params), 
      dataType: 'json'
    }).done(function(data) {
      if (data.success){
        //delete dom element
        $('#'+data.id).remove();

      }else{
        notify_auto('danger', 10, data.message);
      }
    }).fail(function(msg){
      notify_auto('danger', 10, 'Operation Failed.');
    });

  });

  // add stat widget
  $('#add-stat-widget-modal button.submit').on('click', function(e){
    e.preventDefault();
    e.stopImmediatePropagation();
    var name = $('#add-stat-widget-modal input.stat-widget-name').val(),
    url = '/add_stat_widget';
    var color = $('#add-stat-widget-modal input.stat-widget-color').val();
    var index = $('#add-stat-widget-modal input.stat-widget-index').val();

    var params = {
      'widget': statWidgetModalInvoker.parents('div.stat-widget').attr('id'),
      'name': name, 
      'color': color, 
      'index': index 
    }
    if (statWidgetModalInvoker.attr('operation') == 'MODIFY')
      url = '/change_stat_widget';

    var request = $.ajax({
      method: "POST",
      url: url,
      data: JSON.stringify(params), 
      dataType: 'json'
    }).done(function(data) {
      if (data.success){
        //add widget to DOM
        if (statWidgetModalInvoker.attr('operation') == 'ADD_NEW'){
          $('#main-content div.stat-row').append('<div class="col-lg-3 col-md-3 col-xs-12 stat-widget" id="'+data.id+'">\
          <section class="panel">\
            <div class="weather-bg" style="background:#'+color+';">\
                <div class="panel-body">\
                  <span class="title">'+name+'</span>\
                    <span class="actions pull-right">\
                      <a href="#add-stat-data-modal" data-toggle="modal" operation="ADD_NEW" id="'+data.id+'" class="fa fa-plus"></a>\
                      <a href="#add-stat-widget-modal" data-toggle="modal" operation="MODIFY" class="fa fa-wrench"></a>\
                      <a href="javascript:;" class="fa fa-times"></a>\
                  </span>\
                </div>\
            </div>\
            <footer class="weather-category">\
                <ul>\
                </ul>\
            </footer>\
          </section>  \
        </div>');  
        }else{
          $('div#'+data.id+' div.weather-bg').attr('style', 'background:#'+data.color+';');
          $('div#'+data.id+' span.title').html(data.name);

        }
        
      }else{
        notify_auto('danger', 10, data.message);
      }
    }).fail(function(msg){
      notify_auto('danger', 10, 'Operation Failed.');
    });

    $('#add-stat-widget-modal').modal('hide');

  });

  //***add stat calc ***

  //initialize add stat modal chart select
  $('#stat-chart-select').kendoMultiSelect({
    maxSelectedItems: 1, 
    filter: 'contains',
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
  });

  $('#add-stat-data-modal').on('show.bs.modal', function(e){
    //global to store modal invoker
    statDataModalInvoker = $(e.relatedTarget);
    var operation = statDataModalInvoker.attr('operation');

    //change modal submit button text
    if (operation == 'MODIFY'){
      //change submit button text
      $('#add-stat-data-modal button.submit').html('Change');
      //display delete button on modal
      $('#add-stat-data-modal button.delete').css('display', 'inline-block');
      //fetch cliked widget data
      var params = {
        'data_id': statDataModalInvoker.parent().attr('id')
      }
      var request = $.ajax({
        method: "POST",
        url: '/fetch_stat_data',
        data: JSON.stringify(params), 
        dataType: 'json'
      }).done(function(data) {
        if (data.success){
          //populate modal fields
          $('#stat-data-select option:selected').removeAttr('selected');
          $('#stat-sensor-select option:selected').removeAttr('selected');
          $('#stat-chart-select option:selected').removeAttr('selected');
          $('#add-stat-data-modal input.stat-data-name').val(data.name);
          $('#stat-data-select').data('kendoMultiSelect').value(data.data);
          $('#stat-sensor-select').data('kendoMultiSelect').value(data.sensor);
          $('#add-stat-data-modal input.stat-data-extract').val(data.extract);
          $('#stat-chart-select').data('kendoMultiSelect').value(data.chart);
          
          //if a sensor is selected chart select should be disabled and vice-versa
          if ($('#stat-sensor-select').data('kendoMultiSelect').value().length > 0){
            $('#stat-chart-select').data('kendoMultiSelect').enable(false);
          }else{
            $('#stat-chart-select').data('kendoMultiSelect').enable(true);
          }

          if ($('#stat-chart-select').data('kendoMultiSelect').value().length > 0){
            $('#stat-sensor-select').data('kendoMultiSelect').enable(false);
          }else{
            $('#stat-sensor-select').data('kendoMultiSelect').enable(true);
          }

          
        }else{
          notify_auto('danger', 10, data.message);
        }
      }).fail(function(data){
        notify_auto('danger', 10, data.message);
      });

    }else{
      //change submit button text
      $('#add-stat-data-modal button.submit').html('Add');
      //do not display delete button on modal
      $('#add-stat-data-modal button.delete').css('display', 'none');
      //empty select boxes
      $('#stat-data-select').data('kendoMultiSelect').value([]);
      $('#stat-sensor-select').data('kendoMultiSelect').value([]);
      $('#stat-chart-select').data('kendoMultiSelect').value([]);
      $('#stat-chart-select').data('kendoMultiSelect').enable(true);
      $('#stat-sensor-select').data('kendoMultiSelect').enable(true);
    }
 
  });


  //sensor and chart selects of stat-data-modal disable each other
  $('#stat-sensor-select').on('change', function(e){
    if ($(this).data('kendoMultiSelect').value().length > 0){
      $('#add-stat-data-modal select#stat-chart-select').data('kendoMultiSelect').enable(false);
    }else{
      $('#add-stat-data-modal select#stat-chart-select').data('kendoMultiSelect').enable(true)
    }
  });

  $('#stat-chart-select').on('change', function(e){
    if ($(this).data('kendoMultiSelect').value().length > 0){
      $('#stat-sensor-select').data('kendoMultiSelect').enable(false);
    }else{
      $('#stat-sensor-select').data('kendoMultiSelect').enable(true)
    }
  });

  //add or modify stat data
  $('#add-stat-data-modal button.submit').on('click', function(event){
    event.preventDefault();
    event.stopImmediatePropagation();

    var params, url, dataID, widgetID, operation = statDataModalInvoker.attr('operation');

    if (operation == 'MODIFY'){
      url = '/change_stat_data';
      dataID = statDataModalInvoker.parent().attr('id');
    }else{
      url = '/add_stat_data';
      widgetID = statDataModalInvoker.attr('id');
    }

    var name = $('#add-stat-data-modal input.stat-data-name').val(),
    data = $('#add-stat-data-modal select#stat-data-select option:selected').attr('value'),
    sensor = $('#add-stat-data-modal select#stat-sensor-select option:selected').attr('value'), 
    extract = $('#add-stat-data-modal input.stat-data-extract').val(), 
    chart = $('#add-stat-data-modal select#stat-chart-select option:selected').attr('value');

    if (data == undefined ){
      alert('Please specify a function');
      return
    }

    if (sensor == undefined && chart == undefined ){
      alert('Please select a sensor or chart.');
      return
    }

    if (sensor != undefined && chart != undefined ){
      alert('Please select either a sensor or a chart.');
      return
    }

    params = {
      'widget': widgetID,
      'data_id': dataID,
      'name': name, 
      'data': data, 
      'sensor': sensor, 
      'extract': extract,
      'chart': chart, 
      'from': stat_dt_start, 
      'to': stat_dt_end
    }
    // console.log(params);

    var request = $.ajax({
      method: "POST",
      url: url,
      data: JSON.stringify(params), 
      dataType: 'json'
    }).done(function(data) {
      // if (data.success){
        var value = data.value;
        var unit = data.unit
        if (value == null){
          value = 'failed';
          unit = '';
        }
        if (operation == 'ADD_NEW'){
          statDataModalInvoker.parents('section').children('footer').children('ul').append('<li id="'+data.id+'">\
            <a href="#add-stat-data-modal" data-toggle="modal" operation="MODIFY">\
              <h5>'+name+'</h5>\
              '+value+' '+unit+'\
              <span class="datetime">'+data.date_to+'</span>\
            </a>\
          </li>');
        }else{
          $('li#'+dataID).html('\
            <a href="#add-stat-data-modal" data-toggle="modal" operation="MODIFY">\
              <h5>'+data.name+'</h5>\
              '+value+' '+unit+'\
              <span class="datetime">'+data.date_to+'</span>\
            </a>\
          ');
        }
        //add data to widget
        //if widget has more than 2 data expand widget width
        if (statDataModalInvoker.parents('section').children('footer').children('ul').children().length > 2){
          statDataModalInvoker.parents('div.stat-widget').removeClass("col-lg-3 col-md-3");
          statDataModalInvoker.parents('div.stat-widget').addClass("col-lg-6 col-md-6");
        }else{
          statDataModalInvoker.parents('div.stat-widget').removeClass("col-lg-6 col-md-6");
          statDataModalInvoker.parents('div.stat-widget').addClass("col-lg-3 col-md-3");
        }
        $('#add-stat-data-modal').modal('hide');
      // }else{
      //   notify_auto('danger', 10, data.message);
      // }
    }).fail(function(msg){
      notify_auto('danger', 10, 'Operation Failed.');
    });

  });

  $('#add-stat-data-modal button.delete').on('click', function(e){
    e.stopImmediatePropagation();
    if(!confirm('Are you sure you want to delete widget data permenantly ?')){
      return
    };
    var params = {
      'data_id': statDataModalInvoker.parent().attr('id')
    }
    var request = $.ajax({
      method: "POST",
      url: '/delete_stat_data',
      data: JSON.stringify(params), 
      dataType: 'json'
    }).done(function(data) {
      if (data.success){
        var dataWidgetID = statDataModalInvoker.parents('div.stat-widget').attr('id');
        //delete dom element and hide modal
        $('#'+params.data_id).remove();
        $('#add-stat-data-modal').modal('hide');
        //resize widget
        if ($('#'+dataWidgetID+' ul li').length <= 2){
          $('#'+dataWidgetID).removeClass("col-lg-6 col-md-6");
          $('#'+dataWidgetID).addClass("col-lg-3 col-md-3");
        }
      }else{
        notify_auto('danger', 10, data.message);
      }
    }).fail(function(msg){
      notify_auto('danger', 10, 'Operation Failed.');
    });

  });

  
});

var sort = function(array) {
  var len = array.length;
  if(len < 2) { 
    return array;
  }
  var pivot = Math.ceil(len/2);
  return merge(sort(array.slice(0,pivot)), sort(array.slice(pivot)));
};

var merge = function(left, right) {
  var result = [];
  while((left.length > 0) && (right.length > 0)) {
    if(moment(left[0].date) > moment(right[0].date)) {
      result.push(right.shift());
    }
    else {
      result.push(left.shift());
    }
  };

  result = result.concat(left, right);
  return result;
};

function makeData (widget) {
	var dataObjects = {};
	var dataList = [];
	var calcList = [];
	var date;

	$.each(widget.data, function (key, val) {
		// if calculation not selected
		
		if (val == null)
			return true;
		// invalid option
		if (['title', 'range', 'calc'].indexOf(key) != -1)
			return true;
		// if no values returned
		if (val.value.length == 0)
			return true;
		// if multi-graph option
		if (['raw_sensors', 'paw', 'ex_ec', 'voltage'].indexOf(key) != -1) {

			for (var i = 0; i < val.value.length; i++) {
				for (var j = 0; j < val.value[i].length; j++) {
					date = moment(val.value[i][j].date).format('YYYY-MM-DD HH:mm');
					if (dataObjects.hasOwnProperty(date)) {
						dataObjects[date][key+'-'+i] = val.value[i][j].value;

					}else{
						var property = key+'-'+i;
						var obj = {};
						obj[property] = val.value[i][j].value; 
						obj['date'] = date; 
						dataObjects[date] = obj;
					};
				};
				calcList.push(key+'-'+i);
			};
		}else{
			for (var i = 0; i < val.value.length;i++){
				date = moment(val.value[i].date).format('YYYY-MM-DD HH:mm');
				if (dataObjects.hasOwnProperty(date)) {
					dataObjects[date][key] = val.value[i].value;

				}else{
					var property = key;
					var obj = {};
					obj[property] = val.value[i].value; 
					obj['date'] = date; 
					dataObjects[date] = obj;
				};
			};
			calcList.push(key);
		};
	});

	$.each(dataObjects, function (key, val) {
		dataList.push(val);
	})

	

	// time1 = moment('2016-11-11 09:00')
	// time2 = moment('2016-11-11 10:00')
	// console.log(time1.diff(time2));

	// dataList.sort(function (a, b) {
	// 	return moment(a.date).diff(moment(b.date));
	// });
	dataList = sort(dataList);
	
	// make sure dataList[0] contains entry for all datasets
	if(dataList.length > 0){
		$.each(calcList, function (i, val) {
			if (!dataList[0].hasOwnProperty(calcList[i])) {
				dataList[0][calcList[i]] = 0;
			};
		});
	};

	return dataList
};

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
    chart.addLabel('28%', '30%', 'No data! please check the following:', 'left', '12');
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
//set opacity of chart line
function setLineThickness(graph, lineThickness) {
  var className = "amcharts-graph-" + graph.id;
  var items = document.getElementsByClassName( className );
  if ( undefined === items )
    return;
  for ( var x in items ) {
    if ( "object" !== typeof items[x] )
      continue;
    var path = items[x].getElementsByTagName( "path" )[ 0 ];
    if ( undefined !== path ){
      $(path).attr('stroke-width', lineThickness);
    }
  }
}

function render_chart(widget){
console.log(widget);
	var data;
	all_widgets[widget.id] = widget;
	data = makeData(widget);
	if(data.length > 0)
		$('#'+widget.id).parent().parent().children('header').children('span.title').html(widget.title+' <span style="font-size:14px;color:#d3d3d3;"> &nbsp;'+data[data.length-1]['date']+'</span>');
	var chart = AmCharts.makeChart(widget.id, {
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
	    "valueAxes": [],
	    "balloon": {
	        "borderThickness": 2,
	        "shadowAlpha": 0
	    },
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
	    "mouseWheelScrollEnabled": true,
	    "tapToActivate": false,
	    "panEventsEnabled": false,
	    "chartCursor": {
	        "pan": true,
	        "valueLineEnabled": true,
	        "valueLineBalloonEnabled": true,
	        "cursorAlpha":1,
	        "cursorColor":"#258cbb",
	        "limitToGraph":"g1",
	        "valueLineAlpha":0.2, 
	        "categoryBalloonDateFormat": 'MMM DD, YYYY JJ:NN'
	    },
	    
	    "categoryValue": "value",
	    "categoryAxis": {
	        "parseDates": true,
	        "dashLength": 1,
	        "minorGridEnabled": true
	    },
	    "export": {
	        "enabled": true,
	        "position": "bottom-right",
          "exportTitles": true
	    },
	    "listeners":[{
	    	"event": "rendered",
	    	"method": function(e){
	    		var curtain = $('#'+widget.id).parent().children('.curtain');
	    		curtain.remove();
	    	}
	    }],
	     "dataProvider": data,
	     "legend": {
	         "useGraphSettings": true,
	         "position": "bottom",
	         "marginTop": 0,
	         "marginBottom": 0, 
           "autoMargins": false, 
           "verticalGap": 0,
           "fontSize": 10,
           "spacing": 5,
           "marginLeft": 5,
           "marginRight": 5,
           "markerLabelGap": 2, 
           "markerSize": 10, 
           "valueWidth": 40,
           "listeners": [
            {
              "event": "rollOverItem", 
              "method": function (event) {
                setLineThickness(event.chart.graphs[event.dataItem.index], 5);
              }
            },
            {
              "event": "rollOutItem", 
              "method": function (event) {
                setLineThickness(event.chart.graphs[event.dataItem.index], 2);
              }
            }
           ]
	       },
	     "guides": []

	});

	//if empty gracefully handle

	if(AmCharts.checkEmptyData(chart)){
		return
	};
	//speed check
	
	chart.dataDateFormat = "YYYY-MM-DD JJ:NN";
	chart.categoryField = "date";

  //add highlight on hover
  //add chart event listener
  chart.timeout;
  chart.addListener( "rollOverGraph", function( event ) {
    setLineThickness( event.graph, 5 );
  } );
  chart.addListener( "rollOutGraph", function( event ) {
    setLineThickness( event.graph, 2 );
  } );

	var categoryAxis = chart.categoryAxis;
	var axisSet = false;
	var axisId, factor;
	categoryAxis.parseDates = true;
	categoryAxis.minPeriod = "mm";
	var min, max;
	var position = 'left';
	if (data.length > 0) {
		var prop_lst = Object.keys(data[0]);
    console.log(prop_lst);
		for (var i = 0; i < prop_lst.length; i++){
			if (prop_lst[i] == 'date' || prop_lst[i] == 'lineColor'){
				continue;
			};
			graph = new AmCharts.AmGraph();
			graph.valueField = prop_lst[i];
			graph.showBalloon = true;
			graph.lineColor = "#a9ec49";
			graph.fixedColumnWidth = 5;


			if (widget.data[prop_lst[i]] != null && prop_lst[i].split('-')[0] != 'raw_sensors' && prop_lst[i].split('-')[0] != 'paw') {
				var axisTitle = '';
				factor = Math.ceil(chart.valueAxes.length / 2) -1;
				graph.title = widget.data[prop_lst[i]].title;
				graph.lineColor = widget.data[prop_lst[i]].value[0].lineColor;
				graph.lineThickness = 2;
				graph.type = widget.data[prop_lst[i]].value[0].type;
				graph.balloonText = "[[title]]<br/><b style='font-size: 100%'>[[value]]</b>"
				
				for (var j=0;j< chart.valueAxes.length;j++){
					if (chart.valueAxes[j].id == prop_lst[i]) {
						axisSet = true;
						axisId = chart.valueAxes[j].id;
					};
				};
				if (chart.valueAxes.length % 2 == 0) {
					position = 'right';
				}else{
					position = 'left';
				};
				if (prop_lst[i].split('-')[0] === 'chilling_portions') {
					axisTitle = 'Chilling Portions';
				}else if (prop_lst[i].split('-')[0] === 'chilling_hours'){
					axisTitle = 'Chilling Hours';
				}else if (prop_lst[i].split('-')[0] === 'degree_days'){
					axisTitle = 'Degree Days';
				}else if (prop_lst[i].split('-')[0] === 'evapo'){
					axisTitle = 'ETO [mm]';
				}else if (prop_lst[i].split('-')[0] === 'dew_point') {
					axisTitle = 'Dew Point [C]';
				};
				var valueAxis = new AmCharts.ValueAxis();
				if (!axisSet) {
					if (widget.data[prop_lst[i]].params.axes != null) {
						min = parseInt(widget.data[prop_lst[i]].params.axes.min);
						max = parseInt(widget.data[prop_lst[i]].params.axes.max);
						valueAxis.id = prop_lst[i];
						valueAxis.title = axisTitle;
						valueAxis.position = position;
						valueAxis.offset = 60*factor;
						valueAxis.minimum = min;
						valueAxis.maximum = max;
						valueAxis.strictMinMax =true;
						valueAxis.gridAlpha = 0;
						valueAxis.axisAlpha = 1;
						valueAxis.axisColor = graph.lineColor;
						chart.addValueAxis(valueAxis);
						graph.valueAxis = valueAxis.id;
					}else{
						valueAxis.id = prop_lst[i];
						valueAxis.title = axisTitle;
						valueAxis.position = position;
						valueAxis.offset = 60*factor;
						valueAxis.gridAlpha = 0;
						valueAxis.axisAlpha = 1;
						valueAxis.axisColor = graph.lineColor;
						chart.addValueAxis(valueAxis);
						graph.valueAxis = valueAxis.id;
					};	
				}else{
					graph.valueAxis = axisId;
				};
									

				if (graph.type == 'column'){
					graph.fillAlphas = 1;
					graph.behindColumns = true;
					graph.clustered = true;
				};
			};

			if (prop_lst[i].split("-")[0] == 'raw_sensors'){
				var  graphTitleID = widget.data.raw_sensors.value[prop_lst[i].split('-')[1]][0].label_id;
				var graphTitleSuffix = widget.data.raw_sensors.value[prop_lst[i].split('-')[1]][0].suffix;
				graph.title = widget.data.raw_sensors.params.labels[graphTitleID] +' '+ graphTitleSuffix;
				graph.balloonText = "[[title]]<br/><b style='font-size: 100%'>[[value]]</b>"
				factor = Math.ceil(chart.valueAxes.length / 2) -1;
				graph.lineColor = getRandomColor();
				graph.lineThickness = 2;
				if (widget.data.raw_sensors.value[prop_lst[i].split('-')[1]][0].lineColor != '') {
					graph.lineColor = widget.data.raw_sensors.value[prop_lst[i].split('-')[1]][0].lineColor;
				};
				axisSet = false;

				for (var j=0;j< chart.valueAxes.length;j++){
					if (chart.valueAxes[j].id == widget.data.raw_sensors.value[prop_lst[i].split('-')[1]][0].axis_id) {
						axisSet = true;
						axisId = chart.valueAxes[j].id;
					};
				};
				if (chart.valueAxes.length % 2 == 0) {
					position = 'right';
				}else{
					position = 'left';
				};
				var valueAxis = new AmCharts.ValueAxis();
				if (!axisSet) {
					if (widget.data.raw_sensors.params.axes != null) {
						min = parseInt(widget.data.raw_sensors.params.axes.min);
						max = parseInt(widget.data.raw_sensors.params.axes.max);
						valueAxis.id = widget.data.raw_sensors.value[prop_lst[i].split('-')[1]][0].axis_id;
						valueAxis.title = widget.data.raw_sensors.value[prop_lst[i].split('-')[1]][0].axis_name;
						valueAxis.position = position;
						valueAxis.offset = 60*factor;
						valueAxis.minimum = min;
						valueAxis.maximum = max;
						valueAxis.strictMinMax =true;
						valueAxis.gridAlpha = 0;
						valueAxis.axisAlpha = 1;
						valueAxis.axisColor = graph.lineColor;
						chart.addValueAxis(valueAxis);
						graph.valueAxis = valueAxis.id;
					}else{
						valueAxis.id = widget.data.raw_sensors.value[prop_lst[i].split('-')[1]][0].axis_id;
						valueAxis.title = widget.data.raw_sensors.value[prop_lst[i].split('-')[1]][0].axis_name;
						valueAxis.position = position;
						valueAxis.offset = 60*factor;
						valueAxis.gridAlpha = 0;
						valueAxis.axisAlpha = 1;
						valueAxis.axisColor = graph.lineColor;
						chart.addValueAxis(valueAxis);
						graph.valueAxis = valueAxis.id;
					};		
				}else{
					graph.valueAxis = axisId;
				};
				
				graph.type = widget.data.raw_sensors.value[prop_lst[i].split('-')[1]][0].type;
				if (graph.type == 'column'){
					graph.fillAlphas = 1;
					graph.behindColumns = true;
					graph.clustered = true;
				};
				
				// value on bar
				if (widget.data.raw_sensors.value[prop_lst[i].split('-')[1]][0].valueOnBar){
					console.log(widget.data.raw_sensors.value[prop_lst[i].split('-')[1]][0].valueOnBar);
					graph.labelText = "[[value]]";
					graph.labelPosition = "top";
					graph.labelRotation = 270;
					graph.color = "#000000";
					graph.labelFunction = function (item) {
						return item.values.value
					};
				};
				// graph.valueAxis = widget.data.raw_sensors.value[prop_lst[i].split('-')[1]][0].sensor;
				
			};

			if (prop_lst[i].split("-")[0] == 'ex_ec'){
				graph.title = widget.data.ex_ec.value[prop_lst[i].split('-')[1]][0].name;
				graph.balloonText = "[[title]]<br/><b style='font-size: 100%'>[[value]]</b>"
				factor = Math.ceil(chart.valueAxes.length / 2) -1;
				graph.lineColor = getRandomColor();
				graph.lineThickness = 2;
				if (widget.data.ex_ec.value[prop_lst[i].split('-')[1]][0].lineColor != '') {
					graph.lineColor = widget.data.ex_ec.value[prop_lst[i].split('-')[1]][0].lineColor;
				};
				axisSet = false;

				for (var j=0;j< chart.valueAxes.length;j++){
					if (chart.valueAxes[j].id == widget.data.ex_ec.value[prop_lst[i].split('-')[1]][0].sensor) {
						axisSet = true;
						axisId = chart.valueAxes[j].id;
					};
				};
				if (chart.valueAxes.length % 2 == 0) {
					position = 'right';
				}else{
					position = 'left';
				};
				var valueAxis = new AmCharts.ValueAxis();
				if (!axisSet) {
					if (widget.data.ex_ec.params.axes != null) {
						min = parseInt(widget.data.ex_ec.params.axes.min);
						max = parseInt(widget.data.ex_ec.params.axes.max);
						valueAxis.id = widget.data.ex_ec.value[prop_lst[i].split('-')[1]][0].sensor;
						valueAxis.title = 'Saturation Ex EC dS/m';
						valueAxis.position = position;
						valueAxis.offset = 60*factor;
						valueAxis.minimum = min;
						valueAxis.maximum = max;
						valueAxis.strictMinMax =true;
						valueAxis.gridAlpha = 0;
						valueAxis.axisAlpha = 1;
						valueAxis.axisColor = graph.lineColor;
						chart.addValueAxis(valueAxis);
						graph.valueAxis = valueAxis.id;
					}else{
						valueAxis.id = widget.data.ex_ec.value[prop_lst[i].split('-')[1]][0].sensor;
						valueAxis.title = 'Saturation Ex EC dS/m';
						valueAxis.position = position;
						valueAxis.offset = 60*factor;
						valueAxis.gridAlpha = 0;
						valueAxis.axisAlpha = 1;
						valueAxis.axisColor = graph.lineColor;
						chart.addValueAxis(valueAxis); 
						graph.valueAxis = valueAxis.id;
					};		
				}else{
					graph.valueAxis = axisId;
				};
				
				// graph.type = widget.data.ex_ec.value[prop_lst[i].split('-')[1]][0].type;
				if (graph.type == 'column'){
					graph.fillAlphas = 1;
					graph.behindColumns = true;
					graph.clustered = true;
				};

				// graph.valueAxis = widget.data.ex_ec.value[prop_lst[i].split('-')[1]][0].sensor;
				
			};

      if (prop_lst[i].split("-")[0] == 'voltage'){
        graph.title = widget.data.voltage.value[prop_lst[i].split('-')[1]][0].name;
        graph.balloonText = "[[title]]<br/><b style='font-size: 100%'>[[value]]</b>"
        factor = Math.ceil(chart.valueAxes.length / 2) -1;
        graph.lineColor = getRandomColor();
        graph.lineThickness = 2;
        // if (widget.data.voltage.value[prop_lst[i].split('-')[1]][0].lineColor != '') {
        //   graph.lineColor = widget.data.voltage.value[prop_lst[i].split('-')[1]][0].lineColor;
        // };
        axisSet = false;

        for (var j=0;j< chart.valueAxes.length;j++){
          if (chart.valueAxes[j].id == widget.data.voltage.value[prop_lst[i].split('-')[1]][0].sensor) {
            axisSet = true;
            axisId = chart.valueAxes[j].id;
          };
        };
        if (chart.valueAxes.length % 2 == 0) {
          position = 'right';
        }else{
          position = 'left';
        };
        var valueAxis = new AmCharts.ValueAxis();
        if (!axisSet) {
          if (widget.data.voltage.params.axes != null) {
            min = parseInt(widget.data.voltage.params.axes.min);
            max = parseInt(widget.data.voltage.params.axes.max);
            valueAxis.id = widget.data.voltage.value[prop_lst[i].split('-')[1]][0].sensor;
            valueAxis.title = '';
            valueAxis.position = position;
            valueAxis.offset = 60*factor;
            valueAxis.minimum = min;
            valueAxis.maximum = max;
            valueAxis.strictMinMax =true;
            valueAxis.gridAlpha = 0;
            valueAxis.axisAlpha = 1;
            valueAxis.axisColor = graph.lineColor;
            chart.addValueAxis(valueAxis);
            graph.valueAxis = valueAxis.id;
          }else{
            valueAxis.id = widget.data.voltage.value[prop_lst[i].split('-')[1]][0].sensor;
            valueAxis.title = '';
            valueAxis.position = position;
            valueAxis.offset = 60*factor;
            valueAxis.gridAlpha = 0;
            valueAxis.axisAlpha = 1;
            valueAxis.axisColor = graph.lineColor;
            chart.addValueAxis(valueAxis); 
            graph.valueAxis = valueAxis.id;
          };    
        }else{
          graph.valueAxis = axisId;
        };
        
        if (graph.type == 'column'){
          graph.fillAlphas = 1;
          graph.behindColumns = true;
          graph.clustered = true;
        };        
      };

			if (prop_lst[i].split("-")[0] === 'paw'){
				var paw_sensor = widget.data.paw.value[prop_lst[i].split('-')[1]][0].sensor;
				graph.title = widget.data.paw.value[prop_lst[i].split('-')[1]][0].name;
				graph.balloonText = "[[title]]<br/><b style='font-size: 100%'>[[value]]</b>"
				factor = Math.ceil(chart.valueAxes.length / 2) -1;
				graph.lineColor = getRandomColor();
				graph.lineThickness = 2;
				if (widget.data.paw.value[prop_lst[i].split('-')[1]][0].lineColor != ''){
					graph.lineColor = widget.data.paw.value[prop_lst[i].split('-')[1]][0].lineColor;
				};

				if (!widget.data.paw.params.avg){
					var graph_title = widget.data.paw.params.pawFields[paw_sensor].label;
					var line_color = widget.data.paw.params.pawFields[paw_sensor].color;
					if (graph_title != undefined) {
						graph.title = graph_title
					}
					if (line_color != undefined){
						graph.lineColor = '#'+line_color
					}
				}

				axisSet = false;
				for (var j=0;j< chart.valueAxes.length;j++){
					if (chart.valueAxes[j].id == 'paw') {
						axisSet = true;
					};
				};
				if (chart.valueAxes.length % 2 == 0) {
					position = 'right';
				}else{
					position = 'left';
				};
				var valueAxis = new AmCharts.ValueAxis();
				if (!axisSet) {
					if (widget.data.paw.params.axes != null) {
						min = parseInt(widget.data.paw.params.axes.min);
						max = parseInt(widget.data.paw.params.axes.max);
						valueAxis.id = 'paw'
						valueAxis.title = 'PAW VWC%';
						valueAxis.position = position;
						valueAxis.offset = 60*factor;
						valueAxis.minimum = min;
						valueAxis.maximum = max;
						valueAxis.strictMinMax = true;
						valueAxis.gridAlpha = 0;
						valueAxis.axisAlpha = 1;

						valueAxis.guides = [
			       				{
					       			"fillAlpha": 1,
					       			"value": 0,
					       			"toValue": 30,
					       			"fillColor": "#ffb3ba",
					       			// "lineColor": "#FF0000",
					       			// "lineAlpha": "1"
			       				},{
					       			"fillAlpha": 1,
					       			"value": 30,
					       			"toValue": 70,
					       			"fillColor": "#ffffba",
					       			// "lineColor": "#FFA500",
					       			// "lineAlpha": "1"
			       				},{
					       			"fillAlpha": 1,
					       			"value": 70,
					       			"toValue": 100,
					       			"fillColor": "#baffc9",
					       			// "lineColor": "#008000",
					       			// "lineAlpha": "1"
			       				},{
					       			"fillAlpha": 1,
					       			"value": 100,
					       			"toValue": 200,
					       			"fillColor": "#6ec0ff",
					       			// "lineColor": "#0000FF",
					       			// "lineAlpha": "1"
			       				}
							];
						valueAxis.axisColor = graph.lineColor;
						chart.addValueAxis(valueAxis);
						graph.valueAxis = valueAxis.id;
					}else{
						valueAxis.id = 'paw';
						valueAxis.title = 'PAW VWC%';
						valueAxis.position = position;
						valueAxis.offset = 60*factor;
						valueAxis.gridAlpha = 0;
						valueAxis.axisAlpha = 1;
						valueAxis.strictMinMax = true;
						valueAxis.guides = [
			       				{
					       			"fillAlpha": 1,
					       			"value": 0,
					       			"toValue": 30,
					       			"fillColor": "#ffb3ba",
					       			// "lineColor": "#FF0000",
					       			// "lineAlpha": "1"
			       				},{
					       			"fillAlpha": 1,
					       			"value": 30,
					       			"toValue": 70,
					       			"fillColor": "#ffffba",
					       			// "lineColor": "#FFA500",
					       			// "lineAlpha": "1"
			       				},{
					       			"fillAlpha": 1,
					       			"value": 70,
					       			"toValue": 100,
					       			"fillColor": "#baffc9",
					       			// "lineColor": "#008000",
					       			// "lineAlpha": "1"
			       				},{
					       			"fillAlpha": 1,
					       			"value": 100,
					       			"toValue": 200,
					       			"fillColor": "#6ec0ff",
					       			// "lineColor": "#0000FF",
					       			// "lineAlpha": "1"
			       				}
							];
						valueAxis.axisColor = graph.lineColor;
						chart.addValueAxis(valueAxis);
						graph.valueAxis = valueAxis.id;
					};							
				}else{
					graph.valueAxis = 'paw';
				};
				graph.type = widget.data.paw.value[prop_lst[i].split('-')[1]][0].type;
				if (graph.type == 'column'){
					graph.fillAlphas = 1;
					graph.behindColumns = true;
					graph.clustered = true;
				};
			};
			
			chart.addGraph(graph);

		};
		
		chart.validateData();	
	};
  //Add hover events to legend as well
  // chart.legend.addListener("rollOverItem", function (event) {
  //   console.log('legened hovered');
  //   setLineThickness( event.chart.graphs[event.dataItem.index], 3 );
  // });
  
  // chart.legend.addListener("rollOutItem", function (event) {
  //   setLineThickness( event.chart.graphs[event.dataItem.index], 2 );
  // });
};


function updatePAWFields() {
	$('div.attribs').empty();
	if (!$('#checkbox-main-paw-avg').prop('checked')) {
		for (i = 0;i < $main_paw_sensors.length;i++){
			var itemLabel = $('#ms-main-paw option[value="'+$main_paw_sensors[i]+'"]').text();
			var labelID = $('#ms-main-paw option[value="'+$main_paw_sensors[i]+'"]').val();

			var elementStringFC = $('<div class="row top-buffer-5">\
			<div class="control-label col-lg-12 help-block '+labelID+'">'+itemLabel+'</div>\
			<label for="'+labelID+'" class="col-lg-2 control-label top-buffer-5 '+labelID+'">Field Capacity</label>\
			<div class="col-lg-4"><input type="text" class="form-control top-buffer-5 input-sm '+labelID+' paw-fc" id="" /></div>\
			<label for="'+labelID+'" class=" col-lg-2 control-label top-buffer-5 '+labelID+'">Wilting Point</label>\
			<div class="col-lg-4"><input type="text" class="form-control col-sm-4 top-buffer-5  input-sm '+labelID+' paw-wp" id="" /></div></div>');

			var str = $('<div class="row"><label for="'+labelID+'" class=" col-lg-2 control-label top-buffer '+labelID+'">Label</label>\
			<div class="col-lg-4"><input type="text" value='+itemLabel+' class="form-control input-sm '+labelID+' paw-label" id="" />\
			</div><label for="'+labelID+'" class=" col-lg-2 control-label top-buffer '+labelID+'">Color</label>\
			<div class="col-lg-4 '+labelID+' " id="'+labelID+'"></div>');
			// <input id="paw-color" value="ffffba" class="jscolor form-control '+labelID+' input-sm paw-color"></div>

			$('#paw div.attribs').append(elementStringFC);
			$('#paw div.attribs').append(str);
			var color_input = document.createElement('INPUT');
			color_input.className = 'jscolor-input form-control input-sm paw-color '+labelID;
			pickers[labelID] = new jscolor(color_input, {'zIndex': 1052});
			document.getElementById(labelID).appendChild(color_input);
		};
		
	}else{
		$('div.attribs').empty();
		var elementStringFC = '<div class="form-group .main-paw-fc"><label for="main-paw-fc" class="col-lg-2 col-sm-2 control-label">Field Capacity</label><div class="col-lg-4"><input type="text" class="form-control input-sm" id="main-paw-fc" placeholder="FC"><p class="help-block"></p></div></div>';
		var elementStringWP = '<div class="form-group .main-paw-wp"><label for="main-paw-wp" class="col-lg-2 col-sm-2 control-label">Wilting Point</label><div class="col-lg-4"><input type="text" class="form-control input-sm" id="main-paw-wp" placeholder="WP"><p class="help-block"></p></div></div>';
        $('#paw div.attribs').append(elementStringFC);
        $('#paw div.attribs').append(elementStringWP);
	};
};

function updatePAWFieldsValues () {
	$main_paw_fc = $('#main-paw-fc').val() == null ? 0: $('#main-paw-fc').val();
	$main_paw_wp = $('#main-paw-wp').val() == null ? 0: $('#main-paw-wp').val();;
	for(i = 0;i < $main_paw_sensors.length; i++){
		$pawFields[$main_paw_sensors[i]] = {
			'fc': $('.'+$main_paw_sensors[i]+'.paw-fc').val(),
			'wp': $('.'+$main_paw_sensors[i]+'.paw-wp').val(), 
			'label': $('input.'+$main_paw_sensors[i]+'.paw-label').val(),
			'color': $('input.'+$main_paw_sensors[i]+'.paw-color').val()
		};
	};	
};

function restorePAWFieldsValues (pawFieldsValues) {
	$.each(pawFieldsValues, function  (key, value) {
		$('input.'+key+'.'+'paw-fc').val(value.fc);
		$('input.'+key+'.'+'paw-wp').val(value.wp);
		$('input.'+key+'.'+'paw-label').val(value.label);
		if (pickers.hasOwnProperty(key) && value.color != undefined)
			pickers[key].fromString(value.color);
	});
};

function populateRawSensors (labels) {
	$('#ms-main-sensors-label-ctn').empty();
	$.each(labels, function (key, value) {
		var placeholder = $('#ms-main-sensors option[value="'+key+'"').text();
		$('#ms-main-sensors-label-ctn').append('<div class="col-sm-2 top-buffer-5 '+key+'"><label>Label</label></div>\
				<div class="col-sm-10 top-buffer-5 '+key+'">\
				<input type="text" class="form-control input-sm" id="'+key+'" value="'+value+'" placeholder="'+placeholder+'">\
				</div>');
	});
};

$(function(){
	$('#paw').on('change','.paw-fc', function (e){
		updatePAWFieldsValues();
	});
	$('#paw').on('change','.paw-wp', function (e){
		updatePAWFieldsValues();
	});
	$('#paw').on('change','#main-paw-fc', function (e){
		updatePAWFieldsValues();
	});
	$('#paw').on('change','#main-paw-wp', function (e){
		updatePAWFieldsValues();
	});
	$('#paw').on('change','input.paw-label', function (e) {
		updatePAWFieldsValues();
	});
	$('#paw').on('change','input.paw-color', function (e) {
		updatePAWFieldsValues();
	});
});

$('#checkbox-main-paw-avg').on('change', function (e){
	updatePAWFields();

});



var ms_main_sensors, ms_main_paw, s_main_cp, s_main_dd, s_main_ch, s_main_eto_t, s_main_eto_rh, s_main_eto_sr, s_main_eto_ws, s_main_dp_t, s_main_dp_rh;
var main_sensors_labels = {};
$(document).ready(function(){
	$options = $.map($("#ms-main-sensors option"), function (el, i) {
		return {'value':$(el).val(), 'text':$(el).text(), 'station': $(el).parent().attr('label')}
	});
	ms_main_sensors = $('#ms-main-sensors').kendoMultiSelect({
		select:  function(e){
			var dataItem = e.dataItem;
			$('#ms-main-sensors-label-ctn').append('<div class="col-sm-2 top-buffer-5 '+dataItem.value+'"><label>Label</label></div>\
				<div class="col-sm-10 top-buffer-5 '+dataItem.value+'">\
				<input type="text" class="form-control input-sm" id="'+dataItem.value+'" placeholder="'+dataItem.text+'">\
				</div>');

		}, 
		deselect: function(e){
			var dataItem = e.dataItem;
			$('#ms-main-sensors-label-ctn .'+dataItem.value).remove();
			if (main_sensors_labels.hasOwnProperty(dataItem.value)) {
				delete main_sensors_labels[dataItem.value];
			};
		},
		filter: 'contains',
    filtering: function (e) {

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
	})
	.data('kendoMultiSelect');
	$('#ms-main-sensors-label-ctn').on('change', 'input', function (e) {
		main_sensors_labels[$(this).attr('id')] = $(this).val();
	});
	
	ms_main_paw = $('#ms-main-paw').kendoMultiSelect({
		select: function (e) {
			var dataItem = e.dataItem;
			if ($('#checkbox-main-paw-avg').prop('checked')){
				return;
			};

			var elementStringFC = $('<div class="row top-buffer-5">\
			<div class="control-label col-lg-12 help-block '+dataItem.value+'">'+dataItem.text+'</div>\
			<label for="'+dataItem.value+'" class="col-lg-2 control-label top-buffer-5 '+dataItem.value+'">Field Capacity</label>\
			<div class="col-lg-4"><input type="text" class="form-control top-buffer-5 input-sm '+dataItem.value+' paw-fc" id="" /></div>\
			<label for="'+dataItem.value+'" class=" col-lg-2 control-label top-buffer-5 '+dataItem.value+'">Wilting Point</label>\
			<div class="col-lg-4"><input type="text" class="form-control col-sm-4 top-buffer-5  input-sm '+dataItem.value+' paw-wp" id="" /></div></div>');

			var str = $('<div class="row"><label for="'+dataItem.value+'" class=" col-lg-2 control-label top-buffer '+dataItem.value+'">Label</label>\
			<div class="col-lg-4"><input type="text" value='+dataItem.text+' class="form-control input-sm '+dataItem.value+' paw-label" id="" />\
			</div><label for="'+dataItem.value+'" class=" col-lg-2 control-label top-buffer '+dataItem.value+'">Color</label>\
			<div class="col-lg-4 '+dataItem.value+' " id="'+dataItem.value+'"></div>');
			// <input id="paw-color" value="ffffba" class="jscolor form-control '+dataItem.value+' input-sm paw-color"></div>

			$('#paw div.attribs').append(elementStringFC);
			$('#paw div.attribs').append(str);
			var color_input = document.createElement('INPUT');
			color_input.className = 'jscolor-input form-control input-sm paw-color '+dataItem.value;
			pickers[dataItem.value] = new jscolor(color_input, {'zIndex': 1052});
			document.getElementById(dataItem.value).appendChild(color_input);
			$main_paw_sensors.push(dataItem.value);
		},
		deselect: function (e) {
			var dataItem = e.dataItem;
			$('#paw div.attribs .'+dataItem.value).remove();
			if (pickers.hasOwnProperty(dataItem.value)){
				delete pickers[dataItem.value];	
			};
			if ($main_paw_sensors.indexOf(dataItem.value) != -1){
				var index = $main_paw_sensors.indexOf(dataItem.value);
				$main_paw_sensors.splice(index, 1);
			};
			if ($pawFields.hasOwnProperty(dataItem.value))
				delete $pawFields[dataItem.value];
		},
		filter: 'contains',
    filtering: function (e) {
      //custome filtering logic
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
	s_main_cp = $('#s-main-cp').kendoMultiSelect({
		maxSelectedItems: 1, 
		filter: 'contains',
    filtering: function (e) {
      //custome filtering logic
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
	s_main_dd = $('#s-main-dd').kendoMultiSelect({
		maxSelectedItems: 1, 
		filter: 'contains',
    filtering: function (e) {
      //custome filtering logic
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
	s_main_ch = $('#s-main-ch').kendoMultiSelect({
		maxSelectedItems: 1,
		filter: 'contains',
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
	s_main_eto_t = $('#s-main-eto-t').kendoMultiSelect({
		maxSelectedItems: 1,
		filter: 'contains',
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
	s_main_eto_rh = $('#s-main-eto-rh').kendoMultiSelect({
		maxSelectedItems: 1,
		filter: 'contains',
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
	s_main_eto_sr = $('#s-main-eto-sr').kendoMultiSelect({
		maxSelectedItems: 1,
		filter: 'contains',
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
	s_main_eto_ws = $('#s-main-eto-ws').kendoMultiSelect({
		maxSelectedItems: 1,
		filter: 'contains',
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
	s_main_dp_t = $('#s-main-dp-t').kendoMultiSelect({
		maxSelectedItems: 1,
		filter: 'contains',
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
	s_main_dp_rh = $('#s-main-dp-rh').kendoMultiSelect({
		maxSelectedItems: 1,
		filter: 'contains',
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
	// s_stat_station = $('#statmodal select.station').kendoMultiSelect({
	// 	maxSelectedItems: 1,
	// 	filter: 'contains'
	// }).data('kendoMultiSelect');
	// s_stat_sensor = $('#statmodal select.sensor').kendoMultiSelect({
	// 	maxSelectedItems: 1,
	// 	filter: 'contains'
	// }).data('kendoMultiSelect');



});

// $('#statmodal select.station').chosen({width:"100%", scroll_to_highlighted:false});
// $('#statmodal select.sensor').chosen({width:"100%", scroll_to_highlighted:false, disable_search:true});


// stat configuration modal 

$('#statmodal').on('show.bs.modal', function (e) {
	$invoker = $(e.relatedTarget);
	$id = $invoker.parent().parent().attr('id');
	if ($id in all_widgets) {
		station = all_widgets[$id].data.calc.params.station_id
		sensor = all_widgets[$id].data.calc.params.sensor;
		s_stat_station.value(station);
		s_stat_sensor.value(sensor);
		$('#statmodal select.station option:selected').removeAttr('selected');
		$('#statmodal select.sensor option:selected').removeAttr('selected');
		$('#statmodal select.station option[value="'+station+'"]').attr('selected', 'selected');
		$('#statmodal select.sensor option[value="'+sensor+'"]').attr('selected', 'selected');
	};
	
	$sensor = $('#statmodal select.station').val();
	// $sensor = s_stat_sensor.value()[0];
	$station_id = $('#statmodal select.station option:selected').attr('station');
	$station_name = $($invoker).text();
	$db = $('#statmodal select.station option').attr('db');
	$stat_data = $('#statmodal select.sensor').val();
	$station_elem = $('#statmodal select.station');
	$stat_data_elem = $('#statmodal select.sensor');
	$('#statmodal select.station').on('change', function (e) {
		e.stopImmediatePropagation();
		$station_elem = $(this);
		$station_id = $('#statmodal select.station option:selected').attr('station');
		$sensor = $('#statmodal select.station').val();
		$station_name = $(this).find('option:selected').parent().attr('label');

	});

	$('#statmodal select.sensor').on('change', function (e) {
		e.stopImmediatePropagation();
		$stat_data_elem = $(this);
		$stat_data = $(this).val();
	});
	// s_stat_sensor.bind('change', function (e) {
	// 	$stat_data_elem = $(this);
	// 	$stat_data = this.value();
	// })

	$('#statmodal button.submit').on('click', function  (e) {
		e.stopImmediatePropagation();
		elem = notify_man('info', 'Widget loading...');
		$invoker.children().first().text($station_name);
		$invoker.parent().next().children('p').text($stat_data_elem.find('option:selected').text());
		$db = $station_elem.find('option:selected').attr('db');
		data = {'calc':{'params':{'db':$db, 
								'station_id':$station_id,
								'station_name':$station_name,
								'sensor_name':$stat_data_elem.find('option:selected').text(),
								'sensor':$sensor,
								'data':$stat_data}, 'value':null}}
		widget = new Widget($invoker.parent().parent().attr('id'), '99', 'stat', 'stat', 'None', data);
		ajax_request(render_stat, widget, elem);

		$('#statmodal').modal('hide');
	});
	$('#statmodal button.remove').on('click', function (e) {
		e.stopImmediatePropagation();
		if(!confirm('Are you sure you want to delete widget permenantly ?')){
			return
		};
		$invoker.parent().parent().parent().remove();

		var request = $.ajax({
			  method: "POST",
			  url: url_remove_widget,
			  data: JSON.stringify({'id':$invoker.parent().parent().attr('id')}), 
			  dataType: 'json'
			}).done(function(data) {
	    		if (data.success){
	    			notify_auto('success', 5, 'Widget successfully removed.');
	    		}else{
	    			notify_auto('danger', 5, 'Failed to remove widget.');
	    		}
	  		}).fail(function(msg){
	  			notify_auto('danger', 5, 'Failed to remove widget.');
	  	});
		$('#statmodal').modal('hide');
	});

	return;
});

//saturation ex ec populate form 
function populateExEC(exECParams) {
	$('#ex-ec-ctn').remove();
	var container = $('<div id="ex-ec-ctn"></div>');
	$('#btn-ex-ec-ctn').before(container);
	$sat_ex_ec_sensors = exECParams;
	for (var i= 0; i<exECParams.length; i++){
		$('#btn-ex-ec-ctn').before(container);
		if (satExECLst.indexOf(exECParams[i].inputID)===-1){
			satExECLst.push(exECParams[i].inputID);	
		}
		var NewLabel = '<div class="col-md-2 col-sm-2 col-lg-2 top-buffer"><label class="control-label"><input class="ex-ec" name="sample-checkbox-01" id="checkbox-ex-ec-'+exECParams[i].inputID+'" value="1" type="checkbox" checked /> Sensor</label></div>'
		var NewSelect = '<div class="col-md-10 col-sm-10 col-lg-10 top-buffer"><select class="form-control ex-ec input-sm m-bot5" id="ms-ex-ec-'+exECParams[i].inputID+'"></select></div>';
		var NewText = '<div class="col-lg-2 col-md-2 col-sm-2"><label for="ex-ec-offset-'+exECParams[i].inputID+'" class="control-label">Offset </label></div><div class="col-lg-4 col-md-4 col-sm-4"><input type="text" class="form-control input-sm ex-ec" id="ex-ec-offset-'+exECParams[i].inputID+'" placeholder=""></div>';
		var NewSaturation = '<div class="col-lg-2 col-md-2 col-sm-2"><label for="ex-ec-saturation-'+exECParams[i].inputID+'" class="control-label">Saturation </label></div><div class="col-lg-4 col-md-4 col-sm-4"><input type="text" class="form-control input-sm ex-ec" id="ex-ec-saturation-'+exECParams[i].inputID+'" placeholder=""></div>';
		var NewAxisLabel = '<div class="col-lg-2 col-md-2 col-sm-2 top-buffer-5"><label for="ex-ec-label-'+exECParams[i].inputID+'" class="control-label">Label </label></div><div class="col-lg-10 col-md-10 col-sm-10 top-buffer-5"><input type="text" class="form-control input-sm ex-ec" id="ex-ec-label-'+exECParams[i].inputID+'" placeholder=""></div>';
		$('#checkbox-ex-ec-'+exECParams[i].inputID).prop('checked', true);
		container.append(NewLabel);
		container.append(NewSelect);
		container.append(NewText);
		container.append(NewSaturation);
		container.append(NewAxisLabel);
		var dataSource = new kendo.data.DataSource({
			data: $options,
			group: {field: "station"}
		});
		$('#ms-ex-ec-'+exECParams[i].inputID).kendoMultiSelect({
			filter: 'contains',
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
      },
			dataSource: dataSource,
			dataValueField: 'value',
			dataTextField: 'text'
		})
		.data('kendoMultiSelect')
		.value(exECParams[i].sensors);
		$('#ex-ec-offset-'+exECParams[i].inputID).val(exECParams[i].offset);
		$('#ex-ec-saturation-'+exECParams[i].inputID).val(exECParams[i].saturation);
		$('#ex-ec-label-'+exECParams[i].inputID).val(exECParams[i].label);
	}
}
//populate voltage calc form
function populateVoltageForm(voltageFormValues){
  $('#voltage-ctn').remove();
  var voltageCtn = $('<div id="voltage-ctn"></div>');
  $('#btn-voltage-ctn').before(voltageCtn);
  // voltageSensors = voltageFormValues;
  for(var i = 0; i < voltageFormValues.length; i++){
    // $('#btn-voltage-ctn').before(voltageCtn);
    if(voltageLst.indexOf(voltageFormValues[i].inputID) ===-1)
      voltageLst.push(voltageFormValues[i].inputID);
    var voltageHTML = '\
      <div class="col-md-2 col-sm-2 col-lg-2 top-buffer">\
        <label class="control-label">\
          <input class="voltage" name="voltage-checkbox" id="voltage-checkbox-'+voltageFormValues[i].inputID+'" value="1" type="checkbox"/>\
            Sensor\
        <label/>\
      </div>\
      <div class="col-md-10 col-sm-10 col-lg-10 top-buffer">\
        <select class="form-control voltage input-sm m-bot5" id="ms-voltage-'+voltageFormValues[i].inputID+'">\
        </select>\
      </div>\
      <div class="col-lg-2 col-md-2 col-sm-2">\
        <label for="voltage-equation-'+voltageFormValues[i].inputID+'" class="control-label">Equation</label>\
      </div>\
      <div class="col-lg-10 col-md-10 col-sm-10">\
        <input type="text" class="form-control input-sm voltage" id="voltage-equation-'+voltageFormValues[i].inputID+'" placeholder="i.e. x^2+3*x+1">\
      </div>\
      <div class="col-lg-2 col-md-2 col-sm-2 top-buffer-5">\
        <label for="voltage-label-'+voltageFormValues[i].inputID+'" class="control-label">Label </label>\
      </div>\
      <div class="col-lg-10 col-md-10 col-sm-10">\
        <input type="text" class="form-control input-sm voltage top-buffer-5" id="voltage-label-'+voltageFormValues[i].inputID+'" placeholder="">\
      </div>\
    ';
    $('#voltage-ctn').append(voltageHTML);
    $('#voltage-checkbox-'+voltageFormValues[i].inputID).prop('checked', true);
    var voltageSelectDataSource = new kendo.data.DataSource({
      data: $options,
      group: {field: 'station'}
    });
    $('#ms-voltage-'+voltageFormValues[i].inputID).kendoMultiSelect({
      filter: 'contains',
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
      },
      dataSource: voltageSelectDataSource,
      dataValueField: 'value',
      dataTextField: 'text'
    })
    .data('kendoMultiSelect')
    .value(voltageFormValues[i].sensor);
    $('#voltage-equation-'+voltageFormValues[i].inputID).val(voltageFormValues[i].equation);
    $('#voltage-label-'+voltageFormValues[i].inputID).val(voltageFormValues[i].label);
  }
}

// fixed axis
$(function(){
	$main_sensors_check_axis = $('#checkbox-main-sensors-axis').prop('checked', true);
	$main_sensors_axis_min = $('#main-sensors-axis-min').val();
	$main_sensors_axis_max = $('#main-sensors-axis-max').val();
	$main_sensors_axes = null;

	if (!$main_sensors_check_axis) {
		$('#main-sensors-axis-min').attr('disabled', 'disabled');
		$('#main-sensors-axis-max').attr('disabled', 'disabled');
		$main_sensors_axes = null;		
	}else{
		$main_sensors_axes = {'min':$main_sensors_axis_min, 'max':$main_sensors_axis_max};
		$('main-sensors-axis-min').removeAttr('disabled');
		$('main-sensors-axis-max').removeAttr('disabled');
	};
	$('#checkbox-main-sensors-axis').on('change', function (e) {
		if ($(this).prop('checked')) {
			$('#main-sensors-axis-min').removeAttr('disabled');
			$('#main-sensors-axis-max').removeAttr('disabled');
			$main_sensors_axis_min = $('#main-sensors-axis-min').val();
			$main_sensors_axis_max = $('#main-sensors-axis-max').val();
			$main_sensors_axes = {'min':$main_sensors_axis_min, 'max':$main_sensors_axis_max};
		}else{
			$('#main-sensors-axis-min').attr('disabled', 'disabled');
			$('#main-sensors-axis-max').attr('disabled', 'disabled');
			$main_sensors_axes = null;
		};	
	});
	$('#main-sensors-axis-min').on('change', function (e) {
		$main_sensors_axis_min = $(this).val();
		$main_sensors_axes.min = $main_sensors_axis_min;
	});
	$('#main-sensors-axis-max').on('change', function (e) {
		$main_sensors_axis_max = $(this).val();
		$main_sensors_axes.max = $main_sensors_axis_max;
	});

	$paw_check_axis = $('#checkbox-paw-axis').prop('checked', true);
	$paw_axis_min = $('#paw-axis-min').val();
	$paw_axis_max = $('#paw-axis-max').val();
	$paw_axes = null;

	if (!$paw_check_axis) {
		$('#paw-axis-min').attr('disabled', 'disabled');
		$('#paw-axis-max').attr('disabled', 'disabled');
		$paw_axes = null;		
	}else{
		$paw_axes = {'min':$paw_axis_min, 'max':$paw_axis_max};
		$('paw-axis-min').removeAttr('disabled');
		$('paw-axis-max').removeAttr('disabled');
	};
	$('#checkbox-paw-axis').on('change', function (e) {
		if ($(this).prop('checked')) {
			$('#paw-axis-min').removeAttr('disabled');
			$('#paw-axis-max').removeAttr('disabled');
			$paw_axis_min = $('#paw-axis-min').val();
			$paw_axis_max = $('#paw-axis-max').val();
			$paw_axes = {'min':$paw_axis_min, 'max':$paw_axis_max};
		}else{
			$('#paw-axis-min').attr('disabled', 'disabled');
			$('#paw-axis-max').attr('disabled', 'disabled');
			$paw_axes = null;
		};	
	});
	$('#paw-axis-min').on('change', function (e) {
		$paw_axis_min = $(this).val();
		$paw_axes.min = $paw_axis_min;
	});
	$('#paw-axis-max').on('change', function (e) {
		$paw_axis_max = $(this).val();
		$paw_axes.max = $paw_axis_max;
	});

	$cp_check_axis = $('#checkbox-cp-axis').prop('checked', true);
	$cp_axis_min = $('#cp-axis-min').val();
	$cp_axis_max = $('#cp-axis-max').val();
	$cp_axes = null;

	if (!$cp_check_axis) {
		$('#cp-axis-min').attr('disabled', 'disabled');
		$('#cp-axis-max').attr('disabled', 'disabled');
		$cp_axes = null;		
	}else{
		$cp_axes = {'min':$cp_axis_min, 'max':$cp_axis_max};
		$('cp-axis-min').removeAttr('disabled');
		$('cp-axis-max').removeAttr('disabled');
	};
	$('#checkbox-cp-axis').on('change', function (e) {
		if ($(this).prop('checked')) {
			$('#cp-axis-min').removeAttr('disabled');
			$('#cp-axis-max').removeAttr('disabled');
			$cp_axis_min = $('#cp-axis-min').val();
			$cp_axis_max = $('#cp-axis-max').val();
			$cp_axes = {'min':$cp_axis_min, 'max':$cp_axis_max};
		}else{
			$('#cp-axis-min').attr('disabled', 'disabled');
			$('#cp-axis-max').attr('disabled', 'disabled');
			$cp_axes = null;
		};	
	});
	$('#cp-axis-min').on('change', function (e) {
		$cp_axis_min = $(this).val();
		$cp_axes.min = $cp_axis_min;
	});
	$('#cp-axis-max').on('change', function (e) {
		$cp_axis_max = $(this).val();
		$cp_axes.max = $cp_axis_max;
	});

	$dd_check_axis = $('#checkbox-dd-axis').prop('checked', true);
	$dd_axis_min = $('#dd-axis-min').val();
	$dd_axis_max = $('#dd-axis-max').val();
	$dd_axes = null;

	if (!$dd_check_axis) {
		$('#dd-axis-min').attr('disabled', 'disabled');
		$('#dd-axis-max').attr('disabled', 'disabled');
		$dd_axes = null;		
	}else{
		$dd_axes = {'min':$dd_axis_min, 'max':$dd_axis_max};
		$('dd-axis-min').removeAttr('disabled');
		$('dd-axis-max').removeAttr('disabled');
	};
	$('#checkbox-dd-axis').on('change', function (e) {
		if ($(this).prop('checked')) {
			$('#dd-axis-min').removeAttr('disabled');
			$('#dd-axis-max').removeAttr('disabled');
			$dd_axis_min = $('#dd-axis-min').val();
			$dd_axis_max = $('#dd-axis-max').val();
			$dd_axes = {'min':$dd_axis_min, 'max':$dd_axis_max};
		}else{
			$('#dd-axis-min').attr('disabled', 'disabled');
			$('#dd-axis-max').attr('disabled', 'disabled');
			$dd_axes = null;
		};	
	});
	$('#dd-axis-min').on('change', function (e) {
		$dd_axis_min = $(this).val();
		$dd_axes.min = $dd_axis_min;
	});
	$('#dd-axis-max').on('change', function (e) {
		$dd_axis_max = $(this).val();
		$dd_axes.max = $dd_axis_max;
	});

	$ch_check_axis = $('#checkbox-ch-axis').prop('checked', true);
	$ch_axis_min = $('#ch-axis-min').val();
	$ch_axis_max = $('#ch-axis-max').val();
	$ch_axes = null;

	if (!$ch_check_axis) {
		$('#ch-axis-min').attr('disabled', 'disabled');
		$('#ch-axis-max').attr('disabled', 'disabled');
		$ch_axes = null;		
	}else{
		$ch_axes = {'min':$ch_axis_min, 'max':$ch_axis_max};
		$('ch-axis-min').removeAttr('disabled');
		$('ch-axis-max').removeAttr('disabled');
	};
	$('#checkbox-ch-axis').on('change', function (e) {
		if ($(this).prop('checked')) {
			$('#ch-axis-min').removeAttr('disabled');
			$('#ch-axis-max').removeAttr('disabled');
			$ch_axis_min = $('#ch-axis-min').val();
			$ch_axis_max = $('#ch-axis-max').val();
			$ch_axes = {'min':$ch_axis_min, 'max':$ch_axis_max};
		}else{
			$('#ch-axis-min').attr('disabled', 'disabled');
			$('#ch-axis-max').attr('disabled', 'disabled');
			$ch_axes = null;
		};	
	});
	$('#ch-axis-min').on('change', function (e) {
		$ch_axis_min = $(this).val();
		$ch_axes.min = $ch_axis_min;
	});
	$('#ch-axis-max').on('change', function (e) {
		$ch_axis_max = $(this).val();
		$ch_axes.max = $ch_axis_max;
	});
	$eto_check_axis = $('#checkbox-eto-axis').prop('checked', true);
	$eto_axis_min = $('#eto-axis-min').val();
	$eto_axis_max = $('#eto-axis-max').val();
	$eto_axes = null;

	if (!$eto_check_axis) {
		$('#eto-axis-min').attr('disabled', 'disabled');
		$('#eto-axis-max').attr('disabled', 'disabled');
		$eto_axes = null;		
	}else{
		$eto_axes = {'min':$eto_axis_min, 'max':$eto_axis_max};
		$('eto-axis-min').removeAttr('disabled');
		$('eto-axis-max').removeAttr('disabled');
	};
	$('#checkbox-eto-axis').on('change', function (e) {
		if ($(this).prop('checked')) {
			$('#eto-axis-min').removeAttr('disabled');
			$('#eto-axis-max').removeAttr('disabled');
			$eto_axis_min = $('#eto-axis-min').val();
			$eto_axis_max = $('#eto-axis-max').val();
			$eto_axes = {'min':$eto_axis_min, 'max':$eto_axis_max};
		}else{
			$('#eto-axis-min').attr('disabled', 'disabled');
			$('#eto-axis-max').attr('disabled', 'disabled');
			$eto_axes = null;
		};	
	});
	$('#eto-axis-min').on('change', function (e) {
		$eto_axis_min = $(this).val();
		$eto_axes.min = $eto_axis_min;
	});
	$('#eto-axis-max').on('change', function (e) {
		$eto_axis_max = $(this).val();
		$eto_axes.max = $eto_axis_max;
	});

	$dp_check_axis = $('#checkbox-dp-axis').prop('checked', true);
	$dp_axis_min = $('#dp-axis-min').val();
	$dp_axis_max = $('#dp-axis-max').val();
	$dp_axes = null;

	if (!$dp_check_axis) {
		$('#dp-axis-min').attr('disabled', 'disabled');
		$('#dp-axis-max').attr('disabled', 'disabled');
		$dp_axes = null;		
	}else{
		$dp_axes = {'min':$dp_axis_min, 'max':$dp_axis_max};
		$('dp-axis-min').removeAttr('disabled');
		$('dp-axis-max').removeAttr('disabled');
	};
	$('#checkbox-dp-axis').on('change', function (e) {
		if ($(this).prop('checked')) {
			$('#dp-axis-min').removeAttr('disabled');
			$('#dp-axis-max').removeAttr('disabled');
			$dp_axis_min = $('#dp-axis-min').val();
			$dp_axis_max = $('#dp-axis-max').val();
			$dp_axes = {'min':$dp_axis_min, 'max':$dp_axis_max};
		}else{
			$('#dp-axis-min').attr('disabled', 'disabled');
			$('#dp-axis-max').attr('disabled', 'disabled');
			$dp_axes = null;
		};	
	});
	$('#dp-axis-min').on('change', function (e) {
		$dp_axis_min = $(this).val();
		$dp_axes.min = $dp_axis_min;
	});
	$('#dp-axis-max').on('change', function (e) {
		$dp_axis_max = $(this).val();
		$dp_axes.max = $dp_axis_max;
	});

	$ex_ec_check_axis = $('#checkbox-ex-ec-axis').prop('checked', true);
	$ex_ec_axis_min = $('#ex-ec-axis-min').val();
	$ex_ec_axis_max = $('#ex-ec-axis-max').val();
	$ex_ec_axes = null;

	if (!$ex_ec_check_axis) {
		$('#ex-ec-axis-min').attr('disabled', 'disabled');
		$('#ex-ec-axis-max').attr('disabled', 'disabled');
		$ex_ec_axes = null;		
	}else{
		$ex_ec_axes = {'min':$ex_ec_axis_min, 'max':$ex_ec_axis_max};
		$('ex-ec-axis-min').removeAttr('disabled');
		$('ex-ec-axis-max').removeAttr('disabled');
	};
	$('#checkbox-ex-ec-axis').on('change', function (e) {
		if ($(this).prop('checked')) {
			$('#ex-ec-axis-min').removeAttr('disabled');
			$('#ex-ec-axis-max').removeAttr('disabled');
			$ex_ec_axis_min = $('#ex-ec-axis-min').val();
			$ex_ec_axis_max = $('#ex-ec-axis-max').val();
			$ex_ec_axes = {'min':$ex_ec_axis_min, 'max':$ex_ec_axis_max};
		}else{
			$('#ex-ec-axis-min').attr('disabled', 'disabled');
			$('#ex-ec-axis-max').attr('disabled', 'disabled');
			$ex_ec_axes = null;
		};	
	});
	$('#ex-ec-axis-min').on('change', function (e) {
		$ex_ec_axis_min = $(this).val();
		$ex_ec_axes.min = $ex_ec_axis_min;
	});
	$('#ex-ec-axis-max').on('change', function (e) {
		$ex_ec_axis_max = $(this).val();
		$ex_ec_axes.max = $ex_ec_axis_max;
	});

  //voltage calc fixed axes
  var voltageAxisCheckbox = $('#checkbox-voltage-axis').prop('checked', true);
  voltageAxes.min = $('#voltage-axis-min').val();
  voltageAxes.max = $('#voltage-axis-max').val();
  if (!voltageAxisCheckbox){
    $('#voltage-axis-min').attr('disabled', true);
    $('#voltage-axis-max').attr('disabled', true);
  }else{
    $('#voltage-axis-min').removeAttr('disabled');
    $('#voltage-axis-max').removeAttr('disabled');
    voltageAxes.min = $('#voltage-axis-min').val();
    voltageAxes.max = $('#voltage-axis-max').val();
  }
  $('checkbox-voltage-axis').on('change', function(e){
    if ($(this).prop('checked')){
      $('#voltage-axis-min').removeAttr('disabled');
      $('#voltage-axis-max').removeAttr('disabled');
      voltageAxes.min = $('#voltage-axis-min').val();
      voltageAxes.max = $('#voltage-axis-max').val();
    }else{
      $('#voltage-axis-min').attr('disabled', true);
      $('#voltage-axis-max').attr('disabled', true);
      voltageAxes = null;
    }
  });
  $('#voltage-axis-min').on('change', function(e){
    voltageAxes.min = $(this).val();
  });
  $('#voltage-axis-max').on('change', function(e){
    voltageAxes.max = $(this).val();
  });


	var moreSatExEC, satExECCount=0, dynamicExECSelects, dynamicExECTexts, voltageGraphCount=0;
  //sat ex ec dynamic form creation
	$('#btn-ex-ec').on('click', function (e) {
		if(satExECLst.length > 0){
			satExECCount = Math.max.apply(null, satExECLst) + 1;
		}else{
			satExECCount +=1;
		}
		var satExECLabel = '<div class="col-md-2 col-sm-2 col-lg-2 top-buffer"><label class="control-label"><input class="ex-ec" name="sample-checkbox-01" id="checkbox-ex-ec-'+satExECCount+'" value="1" type="checkbox" /> Sensor</label></div>'
		var satExECSelect = '<div class="col-md-10 col-sm-10 col-lg-10 top-buffer"><select class="form-control ex-ec input-sm m-bot5" id="ms-ex-ec-'+satExECCount+'"></select></div>';
		var satEXECText = '<div class="col-lg-2 col-md-2 col-sm-2"><label for="ex-ec-offset-'+satExECCount+'" class="control-label">Offset </label></div><div class="col-lg-4 col-md-4 col-sm-4"><input type="text" class="form-control input-sm ex-ec" id="ex-ec-offset-'+satExECCount+'" placeholder=""></div>';
		var satEXECSaturation = '<div class="col-lg-2 col-md-2 col-sm-2"><label for="ex-ec-saturation-'+satExECCount+'" class="control-label">Saturation </label></div><div class="col-lg-4 col-md-4 col-sm-4"><input type="text" class="form-control input-sm ex-ec" id="ex-ec-saturation-'+satExECCount+'" placeholder=""></div>';
		var satEXECAxis = '<div class="col-lg-2 col-md-2 col-sm-2 top-buffer-5"><label for="ex-ec-label-'+satExECCount+'" class="control-label">Label </label></div><div class="col-lg-10 col-md-10 col-sm-10"><input type="text" class="form-control input-sm ex-ec top-buffer-5" id="ex-ec-label-'+satExECCount+'" placeholder=""></div>';
		$('#ex-ec-ctn').append(satExECLabel);
		$('#ex-ec-ctn').append(satExECSelect);
		$('#ex-ec-ctn').append(satEXECText);
		$('#ex-ec-ctn').append(satEXECSaturation);
		$('#ex-ec-ctn').append(satEXECAxis);
		var elementID = '#ms-ex-ec-'+satExECCount;
		var dataSource = new kendo.data.DataSource({
			data: $options,
			group: {field: "station"}
		});
		$(elementID).kendoMultiSelect({
			filter: 'contains',
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
      },
			dataSource: dataSource, 
			dataValueField: 'value',
			dataTextField: 'text'
		});
		$('#checkbox-ex-ec-'+satExECCount).prop('checked', true);
		satExECLst.push(satExECCount);
		
	});

  //voltage calc dynamic form creation
  $('#btn-voltage').on('click', function(e) {
    if(voltageLst.length > 0){
      voltageGraphCount = Math.max.apply(null, voltageLst) + 1;
    }else{
      voltageGraphCount  += 1;
    }
    var voltageHTML = '\
      <div class="col-md-2 col-sm-2 col-lg-2 top-buffer">\
        <label class="control-label">\
          <input class="voltage" name="voltage-checkbox" id="voltage-checkbox-'+voltageGraphCount+'" value="1" type="checkbox"/>\
            Sensor\
        <label/>\
      </div>\
      <div class="col-md-10 col-sm-10 col-lg-10 top-buffer">\
        <select class="form-control voltage input-sm m-bot5" id="ms-voltage-'+voltageGraphCount+'">\
        </select>\
      </div>\
      <div class="col-lg-2 col-md-2 col-sm-2">\
        <label for="voltage-equation-'+voltageGraphCount+'" class="control-label">Equation</label>\
      </div>\
      <div class="col-lg-10 col-md-10 col-sm-10">\
        <input type="text" class="form-control input-sm voltage" id="voltage-equation-'+voltageGraphCount+'" placeholder="i.e. x^2+3*x+1">\
      </div>\
      <div class="col-lg-2 col-md-2 col-sm-2 top-buffer-5">\
        <label for="voltage-label-'+voltageGraphCount+'" class="control-label">Label </label>\
      </div>\
      <div class="col-lg-10 col-md-10 col-sm-10">\
        <input type="text" class="form-control input-sm voltage top-buffer-5" id="voltage-label-'+voltageGraphCount+'" placeholder="">\
      </div>\
    ';
    $('#voltage-ctn').append(voltageHTML);
    var voltageMultiSelectID = '#ms-voltage-'+voltageGraphCount;
    var voltageSelectDataSource = new kendo.data.DataSource({
      data: $options,
      group: {field: "station"}
    });
    $(voltageMultiSelectID).kendoMultiSelect({
      filter: 'contains',
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
      },
      dataSource: voltageSelectDataSource, 
      dataValueField: 'value',
      dataTextField: 'text'
    });
    $('#voltage-checkbox-'+voltageGraphCount).prop('checked', true);
    voltageLst.push(voltageGraphCount);
  });
	
  //sat ex ec calc form change event handler
	$('#ex-ec').on('change','input.ex-ec:checkbox', function (e){
		if (!$(this).prop('checked')) {
			var id = $(this).attr('id').split('-')[$(this).attr('id').split('-').length-1];
			for (var i = 0; i < $sat_ex_ec_sensors.length; i++){
				if ($sat_ex_ec_sensors[i].inputID == id) {
					$sat_ex_ec_sensors.splice(i,1);
				};
				if (satExECLst[i] == id) {
					satExECLst.splice(i, 1);
				};
			};
			populateExEC($sat_ex_ec_sensors);

			
		};
	});
  //voltage calc form change event handler
  $('#voltage').on('change', 'input.voltage:checkbox', function(e){
    if(!$(this).prop('checked')){
      var id = $(this).attr('id').split('-')[$(this).attr('id').split('-').length-1];
      for (var i = 0; i < voltageSensors.length; i++){
        if (voltageSensors[i].inputID == id){
          voltageSensors.splice(i, 1);
        }
        if (voltageLst[i] == id){
          voltageLst.splice(i, 1);
        }
      };
      populateVoltageForm(voltageSensors);
    }
  });

  //Sat ex ec calc enable/disable
	$('#checkbox-ex-ec').prop('checked', false);
	$ex_ec_checkbox = $('#checkbox-ex-ec').prop('checked');
	$('#checkbox-ex-ec').on('change', function (e) {
		$ex_ec_checkbox = $('#checkbox-ex-ec').prop('checked');
		if($ex_ec_checkbox){
			$('#checkbox-ex-ec-axis').removeAttr('disabled');
			$('#ex-ec-axis-min').removeAttr('disabled');
			$('#ex-ec-axis-max').removeAttr('disabled');
		}else{
			$('#checkbox-ex-ec-axis').attr('disabled', 'disabled');
			$('#ex-ec-axis-min').attr('disabled', 'disabled');
			$('#ex-ec-axis-max').attr('disabled', 'disabled');
		}
	});

  //Voltage calc enable/disable
  $('#checkbox-voltage').prop('checked', false);
  voltageCheckbox = $('#checkbox-voltage').prop('checked');
  $('#checkbox-voltage').on('change', function(e){
    voltageCheckbox = $('#checkbox-voltage').prop('checked');
    if(voltageCheckbox){
      $('#checkbox-voltage-axis').removeAttr('disabled');
      $('#voltage-axis-min').removeAttr('disabled');
      $('#voltage-axis-max').removeAttr('disabled');
    }else{
      $('#checkbox-voltage-axis').attr('disabled', 'disabled');
      $('#voltage-axis-min').attr('disabled', 'disabled');
      $('#voltage-axis-max').attr('disabled', 'disabled');
    }
  });
	//build Sat ex ec calc variables list
	for (var i = 0; i < satExECLst.length; i++){
		var ex_ec_obj = {'inputID':null,'sensors':[],'offset':null, 'label':null, 'saturation':null}
		ex_ec_obj.sensors = $.map($('#ms-ex-ec-'+satExECLst[i]), function (el, i) {
			return $(el).val();
		});
		ex_ec_obj.offset = $('#ex-ec-offset-'+satExECLst[i]).val();
		ex_ec_obj.inputID = satExECLst[i];
		ex_ec_obj.saturation = $('#ex-ec-saturation-'+satExECLst[i]).val();
		ex_ec_obj.label = $('#ex-ec-label-'+satExECLst[i]).val();
		$sat_ex_ec_sensors.push(ex_ec_obj);
	};
  //build voltage calc variables list
  for (var i = 0; i < voltageLst.length; i++){
    var voltageVarsObj = {
      inputID: null, 
      sensor: null,
      equation: null,
      label: null
    }
    voltageVarsObj.inputID = voltageLst[i];
    voltageVarsObj.sensor = $('#ms-voltage-'+voltageLst[i]).val();
    voltageVarsObj.equation = $('#voltage-equation-'+voltageLst[i]).val();
    voltageVarsObj.label = $('#voltage-label-'+voltageLst[i]).val();
    voltageSensors.push(voltageVarsObj);
  }
  //update Sat ex ec calc variables list on change
	$('#ex-ec').on('change', '.ex-ec', function (e){
		$sat_ex_ec_sensors = [];
		for (var i = 0; i < satExECLst.length; i++){
			var ex_ec_obj = {'inputID':null,'sensors':[],'offset':null, 'label':null, 'saturation':null}
			ex_ec_obj.sensors = $.map($('#ms-ex-ec-'+satExECLst[i]), function (el, i) {
				return $(el).val();
			});
			ex_ec_obj.offset = $('#ex-ec-offset-'+satExECLst[i]).val();
			ex_ec_obj.inputID = satExECLst[i];
			ex_ec_obj.saturation = $('#ex-ec-saturation-'+satExECLst[i]).val();
			ex_ec_obj.label = $('#ex-ec-label-'+satExECLst[i]).val();
			$sat_ex_ec_sensors.push(ex_ec_obj);
		};	
	});
  //update voltage calc variables list on change
  $('#voltage').on('change', '.voltage', function(e){
    voltageSensors = [];
    for (var i = 0; i < voltageLst.length; i++){
      var voltageVarsObj = {
        inputID: null, 
        sensor: null,
        equation: null,
        label: null
      }
      voltageVarsObj.inputID = voltageLst[i];
      voltageVarsObj.sensor = $('#ms-voltage-'+voltageLst[i]).val();
      voltageVarsObj.equation = $('#voltage-equation-'+voltageLst[i]).val();
      voltageVarsObj.label = $('#voltage-label-'+voltageLst[i]).val();
      voltageSensors.push(voltageVarsObj);
    }
  });
});

var $checkbox_ex_ec_avg = $('#checkbox-ex-ec-avg').prop('checked');
$('#checkbox-ex-ec-avg').on('change', function (e) {
	$checkbox_ex_ec_avg = $('#checkbox-ex-ec-avg').prop('checked');
});

$('#main-chart-modal').on('show.bs.modal', function (e){
	$invoker = $(e.relatedTarget);
	$id = $invoker.parent().parent().parent().children('div').children('div').attr('id');
	$widget_id = $id;
	$main_sensors = [];


	if ($id in all_widgets) {
		$('#inputTitle').val(all_widgets[$id].data.title);
		$('#inputIndex').val(all_widgets[$id].index);
		if (all_widgets[$id].data.raw_sensors != null) {
			$('#checkbox-main-sensors').prop('checked', true);
			$('#ms-main-sensors').removeAttr('disabled');
			sensors = all_widgets[$id].data.raw_sensors.params.sensors;
			main_sensors_labels = all_widgets[$id].data.raw_sensors.params.labels;
			populateRawSensors(main_sensors_labels);
			$main_sensors = sensors;
			ms_main_sensors.value(sensors);
			if (all_widgets[$id].data.raw_sensors.params.axes != null) {
				$('#checkbox-main-sensors-axis').prop('checked', true);
				$('#main-sensors-axis-min').removeAttr('disabled');
				$('#main-sensors-axis-max').removeAttr('disabled');
				$('#main-sensors-axis-min').val(all_widgets[$id].data.raw_sensors.params.axes.min);
				$('#main-sensors-axis-max').val(all_widgets[$id].data.raw_sensors.params.axes.max);
				$main_sensors_axes = all_widgets[$id].data.raw_sensors.params.axes;
			}else{
				$('#checkbox-main-sensors-axis').prop('checked', false);
				$('#main-sensors-axis-min').attr('disabled', 'disabled');
				$('#main-sensors-axis-max').attr('disabled', 'disabled');
				$main_sensors_axis_min = $('#main-sensors-axis-min').val();
				$main_sensors_axis_max = $('#main-sensors-axis-max').val();
				$main_sensors_axes = {'min': $main_sensors_axis_min, 'max':$main_sensors_axis_max};
			};

		}else{
			$('#checkbox-main-sensors').prop('checked', false);
			$('#ms-main-sensors').attr('disabled', 'disabled');
			$('#main-sensors-axis-min').attr('disabled', 'disabled');
			$('#main-sensors-axis-max').attr('disabled', 'disabled');
			$('#checkbox-main-sensors-axis').attr('disabled', 'disabled');
			$('#main-sensors-axis-min').attr('disabled', 'disabled');
			$('#main-sensors-axis-max').attr('disabled', 'disabled');
		}

		if (all_widgets[$id].data.paw != null) {
			$('#checkbox-main-paw').prop('checked', true);
			$('#ms-main-paw').removeAttr('disabled');
			$('#main-paw-fc').removeAttr('disabled');
			$('#main-paw-wp').removeAttr('disabled');
			$('#checkbox-main-paw-avg').prop('checked', all_widgets[$id].data.paw.params.avg);
			paw_sensors = all_widgets[$id].data.paw.params.sensors;
			$main_paw_sensors = paw_sensors;
			ms_main_paw.value(paw_sensors);
			updatePAWFields();
			$main_paw_fc = all_widgets[$id].data.paw.params.fc;
			$main_paw_wp = all_widgets[$id].data.paw.params.wp;
			$('#main-paw-fc').val(all_widgets[$id].data.paw.params.fc);
			$('#main-paw-wp').val(all_widgets[$id].data.paw.params.wp);
			if(!all_widgets[$id].data.paw.params.avg){
				restorePAWFieldsValues(all_widgets[$id].data.paw.params.pawFields);	
			};
			

			
			for (var i in paw_sensors){
				$('#ms-main-paw option[value="'+paw_sensors[i]+'"]').attr('selected', 'selected');

			};
			if (all_widgets[$id].data.paw.params.axes != null) {
				$('#checkbox-paw-axis').prop('checked', true);
				$('#paw-axis-min').removeAttr('disabled');
				$('#paw-axis-max').removeAttr('disabled');
				$('#paw-axis-min').val(all_widgets[$id].data.paw.params.axes.min);
				$('#paw-axis-max').val(all_widgets[$id].data.paw.params.axes.max);
				$paw_axes = all_widgets[$id].data.paw.params.axes;
			}else{
				$('#checkbox-paw-axis').prop('checked', false);
				$('#paw-axis-min').attr('disabled', 'disabled');
				$('#paw-axis-max').attr('disabled', 'disabled');
				$main_paw_axis_min = $('#paw-axis-min').val();
				$main_paw_axis_max = $('#paw-axis-max').val();
				$paw_axes = {'min': $main_paw_axis_min, 'max':$main_paw_axis_max};
			};
			
		}else{
			$('#checkbox-main-paw').prop('checked', false);
			$('#ms-main-paw').attr('disabled', 'disabled');
			//$('#ms-main-paw').multiSelect('refresh');
			$('#main-paw-fc').attr('disabled', 'disabled');
			$('#main-paw-wp').attr('disabled', 'disabled');
			$('#checkbox-paw-axis').attr('disabled', 'disabled');
			$('#paw-axis-min').attr('disabled', 'disabled');
			$('#paw-axis-max').attr('disabled', 'disabled');
		};

		if (all_widgets[$id].data.chilling_portions != null) {
			$('#checkbox-main-cp').prop('checked', true);
			$('#s-main-cp').removeAttr('disabled');
			s_main_cp.value(all_widgets[$id].data.chilling_portions.params.sensors);
			// $('#s-main-cp option[value="'+all_widgets[$id].data.chilling_portions.params.sensors+'"]').attr('selected','');
			if (all_widgets[$id].data.chilling_portions.params.axes != null) {
				$('#checkbox-cp-axis').prop('checked', true);
				$('#cp-axis-min').removeAttr('disabled');
				$('#cp-axis-max').removeAttr('disabled');
				$('#cp-axis-min').val(all_widgets[$id].data.chilling_portions.params.axes.min);
				$('#cp-axis-max').val(all_widgets[$id].data.chilling_portions.params.axes.max);
				$cp_axes = all_widgets[$id].data.chilling_portions.params.axes;
			}else{
				$('#checkbox-cp-axis').prop('checked', false);
				$('#cp-axis-min').attr('disabled', 'disabled');
				$('#cp-axis-max').attr('disabled', 'disabled');
				$main_cp_axis_min = $('#cp-axis-min').val();
				$main_cp_axis_max = $('#cp-axis-max').val();
				$cp_axes = {'min': $main_cp_axis_min, 'max':$main_cp_axis_max};
				
			};
		}else{
			$('#checkbox-main-cp').prop('checked', false);
			$('#s-main-cp').attr('disabled', 'disabled');
			$('#checkbox-cp-axis').attr('disabled', 'disabled');
			$('#cp-axis-min').attr('disabled', 'disabled');
			$('#cp-axis-max').attr('disabled', 'disabled');
		};

		if (all_widgets[$id].data.degree_days != null) {
			$('#checkbox-main-dd').prop('checked', true);
			$('#s-main-dd').removeAttr('disabled');
			// $('#s-main-dd option[value="'+all_widgets[$id].data.degree_days.params.sensors+'"').attr('selected', '');
			s_main_dd.value(all_widgets[$id].data.degree_days.params.sensors);
			$('#main-dd-th').removeAttr('disabled');
			$('#main-dd-th').val(all_widgets[$id].data.degree_days.params.th);
			if (all_widgets[$id].data.degree_days.params.axes != null) {
				$('#checkbox-dd-axis').prop('checked', true);
				$('#dd-axis-min').removeAttr('disabled');
				$('#dd-axis-max').removeAttr('disabled');
				$('#dd-axis-min').val(all_widgets[$id].data.degree_days.params.axes.min);
				$('#dd-axis-max').val(all_widgets[$id].data.degree_days.params.axes.max);
				$dd_axes = all_widgets[$id].data.degree_days.params.axes;
			}else{
				$('#checkbox-dd-axis').prop('checked', false);
				$('#dd-axis-min').attr('disabled', 'disabled');
				$('#dd-axis-max').attr('disabled', 'disabled');
				$main_dd_axis_min = $('#dd-axis-min').val();
				$main_dd_axis_max = $('#dd-axis-max').val();
				$dd_axes = {'min': $main_dd_axis_min, 'max':$main_dd_axis_max};
				
			};
		}else{
			$('#checkbox-main-dd').prop('checked', false);
			$('#s-main-dd').attr('disabled', 'disabled');
			$('#main-dd-th').attr('disabled', 'disabled');
			$('#checkbox-dd-axis').attr('disabled', 'disabled');
			$('#dd-axis-min').attr('disabled', 'disabled');
			$('#dd-axis-max').attr('disabled', 'disabled');
		};

		if (all_widgets[$id].data.chilling_hours != null) {
			$('#checkbox-main-ch').prop('checked', true);
			$('#s-main-ch').removeAttr('disabled');
			// $('#s-main-ch option[value="'+all_widgets[$id].data.chilling_hours.params.sensors+'"]').attr('selected', '');
			s_main_ch.value(all_widgets[$id].data.chilling_hours.params.sensors)
			$('#main-ch-th').removeAttr('disabled');
			$('#main-ch-th').val(all_widgets[$id].data.chilling_hours.params.th);
			if (all_widgets[$id].data.chilling_hours.params.axes != null) {
				$('#checkbox-ch-axis').prop('checked', true);
				$('#ch-axis-min').removeAttr('disabled');
				$('#ch-axis-max').removeAttr('disabled');
				$('#ch-axis-min').val(all_widgets[$id].data.chilling_hours.params.axes.min);
				$('#ch-axis-max').val(all_widgets[$id].data.chilling_hours.params.axes.max);
				$ch_axes = all_widgets[$id].data.chilling_hours.params.axes;
			}else{
				$('#checkbox-ch-axis').prop('checked', false);
				$('#ch-axis-min').attr('disabled', 'disabled');
				$('#ch-axis-max').attr('disabled', 'disabled');
				$main_ch_axis_min = $('#ch-axis-min').val();
				$main_ch_axis_max = $('#ch-axis-max').val();
				$ch_axes = {'min': $main_ch_axis_min, 'max':$main_ch_axis_max};
				
			};

		}else{
			$('#checkbox-main-ch').prop('checked', false);
			$('#s-main-ch').attr('disabled', 'disabled');
			$('#main-ch-th').attr('disabled', 'disabled');
			$('#checkbox-ch-axis').attr('disabled', 'disabled');
			$('#ch-axis-min').attr('disabled', 'disabled');
			$('#ch-axis-max').attr('disabled', 'disabled');
		};

		if (all_widgets[$id].data.evapo != null) {
			$('#checkbox-main-eto').prop('checked', true);
			$('#s-main-eto-t').removeAttr('disabled');
			$('#s-main-eto-rh').removeAttr('disabled');
			$('#s-main-eto-sr').removeAttr('disabled');
			$('#s-main-eto-ws').removeAttr('disabled');
			$('#main-eto-lat').removeAttr('disabled');
			$('#main-eto-alt').removeAttr('disabled');

			// $('#s-main-eto-t option[value="'+all_widgets[$id].data.evapo.params.temp+'"]').attr('selected', '');
			// $('#s-main-eto-rh option[value="'+all_widgets[$id].data.evapo.params.rh+'"]').attr('selected', '');
			// $('#s-main-eto-sr option[value="'+all_widgets[$id].data.evapo.params.sr+'"]').attr('selected', '');
			// $('#s-main-eto-ws option[value="'+all_widgets[$id].data.evapo.params.ws+'"]').attr('selected', '');
			s_main_eto_t.value(all_widgets[$id].data.evapo.params.temp);
			s_main_eto_rh.value(all_widgets[$id].data.evapo.params.rh);
			s_main_eto_sr.value(all_widgets[$id].data.evapo.params.sr);
			s_main_eto_ws.value(all_widgets[$id].data.evapo.params.ws);
			$('#main-eto-lat').val(all_widgets[$id].data.evapo.params.lat);
			$('#main-eto-alt').val(all_widgets[$id].data.evapo.params.alt);
			if (all_widgets[$id].data.evapo.params.axes != null) {
				$('#checkbox-eto-axis').prop('checked', true);
				$('#eto-axis-min').removeAttr('disabled');
				$('#eto-axis-max').removeAttr('disabled');
				$('#eto-axis-min').val(all_widgets[$id].data.evapo.params.axes.min);
				$('#eto-axis-max').val(all_widgets[$id].data.evapo.params.axes.max);
				$eto_axes = all_widgets[$id].data.evapo.params.axes;
			}else{
				$('#checkbox-eto-axis').prop('checked', false);
				$('#eto-axis-min').attr('disabled', 'disabled');
				$('#eto-axis-max').attr('disabled', 'disabled');
				$main_eto_axis_min = $('#eto-axis-min').val();
				$main_eto_axis_max = $('#eto-axis-max').val();
				$eto_axes = {'min': $main_eto_axis_min, 'max':$main_eto_axis_max};
				
			};
		}else{
			$('#checkbox-main-eto').prop('checked', false);
			$('#s-main-eto-t').attr('disabled', 'disabled');
			$('#s-main-eto-rh').attr('disabled', 'disabled');
			$('#s-main-eto-sr').attr('disabled', 'disabled');
			$('#s-main-eto-ws').attr('disabled', 'disabled');
			$('#main-eto-lat').attr('disabled', 'disabled');
			$('#main-eto-alt').attr('disabled', 'disabled');
			$('#checkbox-eto-axis').attr('disabled', 'disabled');
			$('#eto-axis-min').attr('disabled', 'disabled');
			$('#eto-axis-max').attr('disabled', 'disabled');
		};

		if (all_widgets[$id].data.dew_point != null) {
			$('#checkbox-main-dp').prop('checked', true);
			$('#s-main-dp-t').removeAttr('disabled');
			$('#s-main-dp-rh').removeAttr('disabled');
			// $('#s-main-dp-t option[value="'+all_widgets[$id].data.dew_point.params.temp+'"]').attr('selected', '');
			// $('#s-main-dp-rh option[value="'+all_widgets[$id].data.dew_point.params.rh+'"]').attr('selected', '');
			s_main_dp_t.value(all_widgets[$id].data.dew_point.params.temp);
			s_main_dp_rh.value(all_widgets[$id].data.dew_point.params.rh);
			if (all_widgets[$id].data.dew_point.params.axes != null) {
				$('#checkbox-dp-axis').prop('checked', true);
				$('#dp-axis-min').removeAttr('disabled');
				$('#dp-axis-max').removeAttr('disabled');
				$('#dp-axis-min').val(all_widgets[$id].data.dew_point.params.axes.min);
				$('#dp-axis-max').val(all_widgets[$id].data.dew_point.params.axes.max);
				$dp_axes = all_widgets[$id].data.dew_point.params.axes;
			}else{
				$('#checkbox-dp-axis').prop('checked', false);
				$('#dp-axis-min').attr('disabled', 'disabled');
				$('#dp-axis-max').attr('disabled', 'disabled');
				$main_dp_axis_min = $('#dp-axis-min').val();
				$main_dp_axis_max = $('#dp-axis-max').val();
				$dp_axes = {'min': $main_dp_axis_min, 'max':$main_dp_axis_max};
				
			};
		}else{
			$('#checkbox-main-dp').prop('checked', false);
			$('#s-main-dp-t').attr('disabled', 'disabled');
			$('#s-main-dp-rh').attr('disabled', 'disabled');
		};
    //populate form for ex ec calc
		if (all_widgets[$id].data.ex_ec != null){
			$('#checkbox-ex-ec').prop('checked', true);
			$ex_ec_checkbox = $('#checkbox-ex-ec').prop('checked');
			$('#checkbox-ex-ec-avg').removeAttr('disabled');
			$('#ex-ec-axis-min').removeAttr('disabled');
			$('#ex-ec-axis-max').removeAttr('disabled');
			if (all_widgets[$id].data.ex_ec.params.avg) {
				$('#checkbox-ex-ec-avg').prop('checked', true);
			}else{
				$('#checkbox-ex-ec-avg').prop('checked', false);
			};
			populateExEC(all_widgets[$id].data.ex_ec.params.sensors);
			if (all_widgets[$id].data.ex_ec.params.axes != null) {
				$('#checkbox-ex-ec-axis').prop('checked', true);
				$('#ex-ec-axis-min').removeAttr('disabled');
				$('#ex-ec-axis-max').removeAttr('disabled');
				$('#ex-ec-axis-min').val(all_widgets[$id].data.ex_ec.params.axes.min);
				$('#ex-ec-axis-max').val(all_widgets[$id].data.ex_ec.params.axes.max);
				$ex_ec_axes = all_widgets[$id].data.ex_ec.params.axes;
			}else{
				$('#checkbox-ex-ec-axis').prop('checked', false);
				$('#ex-ec-axis-min').attr('disabled', 'disabled');
				$('#ex-ec-axis-max').attr('disabled', 'disabled');
				$main_ex_ec_axis_min = $('#ex-ec-axis-min').val();
				$main_ex_ec_axis_max = $('#ex-ec-axis-max').val();
				$ex_ec_axes = {'min': $main_ex_ec_axis_min, 'max':$main_ex_ec_axis_max};
				
			};
		}else{
			$('#checkbox-ex-ec').prop('checked', false);
			$('#checkbox-ex-ec-avg').attr('disabled', 'disabled');
			$('#ex-ec-axis-max').attr('disabled', 'disabled');
			$('#ex-ec-axis-max').attr('disabled', 'disabled');
		}
    //populate form for voltage calc
    if (all_widgets[$id].data.voltage != null){
      $('#checkbox-voltage').prop('checked', true);
      voltageCheckbox = $('#checkbox-voltage').prop('checked');
      $('voltage-axis-min').removeAttr('disabled');
      $('voltage-axis-max').removeAttr('disabled');
      voltageSensors = all_widgets[$id].data.voltage.params.sensors;
      populateVoltageForm(voltageSensors);
      if (all_widgets[$id].data.voltage.params.axes != null){
        $('#checkbox-voltage-axis').prop('checked', true);
        $('#voltage-axis-min').removeAttr('disabled');
        $('#voltage-axis-max').removeAttr('disabled');
        $('#voltage-axis-min').val(all_widgets[$id].data.voltage.params.axes.min);
        $('#voltage-axis-max').val(all_widgets[$id].data.voltage.params.axes.max);
        voltageAxes = all_widgets[$id].data.voltage.params.axes;
      }
    }else{

    }

		$('#reportrange span').html(all_widgets[$id].data.range.from + ' - ' + all_widgets[$id].data.range.to);
		$date_from = all_widgets[$id].data.range.from
		$date_to = all_widgets[$id].data.range.to

	};

	if(!($id in all_widgets)){ // if new widget set default index to 99
		$('#inputIndex').val('99');
		$('#inputTitle').val('New chart');
	} 
		

	$main_sensors_check_sensors = $('#checkbox-main-sensors').prop('checked');
	$main_sensors_check_paw = $('#checkbox-main-paw').prop('checked');
	$main_sensors_check_cp = $('#checkbox-main-cp').prop('checked'); 
	$main_sensors_check_dd = $('#checkbox-main-dd').prop('checked');
	$main_sensors_check_ch = $('#checkbox-main-ch').prop('checked');
	$main_sensors_check_eto = $('#checkbox-main-eto').prop('checked'); 
	$main_sensors_check_dp = $('#checkbox-main-dp').prop('checked');

	
	$title = $('#inputTitle').val();
	$('#main-general').find('#inputTitle').on('change', function (e){
		$title = $(this).val();
	});

	$index = $('#inputIndex').val();
	$('#main-general').find('#inputIndex').on('change', function (e){
		$index = $(this).val();
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
		$('#ms-main-ex-ec-t').removeAttr('disabled');
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
			$('#main-sensors-axis-min').removeAttr('disabled');
			$('#checkbox-main-sensors-axis').removeAttr('disabled');
			$('#main-sensors-axis-min').removeAttr('disabled');
			$('#main-sensors-axis-max').removeAttr('disabled');
		}else{
			$main_sensors_check_sensors = false; 
			$('#ms-main-sensors').attr('disabled', 'disabled');
			$('#main-sensors-axis-min').removeAttr('disabled');
			$('#checkbox-main-sensors-axis').attr('disabled', 'disabled');
			$('#main-sensors-axis-min').attr('disabled', 'disabled');
			$('#main-sensors-axis-max').attr('disabled', 'disabled');
		}
	});

	$('#checkbox-main-paw').on('change', function(e){
		e.stopImmediatePropagation();
		if($(this).prop('checked')){
			$main_sensors_check_paw = true;
			$('#ms-main-paw').removeAttr('disabled');
			$('#main-paw-fc').removeAttr('disabled');
			$('#main-paw-wp').removeAttr('disabled');
			// $('#ms-main-paw').multiSelect('refresh');
			$('#checkbox-paw-axis').removeAttr('disabled');
			$('#paw-axis-min').removeAttr('disabled');
			$('#paw-axis-max').removeAttr('disabled');
		}else{
			$main_sensors_check_paw = false; 
			$('#ms-main-paw').attr('disabled', 'disabled');
			$('#main-paw-fc').attr('disabled', 'disabled');
			$('#main-paw-wp').attr('disabled', 'disabled');
			// $('#ms-main-paw').multiSelect('refresh');
			$('#checkbox-paw-axis').attr('disabled', 'disabled');
			$('#paw-axis-min').attr('disabled', 'disabled');
			$('#paw-axis-max').attr('disabled', 'disabled');
		}
	});

	$('#checkbox-main-cp').on('change', function(e){
		e.stopImmediatePropagation();
		if($(this).prop('checked')){
			$main_sensors_check_cp = true;
			$('#s-main-cp').removeAttr('disabled');
			$('#checkbox-cp-axis').removeAttr('disabled');
			$('#cp-axis-min').removeAttr('disabled');
			$('#cp-axis-max').removeAttr('disabled');
		}else{
			$main_sensors_check_cp = false; 
			$('#s-main-cp').attr('disabled', 'disabled');
			$('#checkbox-cp-axis').attr('disabled');
			$('#cp-axis-min').attr('disabled', 'disabled');
			$('#cp-axis-max').attr('disabled', 'disabled');

		}
	});

	$('#checkbox-main-dd').on('change', function(e){
		e.stopImmediatePropagation();
		if($(this).prop('checked')){
			$main_sensors_check_dd = true;
			$('#s-main-dd').removeAttr('disabled');
			$('#main-dd-th').removeAttr('disabled');
			$('#checkbox-dd-axis').removeAttr('disabled');
			$('#dd-axis-min').removeAttr('disabled');
			$('#dd-axis-max').removeAttr('disabled');
		}else{
			$main_sensors_check_dd = false; 
			$('#s-main-dd').attr('disabled', 'disabled');
			$('#main-dd-th').attr('disabled', 'disabled');
			$('#checkbox-dd-axis').attr('disabled', 'disabled');
			$('#dd-axis-min').attr('disabled', 'disabled');
			$('#dd-axis-max').attr('disabled', 'disabled');
		}
	});
	$('#checkbox-main-ch').on('change', function(e){
		e.stopImmediatePropagation();
		if($(this).prop('checked')){
			$main_sensors_check_ch = true;
			$('#s-main-ch').removeAttr('disabled');
			$('#main-ch-th').removeAttr('disabled');
			$('#checkbox-ch-axis').removeAttr('disabled');
			$('#ch-axis-min').removeAttr('disabled');
			$('#ch-axis-max').removeAttr('disabled');
		}else{
			$main_sensors_check_ch = false; 
			$('#s-main-ch').attr('disabled', 'disabled');
			$('#main-ch-th').attr('disabled', 'disabled');
			$('#checkbox-ch-axis').attr('disabled', 'disabled');
			$('#ch-axis-min').attr('disabled', 'disabled');
			$('#ch-axis-max').attr('disabled', 'disabled');
		}
	});

	$('#checkbox-main-eto').on('change', function(e){
		e.stopImmediatePropagation();
		if($(this).prop('checked')){
			$main_sensors_check_eto = true;
			$('#s-main-eto-t').removeAttr('disabled');
			$('#s-main-eto-rh').removeAttr('disabled');
			$('#s-main-eto-sr').removeAttr('disabled');
			$('#s-main-eto-ws').removeAttr('disabled');
			$('#main-eto-lat').removeAttr('disabled');
			$('#main-eto-alt').removeAttr('disabled');
			$('#checkbox-eto-axis').removeAttr('disabled');
			$('#eto-axis-min').removeAttr('disabled');
			$('#eto-axis-max').removeAttr('disabled');
		}else{
			$main_sensors_check_eto = false; 
			$('#s-main-eto-t').attr('disabled', 'disabled');
			$('#s-main-eto-rh').attr('disabled', 'disabled');
			$('#s-main-eto-sr').attr('disabled', 'disabled');
			$('#s-main-eto-ws').attr('disabled', 'disabled');
			$('#main-eto-lat').attr('disabled', 'disabled');
			$('#main-eto-alt').attr('disabled', 'disabled');
			$('#checkbox-eto-axis').attr('disabled', 'disabled');
			$('#eto-axis-min').attr('disabled', 'disabled');
			$('#eto-axis-max').attr('disabled', 'disabled');
		}
	});
	$('#checkbox-main-dp').on('change', function(e){
		e.stopImmediatePropagation();
		if($(this).prop('checked')){
			$main_sensors_check_dp = true;
			$('#s-main-dp-t').removeAttr('disabled');
			$('#s-main-dp-rh').removeAttr('disabled');
			$('#checkbox-dp-axis').removeAttr('disabled');
			$('#dp-axis-min').removeAttr('disabled');
			$('#dp-axis-max').removeAttr('disabled');
		}else{
			$main_sensors_check_dp = false; 
			$('#s-main-dp-t').attr('disabled', 'disabled');
			$('#s-main-dp-rh').attr('disabled', 'disabled');
			$('#checkbox-dp-axis').attr('disabled', 'disabled');
			$('#dp-axis-min').attr('disabled', 'disabled');
			$('#dp-axis-max').attr('disabled', 'disabled');
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

	$paw_avg = $('#checkbox-main-paw-avg').prop('checked');
	$('#checkbox-main-paw-avg').on('change', function(e){
		$paw_avg = $('#checkbox-main-paw-avg').prop('checked');
	});
	if (!$paw_avg) {
		updatePAWFieldsValues();
	};

	

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
		$main_eto_rh = $("#s-main-eto-rh option:selected").val();		
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
	$main_dp_rh = $("#s-main-dp-rh option:selected").val();
	$('#s-main-dp-t').on('change', function(e){
		e.stopImmediatePropagation();
		$main_dp_t = $("#s-main-dp-t option:selected").val();
	});
	$('#s-main-dp-rh').on('change', function(e){
		e.stopImmediatePropagation();
		$main_dp_rh = $("#s-main-dp-rh option:selected").val();
	});
	//$('#ms-main-sensors').multiSelect('refresh');
	

	$('#main-chart-modal button.submit').on('click', function  (e) {
		// body...
		e.stopImmediatePropagation();


		main_sensors = [];
		raw_sensors = null;
		if ($main_sensors_check_sensors){
			main_sensors = $main_sensors;
			raw_sensors = {
				'params':{
					'sensors':main_sensors,
					'axes': $main_sensors_axes,
					'labels': main_sensors_labels
					}, 
				'value':'',
				'name':'raw_sensors',
				'title':'Raw Sensor',
				'lineColor':'#33ff00',
				'unit':'C'
			};

		}else{
			raw_sensors = null;
		};
		main_paw_sensors = [];
		main_paw_fc = '';
		main_paw_wp = '';
		paw_avg = '';
		paw = null;
		if ($main_sensors_check_paw) {
			main_paw_sensors = $main_paw_sensors
			main_paw_fc = $main_paw_fc;
			main_paw_wp = $main_paw_wp;
			paw_avg = $paw_avg;
			paw = {
				'params':{
					'fc':main_paw_fc, 
					'wp':main_paw_wp,
					'sensors':main_paw_sensors, 
					'avg':paw_avg,
					'pawFields': $pawFields,
					'axes': $paw_axes
					},
				'value':'',
				'name':'paw',
				'title':'PAW',
				'lineColor':'#00fff7',
				'unit':''
			};
		}else{
			paw = null;
		};
		main_cp = '';
		chilling_portions = null;
		if ($main_sensors_check_cp) {
			main_cp = $main_cp;
			chilling_portions = {
				'params':{
					'sensors':main_cp,
					'axes': $cp_axes
					}, 
				'value':'',
				'name':'chilling_portions',
				'title':'Chilling Portions',
				'lineColor':'#33ff00'
			};
		};

		main_dd = '';
		main_dd_th = '';
		degree_days = null; 
		if ($main_sensors_check_dd) {
			main_dd = $main_dd;
			main_dd_th = $main_dd_th;
			degree_days = {
				'params': {
					'sensors':main_dd,
					'th':main_dd_th, 
					'axes': $dd_axes
					},
				'value':'',
				'name':'degree_days',
				'title':'Degree Days',
				'lineColor':'#33ff00'
			};
		};
		main_ch = '';
		main_ch_th = '';
		chilling_hours = null;
		if ($main_sensors_check_ch) {
			main_ch = $main_ch;
			main_ch_th = $main_ch_th;
			chilling_hours = {
				'params': {
					'sensors':main_ch,
					'th':main_ch_th, 
					'axes':$ch_axes
					},
				'value':'',
				'name':'chilling_hours',
				'title':'Chilling Hrs.',
				'lineColor':'#33ff00'
			};
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
				'alt':main_eto_alt,
				'axes': $eto_axes
			},
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
			dew_point = {
				'params':{
					'sensors':'',
					'rh':main_dp_rh,
					'temp': main_dp_t, 
					'axes': $dp_axes
					},
				'value':'',
				'name':'dew_point',
				'title':'Dew Point',
				'lineColor': '#0077ff'
			};
		};

		//saturation ex ec
		var ex_ec = null;
		if($ex_ec_checkbox){
			ex_ec = {
				'params':{
					'sensors': $sat_ex_ec_sensors,
					'avg': $checkbox_ex_ec_avg, 
					'axes': $ex_ec_axes
				},
				'value':'',
				'name': 'ex_ec',
				'title': 'Saturation Ex EC'
			}
		}
    //voltage
    var voltage = null;
    if(voltageCheckbox){
      voltage = {
        'params':{
          'sensors': voltageSensors,
          'axes': voltageAxes
        },
        'value':'',
        'name': 'voltage',
        'title': 'Voltage'
      }
    }

		$id = $invoker.parent().parent().parent().children('div').children('div').attr('id');
		$type = 'main-chart';
		$data = {
			'raw_sensors':raw_sensors,
			'paw':paw,
			'chilling_portions':chilling_portions,
			'degree_days':degree_days,
			'chilling_hours':chilling_hours,
			'evapo':evapo,
			'dew_point':dew_point,
			'ex_ec': ex_ec,
      'voltage': voltage,
			'calc': {'params':{'sensor':'temp_min'}},
			'range': {'from':$date_from, 'to':$date_to},
			'title': $title
		}

		widget = new Widget($id, $index, $title, $type, '', $data);
		$invoker.parent().parent().parent().children('div').append('<div class="nosupport curtain"><i class="fa fa-spin fa-spinner"></i> Loading... </div>');
		notify_elem = notify_man('info', 'Loading chart... please wait.');
		ajax_request(render_chart, widget, notify_elem);

		$invoker.parent().parent().children('span.title').text($title);
		console.log(widget);

		$('#main-chart-modal').modal('hide');

	});
});

function getID() {
	id = getRandomColor();
	widget_lst = Object.keys(all_widgets);
	if (id.split('#')[1] in widget_lst) {
		return getID();
	}else{
		return id.split('#')[1];
	};
}
function addChartWidget() {
	widget_id = getID();	
	large_html = '<div class="col-lg-6">\
                <section id="main-panel-" class="panel main-panel">\
                  <header class="panel-heading">\
                    <span class="title">New chart panel &nbsp;<i id="main-panel-{{forloop.counter}}-i" class=""></i></span>\
                    <span class="tools pull-right">\
                      <a href="javascript:;" class="fa fa-expand expandable"></a>\
                      <a href="javascript:;" class="fa fa-chevron-down"></a>\
                      <a href="#main-chart-modal" data-toggle="modal" class="fa fa-wrench"></a>\
                      <a href="javascript:;" class="fa fa-times"></a>\
                    </span>\
                  </header>\
                  <div class="panel-body">\
                  <div id="'+widget_id+'" class="chart-container"></div>\
                  </div>\
                </section>\
              </div>'
	$('.chart-row').append(large_html);
}

function addStatWidget() {
	widget_id = getID();
	large_html = '<div class="col-lg-3 col-sm-6"><section id="'+widget_id+'" class="panel"><div class="symbol terques"><a data-toggle="modal" class="btn" data-target="#statmodal"><i> Station name</i></a></div><div class="value"><h1 class="count">222</h1><p>Sensor name</p></div></section></div>';
	$('.stat-row').append(large_html);
}
