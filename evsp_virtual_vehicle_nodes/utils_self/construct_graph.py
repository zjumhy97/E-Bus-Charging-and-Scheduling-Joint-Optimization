import time
import json
import pickle

import network_haoyu.EVSPGraphVehicleNode as EGraph
import evsp_virtual_vehicle_nodes.utils_self.generate_trip_data as TripData

# Parameters
data_file_path = '../trip_data/'
graph_file_path = '../graph_generated/'
trip_num = 6
gap = 15
duration = 45
soc_ev = {'粤B12345':100, '粤B23456':100, '粤B34567':100, '粤B45678':100}
start_time_str_trip = '2022-04-21 07:00:00'
start_time_str_graph = '2022-04-21 06:50:00'
end_time_str = '2022-04-22 06:50:00'


start_time_trip = int(time.mktime(time.strptime(start_time_str_trip, "%Y-%m-%d %H:%M:%S")))
start_time_graph = int(time.mktime(time.strptime(start_time_str_graph, "%Y-%m-%d %H:%M:%S")))
end_time = int(time.mktime(time.strptime(end_time_str, "%Y-%m-%d %H:%M:%S")))


trip_data = TripData.TripDataSameGap(start_time_str=start_time_str_trip, gap=gap,
                                     duration=duration, trip_number=trip_num)
trip_data.generate(data_file_path=data_file_path)
file = open(data_file_path + 'trip_' + str(trip_num) + '_gap_' + str(gap) + '_dura_'
                + str(duration)+'.json', 'r')

trip_info = json.load(file)

graph = EGraph.EVSPGraph(time_granularity=5, soc_ev=soc_ev, trip_info=trip_info,
                         start_time=start_time_graph, end_time=end_time)
graph.construct_graph()

with open(graph_file_path + 'vehicle_' + str(len(soc_ev)) + '_trip_' + str(trip_num) + '.pickle', 'wb') as f:
    pickle.dump([graph], f)




