import json
import time

def generate_trip_data(start_time_str, gap, duration, trip_number):
    trip = {}
    # trip1 = {"trip_id": 1,
    #          "attribute": "task",
    #          "start_time_str": start_time_str,
    #          "duration": duration}
    trip_list = locals()
    for i in range(1, trip_number+1):
        # trip_list['trip' + str(i)] = {"trip_id": i,
        #                               "attribute": "task",
        #                               "start_time_str": start_time_str,
        #                               "duration": duration}
        trip['trip' + str(i)] = {"trip_id": i,
                                 "attribute": "task",
                                 "start_time_str": start_time_str,
                                 "duration": duration}
        # (trip_list['trip' + str(i)])
        start_time = int(time.mktime(time.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")))
        start_time += gap * 60
        start_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time))
    jsondata = json.dumps(trip, indent=4, separators=(',', ':'))

    file = open('../trip_data/trip_' + str(trip_number) + '_gap_'+ str(gap) +'_dura_'
                + str(duration)+'.json', 'w')
    file.write(jsondata)
    file.close()


if __name__ == '__main__':
    generate_trip_data(start_time_str='2022-03-24 07:00:00', gap=15, duration=45, trip_number=6)
































