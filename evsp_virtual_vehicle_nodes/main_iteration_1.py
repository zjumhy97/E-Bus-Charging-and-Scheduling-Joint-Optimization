import pickle
import os
import gurobipy as gp
from gurobipy import GRB
import numpy as np
import copy
import sys
import time

import network_haoyu.EVSPGraphVehicleNode as EGraph

trip_num = 20 # 193 50
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
vehicle_num = len(soc_ev)
graph_file_path = './graph_generated/'
pickle_file_name = 'vehicle_' + str(vehicle_num) +'_trip_' + str(trip_num) + '.pickle'
# pickle_file_name = 'vehicle_40_trip_193.pickle'
# pickle_file_name = 'vehicle_4_trip_6.pickle'

def load_graph(graph_file_path:str, pickle_file_name:str):
    """
    Load the EVSP graph from .pickle file located in the file path.

    :param graph_file_path: the file path of the .pickle file
    :param pickle_file_name: the name of the .pickle file
    :return: the EVSP graph
    """
    if os.path.exists(graph_file_path + pickle_file_name):
        with open(graph_file_path + pickle_file_name, 'rb') as f:
            graph = pickle.load(f)
            graph = graph[0]
    return graph

def path_variable_binary_check():
    """
    Check whether the path variable value solved from master problem (linear relaxation) is binary.

    :return: The truth value
    """
    result_not_int = False
    edge_is_1 = []
    x_values = []
    for i in range(edge_size):
        x_values.append(x[i].x)
        if x[i].x == 1:
            edge_is_1.append(i)
        if x[i].x != 1 and x[i].x != 0:
            result_not_int = True
    if result_not_int:
        print('*******************  Result not integer!  *******************')
    return x_values, edge_is_1

def print_eb_path():
    """
    Print the path for all of the EBs after solving the master problem.

    :return: 0
    """
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
    return 0

def print_eb_path_with_soc_charging():
    """
    Print the path of EBs with the soc variation after solving the subproblem.

    :return: 0
    """
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
                                       graph.edge_set[i].end2.start_time_str,
                                       s[graph.edge_set[i].end2.vertex_id].x,
                                       c[i].x])
                        next_vertex_id = graph.edge_set[i].end2.vertex_id
                        break
        print("(", len(path_k) - 3, ")", path_k)
    return 0

def path_reassignment(whether_reassignment:bool):
    """
    # Reassignment the EB paths according to the initial SOC.
    # k EBs, k paths.

    :param whether_reassignment:
    :return:
    """
    if whether_reassignment is True:
        x_reassignment = [x[i].x for i in range(edge_size)]
        # obtain the paths from solving the master problem
        # data structure: {vehicle: soc, length_of_path, edge_id_connect_vehicle_and_trips, first_trip_vertex }
        for k in range(vehicle_num):
            path_k = []
            if x[k].x == 1:
                path_k.extend(graph.edge_set[k].vertex_id_pair)
                next_vertex_id = graph.edge_set[k].end2.vertex_id
                while len(graph.vertex_set[next_vertex_id].edge_id_out) != 0:
                    for i in graph.vertex_set[next_vertex_id].edge_id_out:
                        if x[i].x == 1:
                            path_k.append(graph.edge_set[i].end2.vertex_id)
                            next_vertex_id = graph.edge_set[i].end2.vertex_id
                            break
            # calculate the length of paths
            length_of_path = len(path_k)
            edge_id_connect_vehicle_and_trips = graph.edge_dict[(path_k[1], path_k[2])]

        # vehicle sorted with soc

        # path sorted with length

        # reassignment

    else:
        x_reassignment = [x[i].x for i in range(edge_size)]
    return x_reassignment

solved_number = 0

graph = load_graph(graph_file_path=graph_file_path, pickle_file_name=pickle_file_name)

vertex_size, edge_size = graph.graphSize()
TIME_SLOT_NUM = int(24 * 60 / graph.time_granularity)
S_UPPER = 100
S_LOWER = 10
BIG_M = 1000000
Q_UPPER = 5
Q_TOTAL_UPPER = 5 * 10

PROBABILITY = 0.3
BETA = 0.5

# 之前的小写常量，该 code 已修改，其他两个还没改
# time_slot_num = int(24 * 60 / graph.time_granularity)
# s_upper = 100
# s_lower = 10
# M = 1000000
# q_upper = 5
# q_total_upper = 5 * 10
#
# probability = 0.3
# beta = 0.5

timer_optimize_start = time.time()
SolvedFlag = False
iteration = 0
while SolvedFlag is False:
    # Master Problem, solve problem 3
    MP = gp.Model()
    x = MP.addVars(edge_size, vtype=GRB.CONTINUOUS, name="x")

    b = np.array([vehicle_num])
    b = np.append(b, np.zeros(vertex_size-2))
    b = np.append(b, [-vehicle_num])
    # b = np.array([1] + [0 for i in range(len(vertex_info)-1)] + [-1])

    # flow constraints
    for j in range(vertex_size):
        MP.addConstr(gp.quicksum(x[i] for i in graph.vertex_set[j].edge_id_out) -
                        gp.quicksum(x[i] for i in graph.vertex_set[j].edge_id_in) == b[j])

    # exactly once constraints
    for j in range(1, vertex_size-1):
        MP.addConstr(gp.quicksum(x[i] for i in graph.vertex_set[j].edge_id_out) == 1)

    MP.setObjective(gp.quicksum(x[i] for i in range(graph.edge_size)), GRB.MAXIMIZE)
    MP.optimize()
    print('MP.Status = ', MP.Status)
    if MP.Status == 2:
        x_values, edge_is_1 = path_variable_binary_check()
        print('edge_is_1 = ', edge_is_1)
        print_eb_path()
        # reassignment the path according to initial soc
        x_reassignment = path_reassignment()
    else:
        print('MP is infeasible! need more vehicle')
        break




    # Subproblem, solve problem 4
    SP = gp.Model()

    s = SP.addVars(vertex_size, vtype=GRB.CONTINUOUS, name="s")
    w = SP.addVars(edge_size, lb=0, vtype=GRB.CONTINUOUS, name="w")
    m = SP.addVars(edge_size, lb=0, vtype=GRB.CONTINUOUS, name="m")
    c = SP.addVars(edge_size, lb=0, vtype=GRB.CONTINUOUS, name="c")
    q = SP.addVars(edge_size, TIME_SLOT_NUM, lb=0, ub=Q_UPPER, vtype=GRB.CONTINUOUS, name='q')

    # soc constraints
    SP.addConstr(s[0] == S_UPPER)
    for k in range(vehicle_num):
        SP.addConstr(s[k+1] == graph.vertex_set[k+1].soc)
    for j_index in range(trip_num):
        j = vehicle_num + 1 + j_index
        SP.addConstr(s[j] >= S_LOWER)
        SP.addConstr(s[j] <= S_LOWER - graph.vertex_set[j].energy_consumption)
    # SP.addConstr(s[vertex_size - 1] <= s_upper * vehicle_num)
    SP.addConstr(s[vertex_size - 1] == S_UPPER * vehicle_num)

    # soc evolution
    for j in range(vehicle_num + 1, vertex_size):
        e_j = graph.vertex_set[j].energy_consumption
        # SP.addConstr(s[j] == gp.quicksum(w[i] + m[i] - x[i].x * e_j for i in graph.vertex_set[j].edge_id_in))
        # x_reassignment
        SP.addConstr(s[j] == gp.quicksum(w[i] + m[i] - x_reassignment[i] * e_j for i in graph.vertex_set[j].edge_id_in))

    # bilinear constraints
    for i in range(edge_size):
        SP.addConstr(w[i] <= BIG_M * x_reassignment[i])
        SP.addConstr(w[i] >= s[graph.edge_set[i].end1.vertex_id] - BIG_M * (1 - x_reassignment[i]))
        SP.addConstr(w[i] <= s[graph.edge_set[i].end1.vertex_id] + BIG_M * (1 - x_reassignment[i]))

        SP.addConstr(m[i] <= BIG_M * x_reassignment[i])
        SP.addConstr(m[i] >= c[i] - BIG_M * (1 - x_reassignment[i]))
        SP.addConstr(m[i] <= c[i] + BIG_M * (1 - x_reassignment[i]))

        SP.addConstr(w[i] + m[i] <= S_UPPER)

    # charging constraints
    for i in range(edge_size):
        initial_time = graph.start_time
        toi = graph.edge_set[i].end1.start_time
        doi = graph.edge_set[i].end1.duration
        tdi = graph.edge_set[i].end2.start_time
        start_index = int((toi + doi - initial_time)/graph.time_granularity / 60)
        end_index = int((tdi - initial_time)/graph.time_granularity / 60)
        # constraint (1h)
        # key constraint, whether the charging amount could be achieved physically
        SP.addConstr(c[i] == gp.quicksum(q[i, t] for t in range(start_index, end_index)))

    # constraint (1j)
    for t in range(TIME_SLOT_NUM):
        SP.addConstr(gp.quicksum(q[i, t] for i in range(edge_size)) <= Q_TOTAL_UPPER)

    # electricity_price
    p = []
    for t in range(TIME_SLOT_NUM):
        time_temp = graph.start_time + t * graph.time_granularity * 60
        time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time_temp))
        p.append(graph.electricity_price(time_str, mode='TOU'))

    # 假设 5% 对应的是 5度电
    objective = gp.quicksum(p[t] * gp.quicksum(q[i, t] for i in range(edge_size)) for t in range(TIME_SLOT_NUM))
    # objective = gp.quicksum(p[t] * gp.quicksum(q[i, t] for i in range(edge_size)) for t in range(time_slot_num)) \
    #             - s[vertex_size - 1]

    SP.setObjective(objective, GRB.MINIMIZE)

    # timer_sp_optimize_start = time.time()
    SP.optimize()
    # timer_sp_optimize_end = time.time()
    # print('time (subproblem optimization) = ', timer_sp_optimize_end - timer_sp_optimize_start)

    if SP.Status == 2:
        # optimal
        print_eb_path_with_soc_charging()
        SolvedFlag = True
        print('Ha Ha Ha!')
        print('iteration = ', iteration)
    elif SP.Status == 3:
        # infeasible
        iteration += 1
        print('>> Subproblem is infeasible. iteration = ', iteration)
        # solve Problem 4a, subproblem_relaxed -> SPR
        # Subproblem Relaxation
        SPR = gp.Model()

        s = SPR.addVars(vertex_size, vtype=GRB.CONTINUOUS, name="s")
        w = SPR.addVars(edge_size, lb=0, vtype=GRB.CONTINUOUS, name="w")
        m = SPR.addVars(edge_size, lb=0, vtype=GRB.CONTINUOUS, name="m")
        c = SPR.addVars(edge_size, lb=0, vtype=GRB.CONTINUOUS, name="c")
        q = SPR.addVars(edge_size, TIME_SLOT_NUM, lb=0, ub=Q_UPPER, vtype=GRB.CONTINUOUS, name='q')

        # soc constraints
        SPR.addConstr(s[0] == S_UPPER)
        for k in range(vehicle_num):
            SPR.addConstr(s[k + 1] == graph.vertex_set[k + 1].soc)
        for j_index in range(trip_num):
            j = vehicle_num + 1 + j_index
            SPR.addConstr(s[j] >= S_LOWER)
            SPR.addConstr(s[j] <= S_UPPER - graph.vertex_set[j].energy_consumption)
        # SPR.addConstr(s[vertex_size - 1] <= s_upper * vehicle_num)
        SPR.addConstr(s[vertex_size - 1] == S_UPPER * vehicle_num)

        # soc evolution
        for j in range(vehicle_num + 1, vertex_size):
            e_j = graph.vertex_set[j].energy_consumption
            SPR.addConstr(s[j] == gp.quicksum(w[i] + m[i] - x_reassignment[i] * e_j for i in graph.vertex_set[j].edge_id_in))

        # bilinear constraints
        for i in range(edge_size):
            SPR.addConstr(w[i] <= BIG_M * x_reassignment[i])
            SPR.addConstr(w[i] >= s[graph.edge_set[i].end1.vertex_id] - BIG_M * (1 - x_reassignment[i]))
            SPR.addConstr(w[i] <= s[graph.edge_set[i].end1.vertex_id] + BIG_M * (1 - x_reassignment[i]))

            SPR.addConstr(m[i] <= BIG_M * x_reassignment[i])
            SPR.addConstr(m[i] >= c[i] - BIG_M * (1 - x_reassignment[i]))
            SPR.addConstr(m[i] <= c[i] + BIG_M * (1 - x_reassignment[i]))

            SPR.addConstr(w[i] + m[i] <= S_UPPER)

        # electricity_price
        p = []
        for t in range(TIME_SLOT_NUM):
            time_temp = graph.start_time + t * graph.time_granularity * 60
            time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time_temp))
            p.append(graph.electricity_price(time_str, mode='TOU'))

        # 假设 5% 对应的是 5度电
        objective = gp.quicksum(p[t] * gp.quicksum(q[i, t] for i in range(edge_size)) for t in range(TIME_SLOT_NUM))
        # objective = gp.quicksum(p[t] * gp.quicksum(q[i, t] for i in range(edge_size)) for t in range(time_slot_num)) \
        #             - s[vertex_size - 1]

        SPR.setObjective(objective, GRB.MINIMIZE)

        # timer_sp_optimize_start = time.time()
        SPR.optimize()
        # timer_sp_optimize_end = time.time()
        # print('time (subproblem optimization) = ', timer_sp_optimize_end - timer_sp_optimize_start)
        # print_eb_path_with_soc_charging()

        # violation check
        violation_trips = []
        trip_info = graph.trip_info

        for i in range(edge_size):
            toi = graph.edge_set[i].end1.start_time
            doi = graph.edge_set[i].end1.duration
            tdi = graph.edge_set[i].end2.start_time
            if x[i].x == 1 and c[i].x > Q_UPPER * ((tdi - toi - doi) / graph.time_granularity / 60):
                violation_trips.append(graph.edge_set[i].end1.vertex_id)
                oi = graph.edge_set[i].end1.vertex_id
                di = graph.edge_set[i].end2.vertex_id
                # trip duration modification
                alpha = np.random.choice([0, 1], p=[PROBABILITY, 1 - PROBABILITY])
                trip_info['trip' + str(oi - vehicle_num - 1)]['duration'] \
                    += alpha * BETA * (graph.vertex_set[di].energy_consumption / Q_UPPER) * graph.time_granularity

        # graph update
        time_granularity = graph.time_granularity
        soc_ev = graph.soc_ev
        start_time = graph.start_time
        end_time = graph.end_time
        graph = EGraph.EVSPGraph(time_granularity=time_granularity, soc_ev=soc_ev, trip_info=trip_info,
                                 start_time=start_time, end_time=end_time)
        graph.construct_graph()
        vertex_size, edge_size = graph.graphSize()

timer_optimize_end = time.time()
print('time (optimization) = ', timer_optimize_end - timer_optimize_start)


