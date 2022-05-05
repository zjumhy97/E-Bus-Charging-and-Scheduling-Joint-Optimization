import time
import json
import pickle
import collections

import network_haoyu.EVSPGraphVehicleNode as EGraph
import evsp_virtual_vehicle_nodes.utils_evsp.generate_trip_data as TripData

time_start = time.time()
# Parameters
data_file_path = '../trip_data/'
graph_file_path = '../graph_generated/'
trip_num = 20 # 193
gap = 5
duration = 45
# soc_ev = {'粤B12345':100, '粤B23456':90, '粤B34567':80, '粤B45678':70}
soc_ev = {'粤B12345': 100,
          '粤B13456': 90,
          '粤B14567': 80,
          '粤B15678': 70,
          '粤B16789': 80,
          '粤B17890': 70,
          '粤B18901': 70,
          '粤B19012': 80,
          '粤B10123': 70,
          # '粤B11234': 70,
          # '粤B22345': 100,
          # '粤B23456': 90,
          # '粤B24567': 80,
          # '粤B25678': 70,
          # '粤B26789': 80,
          # '粤B27890': 70,
          # '粤B28901': 70,
          # '粤B29012': 80,
          # '粤B20123': 70,
          # '粤B21234': 70,
          # '粤B32345': 100,
          # '粤B33456': 90,
          # '粤B34567': 80,
          # '粤B35678': 70,
          # '粤B36789': 80,
          # '粤B37890': 70,
          # '粤B38901': 70,
          # '粤B39012': 80,
          # '粤B30123': 70,
          # '粤B31234': 70,
          # '粤B42345': 100,
          # '粤B43456': 90,
          # '粤B44567': 80,
          # '粤B45678': 70,
          # '粤B46789': 80,
          # '粤B47890': 70,
          # '粤B48901': 70,
          # '粤B49012': 80,
          # '粤B40123': 70,
          # '粤B51234': 70,
          }
soc_ev = collections.OrderedDict(soc_ev)
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

time_end = time.time()
time_construct_graph = time_end - time_start
print('time construct graph = ', time_construct_graph)


