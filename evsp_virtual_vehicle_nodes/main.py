import pickle
import os
import gurobipy as gp
from gurobipy import GRB
import numpy as np
import copy
import sys
import time

trip_num = 30 # 193 50
soc_ev = {'粤B12345': [0, 100],
          '粤B13456': [1, 90],
          '粤B14567': [2, 80],
          '粤B15678': [3, 70],
          '粤B16789': [4, 80],
          '粤B17890': [5, 70],
          '粤B18901': [6, 70],
          '粤B19012': [7, 80],
          '粤B10123': [8, 70],
          '粤B11234': [9, 70],
          '粤B22345': [10, 100],
          '粤B23456': [11, 90],
          # '粤B24567': [12, 80],
          # '粤B25678': [13, 70],
          # '粤B26789': [14, 80],
          # '粤B27890': [15, 70],
          # '粤B28901': [16, 70],
          # '粤B29012': [17, 80],
          # '粤B20123': [18, 70],
          # '粤B21234': [19, 70],
          # '粤B32345': [20, 100],
          # '粤B33456': [21, 90],
          # '粤B34567': [22, 80],
          # '粤B35678': [23, 70],
          # '粤B36789': [24, 80],
          # '粤B37890': [25, 70],
          # '粤B38901': [26, 70],
          # '粤B39012': [27, 80],
          # '粤B30123': [28, 70],
          # '粤B31234': [29, 70],
          # '粤B42345': [30, 100],
          # '粤B43456': [31, 90],
          # '粤B44567': [32, 80],
          # '粤B45678': [33, 70],
          # '粤B46789': [34, 80],
          # '粤B47890': [35, 70],
          # '粤B48901': [36, 70],
          # '粤B49012': [37, 80],
          # '粤B40123': [38, 70],
          # '粤B51234': [39, 70],
          }
vehicle_num = len(soc_ev)
graph_file_path = './graph_generated/'
pickle_file_name = 'vehicle_' + str(vehicle_num) +'_trip_' + str(trip_num) + '.pickle'

def load_graph(graph_file_path, pickle_file_name):
    if os.path.exists(graph_file_path + pickle_file_name):
        with open(graph_file_path + pickle_file_name, 'rb') as f:
            graph = pickle.load(f)
            graph = graph[0]
    return graph

def path_variable_binary_check():
    result_not_int = False
    for i in range(edge_size):
        if x[i].x != 1 and x[i].x != 0:
            result_not_int = True

    if result_not_int:
        print('*******************  Result not integer!  *******************')

def print_eb_path():
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
                        path_k.append(graph.edge_set[i].end2.vertex_id)
                        next_vertex_id = graph.edge_set[i].end2.vertex_id
                        break
        print("(", len(path_k) - 3, ")", path_k)

def print_eb_path_with_soc_charging():
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
                        # 现在的 [74, 10, 5] -> [83, -15, 25]
                        # 想要的 [45, '74', 15] -> [15+25, '83', 10]
                        path_k.append([s[graph.edge_set[i].end1.vertex_id].x + c[i].x,
                                       str(graph.edge_set[i].end2.vertex_id),
                                       s[graph.edge_set[i].end2.vertex_id].x,
                                       c[i].x])
                        next_vertex_id = graph.edge_set[i].end2.vertex_id
                        break
        print("(", len(path_k) - 3, ")", path_k)

graph = load_graph(graph_file_path=graph_file_path, pickle_file_name=pickle_file_name)

vertex_size, edge_size = graph.graphSize()
time_slot_num = int(24 * 60 / graph.time_granularity)
s_upper = 100
s_lower = 10
M = 1000000
q_upper = 5
q_total_upper = 5 * 10

model = gp.Model()
x = model.addVars(edge_size, vtype=GRB.BINARY, name="x")
s = model.addVars(vertex_size, vtype=GRB.CONTINUOUS, name="s")
w = model.addVars(edge_size, lb=0, vtype=GRB.CONTINUOUS, name="w")
m = model.addVars(edge_size, lb=0, vtype=GRB.CONTINUOUS, name="m")
c = model.addVars(edge_size, lb=0, vtype=GRB.CONTINUOUS, name="c")
q = model.addVars(edge_size, time_slot_num, lb=0, ub=q_upper, vtype=GRB.CONTINUOUS, name='q')
model.update()
# model.setParam('Method', 2)
# model.setParam('DegenMoves', 0)
# model.setParam('NodeMethod', 2)

b = np.array([vehicle_num])
b = np.append(b, np.zeros(vertex_size-2))
b = np.append(b, [-vehicle_num])
# b = np.array([1] + [0 for i in range(len(vertex_info)-1)] + [-1])

# x_reassignment = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, -0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.0, 1.0, -0.0, -0.0, -0.0, -0.0, -0.0, 0.0, 0.0, 0.0, -0.0, -0.0, -0.0, -0.0, -0.0, 1.0, -0.0, 0.0, 0.0, 0.0, 1.0, -0.0, -0.0, -0.0, -0.0, -0.0, -0.0, 0.0, 0.0, 0.0, -0.0, -0.0, -0.0, -0.0, 1.0, -0.0, -0.0, 0.0, 0.0, 0.0, -0.0, -0.0, 1.0, -0.0, -0.0, -0.0, -0.0, 0.0, 0.0, 0.0, -0.0, -0.0, -0.0, -0.0, -0.0, -0.0, 1.0, 0.0, 0.0, 0.0, -0.0, -0.0, -0.0, 1.0, -0.0, -0.0, -0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
# for i in range(edge_size):
#     model.addConstr(x[i] == x_reassignment[i])

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
for i in range(edge_size):
    initial_time = graph.start_time
    toi = graph.edge_set[i].end1.start_time
    doi = graph.edge_set[i].end1.duration
    tdi = graph.edge_set[i].end2.start_time
    start_index = int((toi + doi - initial_time) / graph.time_granularity / 60)
    end_index = int((tdi - initial_time) / graph.time_granularity / 60)
    # constraint (1h)
    # key constraint, whether the charging amount could be achieved physically
    model.addConstr(c[i] == gp.quicksum(q[i, t] for t in range(start_index, end_index)))


for t in range(time_slot_num):
    model.addConstr(gp.quicksum(q[i, t] for i in range(edge_size)) <= q_total_upper)

# electricity_price
p = []
for t in range(time_slot_num):
    time_temp = graph.start_time + t * graph.time_granularity * 60
    time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time_temp))
    p.append(graph.electricity_price(time_str, mode='TOU'))

# 假设 5% 对应的是 5度电
objective = gp.quicksum(p[t] * gp.quicksum(q[i, t] for i in range(edge_size)) for t in range(time_slot_num))
model.setObjective(objective, GRB.MINIMIZE)
# model.setObjective(gp.quicksum(x[i] * graph.edge_set[i].weight for i in range(edge_size)), GRB.MINIMIZE)

timer_optimize_start = time.time()
model.optimize()
timer_optimize_end = time.time()

# model.write(".sol")

print_eb_path_with_soc_charging()

print('time (optimization) = ', timer_optimize_end - timer_optimize_start)

x_reassigned = []
for i in range(edge_size):
    x_reassigned.append(x[i].x)

print(x_reassigned)


