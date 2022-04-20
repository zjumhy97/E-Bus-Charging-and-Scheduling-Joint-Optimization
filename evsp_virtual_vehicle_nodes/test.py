import network_haoyu.EVSPGraphVehicleNode as EGraph

import time
import json

soc_ev = {'粤B12345':100, '粤B23456':90, '粤B34567':80, '粤B45678':70}
start_time_str = '2022-03-24 06:50:00'
start_time = int(time.mktime(time.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")))
end_time_str = '2022-03-25 06:30:00'
end_time = int(time.mktime(time.strptime(end_time_str, "%Y-%m-%d %H:%M:%S")))

trip_number = 6
gap = 15
duration = 45

file = open('./trip_data/trip_' + str(trip_number) + '_gap_'+ str(gap) +'_dura_'
                + str(duration)+'.json', 'r')
trip_data = json.load(file)



graph = EGraph.EVSPGraph(time_granularity=5, soc_ev=soc_ev, trip_info=trip_data)

graph.start_time = start_time
graph.start_time_str = start_time_str
graph.end_time = end_time
graph.end_time_str = end_time_str

# graph.addDepotVertex(attribute='origin')
# graph.addVirtualVehicleVertex(soc_ev=soc_ev)
graph.construct_graph(vertex_info=None)


print(1)