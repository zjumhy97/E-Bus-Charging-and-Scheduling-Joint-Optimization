import pickle
import os
import gurobipy as gp
from gurobipy import GRB
import numpy as np
import copy
import sys
import time

trip_num = 50 # 193 50
soc_ev = {'粤B12345': 100,
          '粤B13456': 90,
          '粤B14567': 80,
          '粤B15678': 70,
          '粤B16789': 80,
          '粤B17890': 70,
          '粤B18901': 70,
          '粤B19012': 80,
          '粤B10123': 70,
          '粤B11234': 70,
          '粤B22345': 100,
          '粤B23456': 90,
          '粤B24567': 80,
          '粤B25678': 70,
          '粤B26789': 80,
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
vehicle_num = len(soc_ev)
graph_file_path = './graph_generated/'
pickle_file_name = 'vehicle_15_trip_50.pickle'
# pickle_file_name = 'vehicle_40_trip_193.pickle'
# pickle_file_name = 'vehicle_4_trip_6.pickle'

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
q_total_upper = 5 * 20


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
    initial_time_str = graph.edge_set[i].end1.start_time_str[0:11] + '00:00:00'
    initial_time = int(time.mktime(time.strptime(initial_time_str, "%Y-%m-%d %H:%M:%S")))
    toi = graph.edge_set[i].end1.start_time
    doi = graph.edge_set[i].end1.duration
    index = int((toi + doi - initial_time)/graph.time_granularity / 60)
    model.addConstr(c[i] == gp.quicksum(q[i, t] for t in range(index, time_slot_num)))


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




