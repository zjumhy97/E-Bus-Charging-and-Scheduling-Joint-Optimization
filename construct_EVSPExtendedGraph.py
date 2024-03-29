import pickle
import os
import gurobipy as gp
from gurobipy import GRB
import numpy as np
import copy
import sys
import time
import network_haoyu.EVSPExtentedGraph as EGraph


# 根据输入的节点，建立符合时间约束的有向无环图
# [1, 'task', '2022-03-24 07:00:00 -> 19:00:00', 45, 3]
trip_info_line_0 = [
    [0, 'origin', '2022-03-24 06:45:00', 1, 0],
    [1, 'task', '2022-03-24 07:00:00', 45, 3],
    [2, 'task', '2022-03-24 07:15:00', 45, 3],
    [3, 'task', '2022-03-24 07:30:00', 45, 3],
    [4, 'task', '2022-03-24 07:45:00', 45, 3],
    [5, 'task', '2022-03-24 08:00:00', 45, 3],
    [6, 'task', '2022-03-24 08:15:00', 45, 3],
    [7, 'task', '2022-03-24 08:30:00', 45, 3],
    [8, 'task', '2022-03-24 08:45:00', 45, 3],
    [9, 'task', '2022-03-24 09:00:00', 45, 3],
    [10, 'task', '2022-03-24 09:15:00', 45, 3],
    [11, 'task', '2022-03-24 09:30:00', 45, 3],
    [12, 'task', '2022-03-24 09:45:00', 45, 3],
    [13, 'task', '2022-03-24 10:00:00', 45, 3],
    [14, 'task', '2022-03-24 10:15:00', 45, 3],
    [15, 'task', '2022-03-24 10:30:00', 45, 3],
    [16, 'task', '2022-03-24 10:45:00', 45, 3],
    [17, 'task', '2022-03-24 11:00:00', 45, 3],
    [18, 'task', '2022-03-24 11:15:00', 45, 3],
    [19, 'task', '2022-03-24 11:30:00', 45, 3],
    [20, 'task', '2022-03-24 11:45:00', 45, 3],
    [21, 'task', '2022-03-24 12:00:00', 45, 3],
    [22, 'task', '2022-03-24 12:15:00', 45, 3],
    [23, 'task', '2022-03-24 12:30:00', 45, 3],
    [24, 'task', '2022-03-24 12:45:00', 45, 3],
    [25, 'task', '2022-03-24 13:00:00', 45, 3],
    [26, 'task', '2022-03-24 13:15:00', 45, 3],
    [27, 'task', '2022-03-24 13:30:00', 45, 3],
    [28, 'task', '2022-03-24 13:45:00', 45, 3],
    [29, 'task', '2022-03-24 14:00:00', 45, 3],
    [30, 'task', '2022-03-24 14:15:00', 45, 3],
    [31, 'task', '2022-03-24 14:30:00', 45, 3],
    [32, 'task', '2022-03-24 14:45:00', 45, 3],
    [33, 'task', '2022-03-24 15:00:00', 45, 3],
    [34, 'task', '2022-03-24 15:15:00', 45, 3],
    [35, 'task', '2022-03-24 15:30:00', 45, 3],
    [36, 'task', '2022-03-24 15:45:00', 45, 3],
    [37, 'task', '2022-03-24 16:00:00', 45, 3],
    [38, 'task', '2022-03-24 16:15:00', 45, 3],
    [39, 'task', '2022-03-24 16:30:00', 45, 3],
    [40, 'task', '2022-03-24 16:45:00', 45, 3],
    [41, 'task', '2022-03-24 17:00:00', 45, 3],
    [42, 'task', '2022-03-24 17:15:00', 45, 3],
    [43, 'task', '2022-03-24 17:30:00', 45, 3],
    [44, 'task', '2022-03-24 17:45:00', 45, 3],
    [45, 'task', '2022-03-24 18:00:00', 45, 3],
    [46, 'task', '2022-03-24 18:15:00', 45, 3],
    [47, 'task', '2022-03-24 18:30:00', 45, 3],
    [48, 'task', '2022-03-24 18:45:00', 45, 3],
    [49, 'task', '2022-03-24 19:00:00', 45, 3],
    # # 下面应该没用了
    # [2, 'destination', '2022-03-24 23:58:00', 1],
]
# graph = EGraph.EVSPExtentedGraph(time_granularity=15, soc_level_number=10,
#                                   soc_level_lower_limit=1, battery_capacity=300)


# [1, 'task', '2022-03-24 06:00:00 -> 22:00:00', 180, 12]
trip_info_line_1 = [
    [0, 'origin', '2022-03-24 05:45:00', 1, 0],
    [1, 'task', '2022-03-24 06:00:00', 180, 9],
    [2, 'task', '2022-03-24 06:15:00', 180, 9],
    [3, 'task', '2022-03-24 06:30:00', 180, 9],
    [4, 'task', '2022-03-24 06:45:00', 180, 9],
    [5, 'task', '2022-03-24 07:00:00', 180, 9],
    [6, 'task', '2022-03-24 07:15:00', 180, 9],
    [7, 'task', '2022-03-24 07:30:00', 180, 9],
    [8, 'task', '2022-03-24 07:45:00', 180, 9],
    [9, 'task', '2022-03-24 08:00:00', 180, 9],
    [10, 'task', '2022-03-24 08:15:00', 180, 9],
    [11, 'task', '2022-03-24 08:30:00', 180, 9],
    [12, 'task', '2022-03-24 08:45:00', 180, 9],
    [13, 'task', '2022-03-24 09:00:00', 180, 9],
    [14, 'task', '2022-03-24 09:15:00', 180, 9],
    [15, 'task', '2022-03-24 09:30:00', 180, 9],
    [16, 'task', '2022-03-24 09:45:00', 180, 9],
    [17, 'task', '2022-03-24 10:00:00', 180, 9],
    [18, 'task', '2022-03-24 10:15:00', 180, 9],
    [19, 'task', '2022-03-24 10:30:00', 180, 9],
    [20, 'task', '2022-03-24 10:45:00', 180, 9],
    [21, 'task', '2022-03-24 11:00:00', 180, 9],
    [22, 'task', '2022-03-24 11:15:00', 180, 9],
    [23, 'task', '2022-03-24 11:30:00', 180, 9],
    [24, 'task', '2022-03-24 11:45:00', 180, 9],
    [25, 'task', '2022-03-24 12:00:00', 180, 9],
    [26, 'task', '2022-03-24 12:15:00', 180, 9],
    [27, 'task', '2022-03-24 12:30:00', 180, 9],
    [28, 'task', '2022-03-24 12:45:00', 180, 9],
    [29, 'task', '2022-03-24 13:00:00', 180, 9],
    [30, 'task', '2022-03-24 13:15:00', 180, 9],
    [31, 'task', '2022-03-24 13:30:00', 180, 9],
    [32, 'task', '2022-03-24 13:45:00', 180, 9],
    [33, 'task', '2022-03-24 14:00:00', 180, 9],
    [34, 'task', '2022-03-24 14:15:00', 180, 9],
    [35, 'task', '2022-03-24 14:30:00', 180, 9],
    [36, 'task', '2022-03-24 14:45:00', 180, 9],
    [37, 'task', '2022-03-24 15:00:00', 180, 9],
    [38, 'task', '2022-03-24 15:15:00', 180, 9],
    [39, 'task', '2022-03-24 15:30:00', 180, 9],
    [40, 'task', '2022-03-24 15:45:00', 180, 9],
    [41, 'task', '2022-03-24 16:00:00', 180, 9],
    [42, 'task', '2022-03-24 16:15:00', 180, 9],
    [43, 'task', '2022-03-24 16:30:00', 180, 9],
    [44, 'task', '2022-03-24 16:45:00', 180, 9],
    [45, 'task', '2022-03-24 17:00:00', 180, 9],
    [46, 'task', '2022-03-24 17:15:00', 180, 9],
    [47, 'task', '2022-03-24 17:30:00', 180, 9],
    [48, 'task', '2022-03-24 17:45:00', 180, 9],
    [49, 'task', '2022-03-24 18:00:00', 180, 9],
    [50, 'task', '2022-03-24 18:15:00', 180, 9],
    [51, 'task', '2022-03-24 18:30:00', 180, 9],
    [52, 'task', '2022-03-24 18:45:00', 180, 9],
    [53, 'task', '2022-03-24 19:00:00', 180, 9],
    [54, 'task', '2022-03-24 19:15:00', 180, 9],
    [55, 'task', '2022-03-24 19:30:00', 180, 9],
    [56, 'task', '2022-03-24 19:45:00', 180, 9],
    [57, 'task', '2022-03-24 20:00:00', 180, 9],
    [58, 'task', '2022-03-24 20:15:00', 180, 9],
    [59, 'task', '2022-03-24 20:30:00', 180, 9],
    [60, 'task', '2022-03-24 20:45:00', 180, 9],
    [61, 'task', '2022-03-24 21:00:00', 180, 9],
    [62, 'task', '2022-03-24 21:15:00', 180, 9],
    [63, 'task', '2022-03-24 21:30:00', 180, 9],
    [64, 'task', '2022-03-24 21:45:00', 180, 9],
    [65, 'task', '2022-03-24 22:00:00', 180, 9],
]
# graph = EGraph.EVSPExtentedGraph(time_granularity=5, soc_level_number=30,
#                                  soc_level_lower_limit=1, battery_capacity=300)

# [1, 'task', '2022-03-24 06:00:00 -> 22:00:00', 180, 3]
trip_info_line_2 = [
    [0, 'origin', '2022-03-24 05:45:00', 1, 0],
    [1, 'task', '2022-03-24 06:00:00', 180, 3],
    [2, 'task', '2022-03-24 06:15:00', 180, 3],
    [3, 'task', '2022-03-24 06:30:00', 180, 3],
    [4, 'task', '2022-03-24 06:45:00', 180, 3],
    [5, 'task', '2022-03-24 07:00:00', 180, 3],
    [6, 'task', '2022-03-24 07:15:00', 180, 3],
    [7, 'task', '2022-03-24 07:30:00', 180, 3],
    [8, 'task', '2022-03-24 07:45:00', 180, 3],
    [9, 'task', '2022-03-24 08:00:00', 180, 3],
    [10, 'task', '2022-03-24 08:15:00', 180, 3],
    [11, 'task', '2022-03-24 08:30:00', 180, 3],
    [12, 'task', '2022-03-24 08:45:00', 180, 3],
    [13, 'task', '2022-03-24 09:00:00', 180, 3],
    [14, 'task', '2022-03-24 09:15:00', 180, 3],
    [15, 'task', '2022-03-24 09:30:00', 180, 3],
    [16, 'task', '2022-03-24 09:45:00', 180, 3],
    [17, 'task', '2022-03-24 10:00:00', 180, 3],
    [18, 'task', '2022-03-24 10:15:00', 180, 3],
    [19, 'task', '2022-03-24 10:30:00', 180, 3],
    [20, 'task', '2022-03-24 10:45:00', 180, 3],
    [21, 'task', '2022-03-24 11:00:00', 180, 3],
    [22, 'task', '2022-03-24 11:15:00', 180, 3],
    [23, 'task', '2022-03-24 11:30:00', 180, 3],
    [24, 'task', '2022-03-24 11:45:00', 180, 3],
    [25, 'task', '2022-03-24 12:00:00', 180, 3],
    [26, 'task', '2022-03-24 12:15:00', 180, 3],
    [27, 'task', '2022-03-24 12:30:00', 180, 3],
    [28, 'task', '2022-03-24 12:45:00', 180, 3],
    [29, 'task', '2022-03-24 13:00:00', 180, 3],
    [30, 'task', '2022-03-24 13:15:00', 180, 3],
    [31, 'task', '2022-03-24 13:30:00', 180, 3],
    [32, 'task', '2022-03-24 13:45:00', 180, 3],
    [33, 'task', '2022-03-24 14:00:00', 180, 3],
    [34, 'task', '2022-03-24 14:15:00', 180, 3],
    [35, 'task', '2022-03-24 14:30:00', 180, 3],
    [36, 'task', '2022-03-24 14:45:00', 180, 3],
    [37, 'task', '2022-03-24 15:00:00', 180, 3],
    [38, 'task', '2022-03-24 15:15:00', 180, 3],
    [39, 'task', '2022-03-24 15:30:00', 180, 3],
    [40, 'task', '2022-03-24 15:45:00', 180, 3],
    [41, 'task', '2022-03-24 16:00:00', 180, 3],
    [42, 'task', '2022-03-24 16:15:00', 180, 3],
    [43, 'task', '2022-03-24 16:30:00', 180, 3],
    [44, 'task', '2022-03-24 16:45:00', 180, 3],
    [45, 'task', '2022-03-24 17:00:00', 180, 3],
    [46, 'task', '2022-03-24 17:15:00', 180, 3],
    [47, 'task', '2022-03-24 17:30:00', 180, 3],
    [48, 'task', '2022-03-24 17:45:00', 180, 3],
    [49, 'task', '2022-03-24 18:00:00', 180, 3],
    [50, 'task', '2022-03-24 18:15:00', 180, 3],
    [51, 'task', '2022-03-24 18:30:00', 180, 3],
    [52, 'task', '2022-03-24 18:45:00', 180, 3],
    [53, 'task', '2022-03-24 19:00:00', 180, 3],
    [54, 'task', '2022-03-24 19:15:00', 180, 3],
    [55, 'task', '2022-03-24 19:30:00', 180, 3],
    [56, 'task', '2022-03-24 19:45:00', 180, 3],
    [57, 'task', '2022-03-24 20:00:00', 180, 3],
    [58, 'task', '2022-03-24 20:15:00', 180, 3],
    [59, 'task', '2022-03-24 20:30:00', 180, 3],
    [60, 'task', '2022-03-24 20:45:00', 180, 3],
    [61, 'task', '2022-03-24 21:00:00', 180, 3],
    [62, 'task', '2022-03-24 21:15:00', 180, 3],
    [63, 'task', '2022-03-24 21:30:00', 180, 3],
    [64, 'task', '2022-03-24 21:45:00', 180, 3],
    [65, 'task', '2022-03-24 22:00:00', 180, 3],
]
# graph = EGraph.EVSPExtentedGraph(time_granularity=15, soc_level_number=10,
#                                  soc_level_lower_limit=1, battery_capacity=300,
#                                  charger_number=5)

trip_info_line_3 = []
trip_info_line_3.append([0, 'origin', '2022-03-24 05:45:00', 1, 0])
time_index = int(time.mktime(time.strptime('2022-03-24 06:00:00', "%Y-%m-%d %H:%M:%S")))
for i in range(1, 194):
    trip_info_line_3.append([i, 'task', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time_index)), 180, 9])
    time_index += 5*60
# graph = EGraph.EVSPExtentedGraph(time_granularity=5, soc_level_number=30,
#                                  soc_level_lower_limit=1, battery_capacity=300,charger_number=15)


trip_info_line_4 = []
trip_info_line_4.append([0, 'origin', '2022-03-24 05:45:00', 1, 0])
time_index = int(time.mktime(time.strptime('2022-03-24 06:00:00', "%Y-%m-%d %H:%M:%S")))
for i in range(1, 194):
    trip_info_line_4.append([3*i - 2, 'task', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time_index)), 180, 9])
    trip_info_line_4.append([3*i - 1, 'task', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time_index)), 180, 9])
    trip_info_line_4.append([3*i, 'task', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time_index)), 180, 9])
    time_index += 5*60
graph = EGraph.EVSPExtentedGraph(time_granularity=5, soc_level_number=30,
                                 soc_level_lower_limit=1, battery_capacity=300, charger_number=15)



timer_0 = time.time()

graph.constructGraph(trip_info=trip_info_line_4)

timer_construct_graph = time.time()

with open('line_4_time_5_soc_30_trip_579.pickle', 'wb') as f:
    pickle.dump([graph], f)


print('time (construct graph) = ', timer_construct_graph - timer_0)


































