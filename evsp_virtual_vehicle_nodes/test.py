import network_haoyu.EVSPGraphVehicleNode as EGraph

import time

soc_ev = {'粤B12345':100, '粤B23456':90, '粤B34567':80, '粤B45678':70}
start_time_str = '2022-03-24 06:50:00'
start_time = int(time.mktime(time.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")))
end_time_str = '2022-03-25 06:30:00'
end_time = int(time.mktime(time.strptime(end_time_str, "%Y-%m-%d %H:%M:%S")))

graph = EGraph.EVSPGraph(time_granularity=5, soc_ev=soc_ev)

graph.start_time = start_time
graph.start_time_str = start_time_str
graph.end_time = end_time
graph.end_time_str = end_time_str

# graph.addDepotVertex(attribute='origin')
# graph.addVirtualVehicleVertex(soc_ev=soc_ev)
graph.constructGraph(vertex_info=None)


print(1)