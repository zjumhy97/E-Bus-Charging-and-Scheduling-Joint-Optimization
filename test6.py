import pickle
import os
import gurobipy as gp
from gurobipy import GRB
import numpy as np
import copy
import sys
import time
import network_haoyu.EVSPExtentedGraph as EGraph
import csv

if os.path.exists('line_3_time_5_soc_30_trip_193.pickle'):
    with open('line_3_time_5_soc_30_trip_193.pickle', 'rb') as f:
        graph = pickle.load(f)
        graph = graph[0]


vertex_size, edge_size = graph.graphSize()

# model = gp.Model()
# x = model.read('line_3_time_5_soc_30_trip_193_out.sol')


with open('line_3_time_5_soc_30_trip_193_out.sol', newline='\n') as csvfile:
    reader = csv.reader((line.replace('  ', ' ') for line in csvfile), delimiter=' ')
    next(reader)  # skip header
    x=[]
    for var, value in reader:
        x.append(float(value))

print(1)


edge = graph.edge_set[14942]
end1 = edge.end1
end2 = edge.end2

time_slot = int(24 * 60 / graph.time_granularity)
charger_number_list = np.zeros(time_slot + 1)
for i in range(edge_size):
    if graph.edge_set[i].attribute == 'charging' and x[i] == 1:
        index = int((graph.edge_set[i].end1.start_time - graph.start_time) / graph.time_granularity / 60)
        print('i=',i)
        print(index)
        charger_number_list[index] += 1

print(charger_number_list)