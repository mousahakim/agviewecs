

def copy_data(src_station, des_station, src_sensor, des_sensor):

    from visualizer.models import StationData

    src_station_data = StationData.objects.filter(station_id=src_station)
    des_station_data = StationData.objects.filter(station_id=des_station)

    count = 0
    existing_count = 0
    new_count = 0
    for record in src_station_data:

        if record.data.has_key(src_sensor):
                
            record_to_change = des_station_data.filter(station_id=des_station, date=record.date)

            if record_to_change.exists():

                changed_record = record_to_change[0]
                record_data = changed_record.data
                record_data.update({des_sensor : record.data[src_sensor]})
                changed_record.data = record_data
                changed_record.save()
                existing_count+=1
            else:

                record.pk = None
                record.station_id = des_station
                record.save()
                new_count+=1

            count+=1

    print('records inserted: ', count)
