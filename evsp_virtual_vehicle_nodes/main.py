import pickle
import os
import gurobipy as gp
from gurobipy import GRB
import numpy as np
import copy
import sys
import time

vehicle_num = 4
trip_num = 6
soc_ev = {'粤B12345':100, '粤B23456':90, '粤B34567':80, '粤B45678':70}
graph_file_path = './graph_generated/'

if os.path.exists(graph_file_path + 'vehicle_4_trip_6.pickle'):
    with open(graph_file_path + 'vehicle_4_trip_6.pickle', 'rb') as f:
        graph = pickle.load(f)
        graph = graph[0]

vertex_size, edge_size = graph.graphSize()

model = gp.Model()
x = model.addVars(edge_size, vtype=GRB.BINARY, name="x")
s = model.addVars(vertex_size, vtype=GRB.CONTINUOUS, name="s")
w = model.addVars(edge_size, lb=0, vtype=GRB.CONTINUOUS, name="w")
m = model.addVars(edge_size, lb=0, vtype=GRB.CONTINUOUS, name="m")
c = model.addVars(edge_size, lb=0, vtype=GRB.CONTINUOUS, name="c")
q = model.addVars(edge_size, )
model.update()
# model.setParam('Method', 2)
# model.setParam('DegenMoves', 0)
# model.setParam('NodeMethod', 2)

b = np.array([vehicle_num])
b = np.append(b, np.zeros(vertex_size-2))
b = np.append(b, [-vehicle_num])
# b = np.array([1] + [0 for i in range(len(vertex_info)-1)] + [-1])

s_upper = 100
s_lower = 10
M = 1000000

# flow constraints
for j in range(vertex_size):
    model.addConstr(gp.quicksum(x[i] for i in graph.vertex_set[j].edge_id_out) -
                    gp.quicksum(x[i] for i in graph.vertex_set[j].edge_id_in) == b[j])

# exactly once constraints
for j in range(1, vertex_size-1):
    model.addConstr(gp.quicksum(x[i] for i in graph.vertex_set[j].edge_id_out) == 1)

# soc constraints
model.addConstr(s[0] == s_upper)
for k in range(vehicle_num):
    model.addConstr(s[k+1] == graph.vertex_set[k+1].soc)
for j_index in range(trip_num):
    j = vehicle_num + 1 + j_index
    model.addConstr(s[j] >= s_lower)
    model.addConstr(s[j] <= s_upper - graph.vertex_set[j].energy_consumption)
model.addConstr(s[vertex_size - 1] == s_upper * vehicle_num)

# soc evolution
for j in range(vehicle_num + 1, vertex_size):
    e_j = graph.vertex_set[j].energy_consumption
    model.addConstr(s[j] == gp.quicksum(w[i] + m[i] - x[i] * e_j for i in graph.vertex_set[j].edge_id_in))

# bilinear constraints
for i in range(edge_size):
    model.addConstr(w[i] <= M * x[i])
    model.addConstr(w[i] >= s[graph.edge_set[i].end1.vertex_id] - M * (1 - x[i]))
    model.addConstr(w[i] <= s[graph.edge_set[i].end1.vertex_id] + M * (1 - x[i]))

    model.addConstr(m[i] <= M * x[i])
    model.addConstr(m[i] >= c[i] - M * (1 - x[i]))
    model.addConstr(m[i] <= c[i] + M * (1 - x[i]))

    model.addConstr(w[i] + m[i] <= s_upper)


# charging constraints


model.setObjective(gp.quicksum(x[i] * graph.edge_set[i].weight for i in range(edge_size)), GRB.MINIMIZE)

timer_optimize_start = time.time()
model.optimize()
timer_optimize_end = time.time()

# model.write("line_4_time_5_soc_30_trip_579_out.sol")

result_not_int = False
for i in range(edge_size):
    if x[i].x != 1 and x[i].x != 0:
        result_not_int = True

if result_not_int:
    print('*******************  Result not integer!  *******************')

print(1)
list = []
for i in range(edge_size):
    list.append(x[i].x)
print(list)

s_list = []
for j in range(vertex_size):
    s_list.append(s[j].x)
print(s_list)

# 打印 path
for k in range(vehicle_num):
    print('EB_' + str(k) + ' ' + graph.vertex_set[k+1].vertex_attribute + ' soc =' + str(graph.vertex_set[k+1].soc) )
    path_k = []
    if x[k].x == 1:
        path_k.extend(graph.edge_set[k].vertex_id_pair)
        next_vertex_id = graph.edge_set[k].end2.vertex_id
        while len(graph.vertex_set[next_vertex_id].edge_id_out) != 0:
            for i in graph.vertex_set[next_vertex_id].edge_id_out:
                if x[i].x == 1:
                    # path_k.append(str(graph.edge_set[i].end2.vertex_id) + ':' + str(s[graph.edge_set[i].end2.vertex_id].x))
                    path_k.append(
                        str(graph.edge_set[i].end2.vertex_id) + ':' + str(c[i].x))
                    path_k.append(graph.edge_set[i].end2.vertex_id)
                    next_vertex_id = graph.edge_set[i].end2.vertex_id
                    break
    print(path_k)





print('time (optimization) = ', timer_optimize_end - timer_optimize_start)




