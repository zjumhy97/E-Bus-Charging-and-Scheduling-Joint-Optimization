import pickle
import os
import gurobipy as gp
from gurobipy import GRB
import numpy as np
import copy
import sys
import time
import network_haoyu.EVSPExtentedGraph as EGraph

vehicle_num = 100

if os.path.exists('line_4_time_5_soc_30_trip_579.pickle'):
    with open('line_4_time_5_soc_30_trip_579.pickle', 'rb') as f:
        graph = pickle.load(f)
        graph = graph[0]

# line_3_time_5_soc_30_trip_193.pickle
# line_2_time_15_soc_10_trip_65_charger_5.pickle


vertex_size, edge_size = graph.graphSize()

model = gp.Model()
x = model.addVars(edge_size, vtype=GRB.BINARY, name="x")
model.update()
model.setParam('Method', 2)
model.setParam('DegenMoves', 0)
# model.setParam('NodeMethod', 2)

b = np.array([vehicle_num])
b = np.append(b, np.zeros(vertex_size-2))
b = np.append(b, [-vehicle_num])
# b = np.array([1] + [0 for i in range(len(vertex_info)-1)] + [-1])

# flow constraints
for j in range(vertex_size):
    # print('out edge', graph.vertex_set[j].edge_id_out)
    # print('in edge', graph.vertex_set[j].edge_id_in)
    model.addConstr(gp.quicksum(x[i] for i in graph.vertex_set[j].edge_id_out) -
                    gp.quicksum(x[i] for i in graph.vertex_set[j].edge_id_in) == b[j])


# exactly once constraints
for k in range(1, graph.plane_number - 1):
    trip_in_edge = []
    for vertex in graph.trip_in_vertex_list[k]:
        trip_in_edge.extend(vertex.edge_id_in)
    model.addConstr(gp.quicksum(x[i] for i in trip_in_edge) == 1)

# charger constraints

for i in range(int((graph.end_time - graph.start_time)/graph.time_granularity/60)):
    model.addConstr(gp.quicksum(x[j] for j in graph.charging_edge_set[i]) <= graph.charger_number)


# model.setObjective(gp.quicksum(x[i, k] for i in range(len(graph.edge_set)) for k in range(vehicle_num)), GRB.MINIMIZE)
# model.setObjective(gp.quicksum(x[i, k] for i in range(len(graph.edge_set)) for k in range(vehicle_num)), GRB.MAXIMIZE)
model.setObjective(gp.quicksum(x[i] * graph.edge_set[i].weight for i in range(edge_size)), GRB.MINIMIZE)
# model.setObjective(gp.quicksum(x[i, k] for i in range(2, len(graph.edge_set)) for k in range(2, vehicle_num)), GRB.MINIMIZE)

timer_optimize_start = time.time()
model.optimize()
timer_optimize_end = time.time()

model.write("line_4_time_5_soc_30_trip_579_out.sol")

result_not_int = False
for i in range(edge_size):
    if x[i].x != 1 and x[i].x != 0:
        result_not_int = True

if result_not_int:
    print('*******************  Result not integer!  *******************')


###
#
# 打印结果
# print('Edge number:', edge_size)
# for k in range(1, graph.plane_number - 1):
#     print('> trip', k)
#     trip_in_edge = []
#     edge_value_list = []
#     for vertex in graph.trip_in_vertex_list[k]:
#         trip_in_edge.extend(vertex.edge_id_in)
#     for i in trip_in_edge:
#         # edge_value_list.append([graph.edge_set[i].vertex_id_pair, x[i].x])
#         edge_value_list.append([graph.edge_set[i].start.coordinate_str,graph.edge_set[i].end.coordinate_str, x[i].x])
#         # edge_value_list.append(x[i].x)
#     print(edge_value_list)

# k=5
# print('> trip', k)
# trip_in_edge = []
# edge_value_list = []
# for vertex in graph.trip_in_vertex_list[k]:
#     trip_in_edge.extend(vertex.edge_id_in)
# for i in trip_in_edge:
#     # edge_value_list.append([graph.edge_set[i].vertex_id_pair, x[i].x])
#     edge_value_list.append([i, graph.edge_set[i].start.coordinate_str, graph.edge_set[i].end.coordinate_str, x[i].x])
#     # edge_value_list.append(x[i].x)
# print(edge_value_list)


# 打印 path
path_edge_list = []
for i in range(edge_size):
    if x[i].x != 0:
        path_edge_list.append(graph.edge_set[i].vertex_id_pair)

path_edge_list_col0 = list(np.array(path_edge_list)[:, 0])
path_edge_list_col0_copy = copy.deepcopy(path_edge_list_col0)
path_edge_list_copy = copy.deepcopy(path_edge_list)
path_all = []
path_with_trip_id_all = []
while len(path_edge_list_col0_copy) > 0:
    path = []
    path_with_trip_id = []
    element = path_edge_list_copy[0]
    path.extend(element)
    while element[1] in path_edge_list_col0:
        # 循环条件：存在下一个 element
        row_index = path_edge_list_col0.index(element[1])
        # 确认新的 element
        element_new = path_edge_list[row_index]
        path.extend([element_new[1]])
        path_with_trip_id.extend([graph.vertex_set[element_new[1]].coordinate[0]])
        # 删除旧的 element
        path_edge_list_col0_copy.remove(element[0])
        path_edge_list_copy.remove(element)
        # 更新 element
        element = element_new
    path_edge_list_col0_copy.remove(element[0])
    path_edge_list_copy.remove(element)
    path_all.append(path)
    path_with_trip_id_all.append(list(np.unique(path_with_trip_id)))

for k in range(len(path_all)):
    print('vehicle', k, ':', path_with_trip_id_all[k])

# 看一下第一条路径
# path_0 = []
# for vertex_id in path_all[0]:
#     path_0.append([vertex_id, graph.vertex_set[vertex_id].coordinate_str])
# path_1 = []
# for vertex_id in path_all[1]:
#     path_1.append([vertex_id, graph.vertex_set[vertex_id].coordinate_str])
# path_2 = []
# for vertex_id in path_all[2]:
#     path_2.append([vertex_id, graph.vertex_set[vertex_id].coordinate_str])
# path_3 = []
# for vertex_id in path_all[3]:
#     path_3.append([vertex_id, graph.vertex_set[vertex_id].coordinate_str])


print('time (optimization) = ', timer_optimize_end - timer_optimize_start)



print(1)
#
# for k in range(vehicle_num):
#     print('> vehicle', k)
#     list = []
#     for i in range(edge_size):
#         list.append(x[i, k].x)
#     print(list)
#
