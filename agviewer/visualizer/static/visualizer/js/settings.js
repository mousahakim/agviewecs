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


//glabals



//ajax
function ajax_request(data, url, notify_el){
	var request = $.ajax({
		  method: "POST",
		  url: url,
		  data: JSON.stringify(data), 
		  dataType: 'json'
		}).done(function(data) {
            console.log(data);
            notify_remove(notify_el);
            if (data.success){
              notify_auto('success', 5, data.message);  
            }else{
              notify_auto('danger', 5, data.message);
            };
  		}).fail(function(msg){
            notify_remove(notify_el);
            notify_auto('danger', 5, 'Operation failed. Please try again.');
  		});
};


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

function populate_alert_modal(params){
  console.log(params);
  $('#add-alert-modal .alert-name').val(params['name']);
  $('#add-alert-modal .alert-desc').val(params['description']); 
  $('#add-alert-modal select.alert-type option[value="'+params['type']+'"]').prop('selected', true);
  alert_sensors.value(params.sensors);
  $('#add-alert-modal select.alert-calc option[value="'+params['calc']+'"').prop('selected', true);
  $('#add-alert-modal select.alert-logic option[value="'+params['logic']+'"').prop('selected', true);
  $('#add-alert-modal .alert-extract').val(params['extract']);
  $('#add-alert-modal .alert-threshold').val(params['threshold']);
  $('#add-alert-modal .alert-message').val(params['message']);
  $('#add-alert-modal .alert-t-beyond').val(params['t_beyond']);
  $('#add-alert-modal .alert-via-sms').prop('checked', params['sms_alert']);
  $('#add-alert-modal .alert-via-email').prop('checked', params['email_alert']);
  $('.snooze-checkbox').bootstrapSwitch('state', params['snooze'], params['snooze']);
  $('.snooze-time').val(params['snooze_time']);
}

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
          $('#'+invoker_id+'.delete-alert').parent().parent().remove();
      }
      if (action == 'ADD_NEW'){
        if(data.success){
          params = $.parseJSON(params);
          var uid = data.uid;
          var type_label = 'label-info fa fa-info-circle';
          var snooze_input_element = '<input \
            type="checkbox"\
            id="'+uid+'"\
            name="snooze-inline-checkbox" \
            class="snooze-inline-checkbox form-control">';
          if (params.type == 'warning')
            type_label = 'label-warning fa fa-exclamation-circle';
          if (params.type == 'critical')
            type_label = 'label-danger fa fa-warning';
          if (params.snooze)
            var snooze_input_element = '<input \
            type="checkbox"\
            id="'+uid+'"\
            name="snooze-inline-checkbox" \
            class="snooze-inline-checkbox form-control"\
            checked>';


          $('.alerts-table table tbody').prepend('<tr>\
            <td>'+params.name+'</td>\
            <td class="hidden-xs">'+snooze_input_element+'</td>\
            <td><span class="label '+type_label+' label-mini"> </span></td>\
            <td>\
              <button class="btn btn-primary btn-xs" data-toggle="modal" data-target="#add-alert-modal" id="'+uid+'">\
              <i class="fa fa-pencil"></i></button>\
              <button class="btn btn-danger btn-xs delete-alert" id="'+uid+'"><i class="fa fa-trash-o "></i></button>\
            </td>\
          </tr>');

          $('#'+data.uid+'.snooze-inline-checkbox').bootstrapSwitch({
            'state': params.snooze,
            'size':'mini', 
            'labelWidth': 10,
            'handleWidth': 10,
            'onSwitchChange': function(event, state) {
              // body...
              // var snoozeTime = $('.snooze-time').val();
              var params = {
                'alert_id': $(this).attr('id'),
                'state': state, 
                // 'time': snoozeTime
              }
              console.log(params);

              $.ajax({
                method: 'POST',
                url: '/snooze_state_change',
                data: JSON.stringify(params),
                dataType: 'json'
              }).done(function(data){
                if (data.success){
                  return true
                }else{
                  return false
                }
              }).fail(function(data) {
                console.log(data.message);
                return false  
              });
            },
          });
        }else{
          notify_auto('danger', 5, data.message);
        }

      }
      if (action == 'MODIFY'){
        params = $.parseJSON(params);
        console.log($('#'+params.uid+'.snooze-inline-checkbox').prop('checked'));
        $('#'+params.uid+'.snooze-inline-checkbox').bootstrapSwitch('state', params.snooze, params.snooze);
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
  // if (alert.length == 0) {
  //   $('#alert-list').prepend('\
  //     <li>\
  //       <a href="#">See all notifications</a>\
  //     </li>\
  //   ');
  //   $('#alert-list').prepend('\
  //     <div class="notify-arrow notify-arrow-grey"></div>\
  //       <li>\
  //         <p class="grey">You have '+unread+' unread notifications</p>\ 
  //       </li>\
  //   ');
  // }
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

function removeDashboard(uid){
  var params = {
    'uid': uid
  }

  $.ajax({
    method: 'POST',
    url: '/removedashboard',
    data: JSON.stringify(params),
    dataType: 'json'
  }).done(function(data){
    if (data.success){
      $('select#dashboards option[value="'+uid+'"]').remove();
      $('#'+uid).parent().remove();
    }
  }).fail(function(data){
    notify_auto('danger', 5, 'Operation failed. '+data.status);
  });
}

function editDashboard(uid, name){
  var params = {
    'uid': uid, 
    'name': name
  }

  $.ajax({
    method: 'POST',
    url: '/editdashboard',
    data: JSON.stringify(params),
    dataType: 'json'
  }).done(function(data){
    if (data.success){
      $('select#dashboards option[value="'+uid+'"]').html(name);
      $('#'+uid).html(name)
    }
  }).fail(function(data){
    notify_auto('danger', 5, 'Operation failed. '+data.status);
  });
}


$(function () {

  $('.picker-default').colorpicker({
    format: 'hex'
  });
  $('.picker-default2').colorpicker({
    format: 'hex'
  });

  $s_station = $('select.station').kendoMultiSelect({
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
    },
    value: []
  }).data('kendoMultiSelect');

  $station = $('select.station option:selected').val();
  // $station = $s_station.value()[0];
  $('select.station').on('change', function (e){
      $station = $('select.station option:selected').val();
  })
  $station_alias = $('input.station-alias').val();
  $('input.station-alias').on('change', function (e){
      $station_alias = $('input.station-alias').val();
  });
  $('button.station').on('click', function (e){
      e.stopImmediatePropagation();
      e.preventDefault();
      data = {
        'station_id': $station,
        'alias': $station_alias,
        'success': '',
        'message': ''
      }
      notify_el = notify_man('info', 'Saving new alias...');
      ajax_request(data, URLChangeAlias, notify_el);
  });
  $s_sensor = $('select.sensor').kendoMultiSelect({
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
    },
    value: []
  }).data('kendoMultiSelect');

  $sensor = $('select.sensor option:selected').val();
  $('select.sensor').on('change', function (e){
      $sensor = $('select.sensor option:selected').val();
  });
  $sensor_alias = $('input.sensor-alias').val();
  $('input.sensor-alias').on('change', function (e){
      $sensor_alias = $('input.sensor-alias').val();
  });
  $('button.sensor').on('click', function (e){
      e.stopImmediatePropagation();
      e.preventDefault();
      data = {
        'sensor_id': $sensor,
        'alias': $sensor_alias,
        'success': '',
        'message': ''
      }
      notify_el = notify_man('info', 'Saving new alias...');
      ajax_request(data, URLChangeAlias, notify_el);
  });

  $calc_color_type = $('select.graph-calc-color option:selected').val();
  $('select.graph-calc-color').on('change', function (e) {
    $calc_color_type = $('select.graph-calc-color option:selected').val();
    console.log($calc_color_type);
  });
  $calc_color_color = $('.picker-default').data('colorpicker').color.toHex();
  $('button.graph-calc-color').on('click', function (e) {
    e.stopImmediatePropagation();
    e.preventDefault();
    data = {'opt':'graph_color', 'type':'calc', 'attr':$calc_color_type, 'value':$('.picker-default').data('colorpicker').color.toHex()}
    notify_el = notify_man('info', 'Saving changes...');
    ajax_request(data, URLChangeSetting, notify_el);
    console.log(data);
  });
  $s_color_sense = $('select.graph-sensor-color').kendoMultiSelect({
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
    },
    value: []
  }).data('kendoMultiSelect');

  $sens_color_sense = $('select.graph-sensor-color option:selected').val();
  $('select.graph-sensor-color').on('change', function (e) {
    $sens_color_sense = $('select.graph-sensor-color option:selected').val();
    console.log($sens_color_sense);
  });
  $('button.graph-sensor-color').on('click', function (e) {
    e.stopImmediatePropagation();
    e.preventDefault();
    data = {'opt':'graph_color', 'type':'sensor', 'attr':$sens_color_sense, 'value':$('.picker-default2').data('colorpicker').color.toHex()}
    notify_el = notify_man('info', 'Saving changes...');
    ajax_request(data, URLChangeSetting, notify_el);
    console.log(data);
  });
  $graph_calc = $('select.graph-calc-type option:selected').val();
  $('select.graph-calc-type').on('change', function (e) {
    $graph_calc = $('select.graph-calc-type option:selected').val();
    console.log($graph_calc);
  });

  $graph_type = $('select.graph-graph-type option:selected').val();
  $('select.graph-graph-type').on('change', function (e) {
    $graph_type = $('select.graph-graph-type option:selected').val();
    console.log($graph_type);
  });
  $('button.graph-calc-type').on('click', function (e) {
    e.stopImmediatePropagation();
    e.preventDefault();
    data = {'opt':'graph_type', 'type':'calc', 'attr':$graph_calc, 'value':$graph_type}
    notify_el = notify_man('info', 'Saving changes...');
    ajax_request(data, URLChangeSetting, notify_el)
    console.log($graph_type, $graph_calc); 
  });

  $s_graph_sense = $('select.graph-sensor-type').kendoMultiSelect({
    maxSelectedItems: 3,
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
    value: []
  }).data('kendoMultiSelect');

  $graph_sensor = $('select.graph-sensor-type option:selected').val();
  $('select.graph-sensor-type').on('change', function (e) {
    $graph_sensor = $('select.graph-sensor-type option:selected').val();
    console.log($graph_sensor);
  });
  $graph_sensor_type = $('select.sensor-graph-type option:selected').val();
  $('select.sensor-graph-type').on('change', function (e) {
    $graph_sensor_type = $('select.sensor-graph-type option:selected').val();
    console.log($graph_sensor_type);
  });
  $('button.sensor-graph-type').on('click', function (e) {
    e.stopImmediatePropagation();
    e.preventDefault();
    data = {'opt':'graph_type', 'type':'sensor', 'attr':$graph_sensor, 'value':$graph_sensor_type}
    notify_el = notify_man('info', 'Saving changes...');
    ajax_request(data, URLChangeSetting, notify_el)
    console.log($graph_sensor_type, $graph_sensor);
  });
  $cp_reset_dt = $('select.cp-reset-dt option:selected').val();
  $('select.cp-reset-dt').on('change', function (e) {
    $cp_reset_dt = $('select.cp-reset-dt option:selected').val();
    console.log($cp_reset_dt);
  });
  $('button.cp-reset-dt').on('click', function (e) {
    e.stopImmediatePropagation();
    e.preventDefault();
    data = {'opt':'cp_reset_dt', 'type':'calc', 'attr':'cp_reset_dt', 'value':$cp_reset_dt};
    notify_el = notify_man('info', 'Saving changes...');
    ajax_request(data, URLChangeSetting, notify_el);
    console.log(data);
  });

  $ch_reset_dt = $('select.ch-reset-dt option:selected').val();
  $('select.ch-reset-dt').on('change', function (e) {
    $ch_reset_dt = $('select.ch-reset-dt option:selected').val();
    console.log($ch_reset_dt);
  });
  $('button.ch-reset-dt').on('click', function (e) {
    e.stopImmediatePropagation();
    e.preventDefault();
    data = {'opt':'ch_reset_dt', 'type':'ch_reset_dt', 'attr':'ch_reset_dt', 'value':$ch_reset_dt};
    notify_el = notify_man('info', 'Saving changes...');
    ajax_request(data, URLChangeSetting, notify_el);
    console.log(data);
  });

  $ch_threshold = $('input.ch-threshold').val();
  $('input.ch-threshold').on('change', function (e) {
    $ch_threshold = $('input.ch-threshold').val();
    console.log($ch_threshold);
  });
  $('button.ch-threshold').on('click', function (e) {
    e.stopImmediatePropagation();
    e.preventDefault();
    data = {'opt':'ch_threshold', 'type':'ch_threshold', 'attr':'ch_threshold', 'value':$ch_threshold};
    notify_el = notify_man('info', 'Saving changes...');
    ajax_request(data, URLChangeSetting, notify_el);
    console.log(data);
  });

  $dd_reset_dt = $('select.dd-reset-dt option:selected').val();
  $('select.dd-reset-dt').on('change', function (e) {
    $dd_reset_dt = $('select.dd-reset-dt option:selected').val();
    console.log($dd_reset_dt);
  });
  $('button.dd-reset-dt').on('click', function (e) {
    e.stopImmediatePropagation();
    e.preventDefault();
    data = {'opt':'dd_reset_dt', 'type':'dd_reset_dt', 'attr':'dd_reset_dt', 'value':$dd_reset_dt};
    notify_el = notify_man('info', 'Saving changes...');
    ajax_request(data, URLChangeSetting, notify_el);
    console.log(data);
  });

  $dd_threshold = $('input.dd-threshold').val();
  $('input.dd-threshold').on('change', function (e) {
    $dd_threshold = $('input.dd-threshold').val();
    console.log($dd_threshold);
  });
  $('button.dd-threshold').on('click', function (e) {
    e.stopImmediatePropagation();
    e.preventDefault();
    data = {'opt':'dd_threshold', 'type':'dd_threshold', 'attr':'dd_threshold', 'value':$dd_threshold};
    notify_el = notify_man('info', 'Saving changes...');
    ajax_request(data, URLChangeSetting, notify_el);
    console.log(data);
  });

  $ar_reset_dt = $('select.ar-reset-dt option:selected').val();
  $('select.ar-reset-dt').on('change', function (e) {
    $ar_reset_dt = $('select.ar-reset-dt option:selected').val();
    console.log($ar_reset_dt);
  });
  $('button.ar-reset-dt').on('click', function (e) {
    e.stopImmediatePropagation();
    e.preventDefault();
    data = {'opt':'ar_reset_dt', 'type':'ar_reset_dt', 'attr':'ar_reset_dt', 'value':$ar_reset_dt};
    notify_el = notify_man('info', 'Saving changes...');
    ajax_request(data, URLChangeSetting, notify_el);
    console.log(data);
  });

   alert_sensors = $('select.alert-sensors').kendoMultiSelect({
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
    value: [],
  }).data('kendoMultiSelect'); 

  // $('#add-alert-modal select.alert-calc').on('change', function(e){
  //   e.stopImmediatePropagation();
  //   e.preventDefault();
  //   if($(this).val() != 'none'){
  //     $("#add-alert-modal select.alert-sensors").attr('disabled', 'disabled');
  //   };
  // });

  $('#add-alert-modal button.submit').on('click', function(e){
    e.stopImmediatePropagation();
    e.preventDefault();
    var action = 'ADD_NEW';
    var uid;
    if(alert_modal_invoker.attr('id') != undefined){
      action = 'MODIFY';
      uid = $(alert_modal_invoker).attr('id');
    }
    var name = $('#add-alert-modal .alert-name').val();
    var description = $('#add-alert-modal .alert-desc').val();
    var type = $('#add-alert-modal select.alert-type option:selected').val();
    var calc = $('#add-alert-modal select.alert-calc option:selected').val();
    var sensors = $.map($("#add-alert-modal select.alert-sensors option:selected"), function (el, i) {
          return $(el).val();
      });
    var extract = $('#add-alert-modal .alert-extract').val(); 
    var logic = $('#add-alert-modal select.alert-logic option:selected').val();
    var threshold = $('#add-alert-modal .alert-threshold').val();
    var message = $('#add-alert-modal .alert-message').val();
    var tBeyond = $('#add-alert-modal .alert-t-beyond').val();
    var snooze = $('.snooze-checkbox').prop('checked');
    var snoozeTime = $('.snooze-time').val();
    var via_sms = $('#add-alert-modal .alert-via-sms').prop('checked');
    var via_email = $('#add-alert-modal .alert-via-email').prop('checked');
    console.log(uid);
    var params = {
      'uid': uid,
      'action': action,
      'name' : name, 
      'description': description,
      'type': type, 
      'calc': calc, 
      'sensors': sensors,
      'extract': extract,
      'logic': logic,
      'threshold': threshold,
      'message': message,
      't_beyond': tBeyond,
      'snooze': snooze,
      'snooze_time': snoozeTime, 
      'sms_alert': via_sms,
      'email_alert': via_email
    };

    alert_action(params);
    $('#add-alert-modal').modal('hide');

  });

  $('#add-alert-modal').on('show.bs.modal', function(e){
    alert_modal_invoker = $(e.relatedTarget);
    if(alert_modal_invoker.attr('id') != undefined){
      alert_action({'uid': $(e.relatedTarget).attr('id'), 'action': 'GET'});
    }

  });

  // snooze model switch
  $("[name='snooze-checkbox'").bootstrapSwitch({
    'size':'small', 
    'labelWidth': 20,

  });

  //inline snooze swith
  $("[name='snooze-inline-checkbox'").bootstrapSwitch({
      'size':'mini', 
      'labelWidth': 10,
      'handleWidth': 10,
      'onSwitchChange': function(event, state) {
        // body...
        // var snoozeTime = $('.snooze-time').val();
        var params = {
          'alert_id': $(this).attr('id'),
          'state': state, 
          // 'time': snoozeTime
        }
        console.log(params);

        $.ajax({
          method: 'POST',
          url: '/snooze_state_change',
          data: JSON.stringify(params),
          dataType: 'json'
        }).done(function(data){
          if (data.success){
            return true
          }else{
            return false
          }
        }).fail(function(data) {
          console.log(data.message);
          return false  
        });
      },

    });

  $('.alerts-table').on('click', '.delete-alert', function(e){
    if(!confirm('Are you sure you want to delete alert permenantly ?')){
      return
    };
    var params = {
      'uid': $(this).attr('id'),
      'action': 'DELETE'
    }
    console.log(params); 
    alert_action(params);

  });

  $('.notification-dropdown').on('click', function(e){
    markoff_new_alert();
  })

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

  $('a.remove-dashboard').on('click', function(e){
    var uid = $('select#dashboards option:selected').val();
    console.log(uid);
    removeDashboard(uid);
  });

  $('#edit-dashboard-modal').on('show.bs.modal', function(e){
    // var uid = $('select#dashboards option:selected').val();
    var name = $('select#dashboards option:selected').text();
    $('#edit-dashboard-modal input.dashboard-name').val(name);
    // console.log(uid, name);
    // editDashboard(uid);
  });

  $('#edit-dashboard-modal button.submit').on('click', function(e){
    var uid = $('select#dashboards option:selected').val();
    var name = $('#edit-dashboard-modal input.dashboard-name').val();
    console.log(uid, name);
    editDashboard(uid, name);
    $('#edit-dashboard-modal').modal('hide');
  });

  // $('#sidebar .sidebar-menu').on('click', '.dashboard-item', function(e){
  //   var dashboardUID = $(this).attr('id');
  //   window.location.href = '/?dashboard='+dashboardUID;
  // });



});


//station modal
$('#add-station-modal').on('show.bs.modal', function (e) {
	$invoker = $(e.relatedTarget);
	$db = $('#add-station-modal input.radio:checked').val();
	$station_id = $('#add-station-modal input.id').val();
	$password = $('#add-station-modal input.pass').val();
    $download_data = $('#add-station-modal checkbox.download_data').val();
	
	$('#add-station-modal input.radio').on('change', function (e) {
		e.stopImmediatePropagation();
		$db = $(this).val();
		$station_id = $('#add-station-modal input.id').val();
		$password = $('#add-station-modal input.pass').val();
	});
	$('#add-station-modal input.id').on('change', function (e) {
		e.stopImmediatePropagation();
		$station_id = $('#add-station-modal input.id').val();
		$password = $('#add-station-modal input.pass').val();
	});
	$('#add-station-modal input.pass').on('change', function (e) {
		e.stopImmediatePropagation();
		$station_id = $('#add-station-modal input.id').val();
		$password = $('#add-station-modal input.pass').val();
	});
  $station_alias = $('#add-station-modal input.alias').val();
  $('#add-station-modal input.alias').on('change', function (e) {
    e.stopImmediatePropagation();
    $station_alias = $('#add-station-modal input.alias').val();
  });

	$('#add-station-modal button.submit').on('click', function  (e) {
		e.stopImmediatePropagation();
		data = {
            'db':$db,
            'station_id':$station_id,
            'password':$password,
            'alias':$station_alias,
            'success':'',
            'message':''}

		console.log(data);
        notify_el = notify_man('info', 'Adding station and downloading station data... Please wait.');
		ajax_request(data, URLAddStation, notify_el);
		$('#add-station-modal').modal('hide');
	});

	return;
});

$('#rmv-stn-modal').on('show.bs.modal', function (e) {
  $invoker = $(e.relatedTarget);
  $station_id = $('#rmv-stn-modal select.station option:selected').val();
  $('#rmv-stn-modal select.station').on('change', function (e) {
    e.stopImmediatePropagation();
    $station_id = $('#rmv-stn-modal select.station option:selected').val();
    console.log($station_id);
  });

  $('#rmv-stn-modal button.submit').on('click', function  (e) {
    e.stopImmediatePropagation();
    data = {
            'station_id':$station_id,
            'success':'',
            'message':''}

    console.log(data);
        notify_el = notify_man('info', 'Removing station... Please wait.');
    ajax_request(data, URLRemoveStation, notify_el);
    $('#rmv-stn-modal').modal('hide');
  });

  return;
});



