import pickle
import os
import gurobipy as gp
from gurobipy import GRB
import numpy as np
import copy
import sys
import time

vehicle_num = 4

if os.path.exists('line_4_time_5_soc_30_trip_579.pickle'):
    with open('line_4_time_5_soc_30_trip_579.pickle', 'rb') as f:
        graph = pickle.load(f)
        graph = graph[0]


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


model.setObjective()

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

