import json
import time

class TripDataSameGap():
    def __init__(self, start_time_str, gap, duration, trip_number):
        self.start_time_str = start_time_str
        self.gap = gap
        self.duration = duration
        self.trip_number = trip_number

    def generate(self, data_file_path):
        trip = {}
        # trip1 = {"trip_id": 1,
        #          "attribute": "task",
        #          "start_time_str": start_time_str,
        #          "duration": duration}
        trip_list = locals()
        start_time_str = self.start_time_str
        for i in range(1, self.trip_number+1):
            # trip_list['trip' + str(i)] = {"trip_id": i,
            #                               "attribute": "task",
            #                               "start_time_str": start_time_str,
            #                               "duration": duration}
            trip['trip' + str(i)] = {"trip_id": i,
                                     "attribute": "task",
                                     "start_time_str": start_time_str,
                                     "duration": self.duration,
                                     "energy_consumption": 30}
            # (trip_list['trip' + str(i)])
            start_time = int(time.mktime(time.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")))
            start_time += self.gap * 60
            start_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time))
        jsondata = json.dumps(trip, indent=4, separators=(',', ':'))

        file = open(data_file_path + 'trip_' + str(self.trip_number) + '_gap_' + str(self.gap) + '_dura_'
                    + str(self.duration)+'.json', 'w')
        file.write(jsondata)
        file.close()


































