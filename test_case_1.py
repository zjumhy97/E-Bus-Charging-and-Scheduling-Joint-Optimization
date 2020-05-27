#!/usr/bin/env python3.7

# Copyright 2020, Haoyu Miao

# This Program is for the Joint optimization of the E-Bus Charging and Scheduling
# The problem is formulated as an MILP, and the Benders Decompositon is adopted.

import numpy as np
import scipy.sparse as sp
import gurobipy as gp
from gurobipy import GRB
import E_Bus_Output as eop

## PART I. Parameters

## Time Slot L
L_test = list(range(1,26))

## Time Table & Trip
# Trip_start and Trip_end are virtual vertex in the graph
Trip,Trip_time,Duration_time = gp.multidict({
    "Trip_start" : [0,0],
    "Trip_1" : [1,3],"Trip_2" : [3,3],"Trip_3" : [5,3],"Trip_4" : [7,3],"Trip_5" : [9,3],"Trip_6" : [11,3],
    "Trip_7" : [13,3],"Trip_8" : [15,3],"Trip_9" : [17,3],"Trip_10" : [19,3],"Trip_11" : [21,3],"Trip_12" : [23,3],
    "Trip_end" : [26,0]
})
# Constant b for the constraint
b = [0 for _ in range(len(Trip))]
b[0] = 1
b[-1] = -1

## Bus Fleet K
E_Bus, SOC_MIN, SOC_MAX, Battery_Capacity, Energy_per_Trip_Win, Energy_per_Trip_Sum = gp.multidict({
    "JL_1" : [30,100,150,50,65.8],
    "JL_2" : [30,100,150,50,65.8],
    "JL_3" : [30,100,150,50,65.8],
    #"JL_4" : [30,100,160,47,65.8],
    #"JL_5" : [30,100,160,47,65.8],
    #"JL_6" : [30,100,160,47,65.8],
    #"JL_7" : [30,100,160,47,65.8],
    #"JL_8" : [30,100,160,47,65.8],
    #"JL_9" : [30,100,160,47,65.8],
    #"JL_10" : [30,100,160,47,65.8],
})


# 有一些新添加的变量
# c = np.zeros(len(L_test)+1)
# for i in range(len(L_test)+1):
#    c[i] = 0.637 # 电价
# 这个测试案例是考虑25个time slots
c = [5,5,5,5,5,5,5,5,5,
     2,2,2,2,2,2,2,
     6,6,6,6,6,6,6,6,6]


d = 0 # 峰值功率对应的电价，测试时先将 d = 0，暂时不考虑峰值功率的影响，先考虑基本功率

# K 和 I 两个还需要定义
I = np.zeros((len(Trip),len(Trip),len(L_test)+1))
for i in range(1, len(Trip) - 1):
    for j in range(1, len(Trip) - 1):
        for l in range(1,len(L_test)+1):
            if l >= Trip_time.values()[i] + Duration_time.values()[i] and l <= Trip_time.values()[j] - 1 :
                I[i,j,l] = 1
                print("I[",i,",",j,",",l,"] = ",I[i,j,l] )


K = np.zeros((len(Trip),len(Trip)))
for i in range(len(Trip)):
    for j in range(len(Trip)):
        if Trip_time.values()[i] + Duration_time.values()[i] <= Trip_time.values()[j]:
            K[i,j] = 1

miu = 1000
M1 = 10000
M2 = 10000
delta = 50
Sbar = 150

# 先测试每趟车能不能跑通，离散变量有没有可行解
try:
    MP = gp.Model()      # Benders Master Problem
    x = MP.addVars(range(len(Trip)),range(len(Trip)),range(1,len(E_Bus)+1),vtype=GRB.BINARY,name="x")
    z = MP.addVar(vtype=GRB.CONTINUOUS, name="z")  # objective value of SubProblem
    MP.update()

    # Add Constraints
    # 测试通过
    for i in range(len(Trip)):
        for k in range(1, len(E_Bus) + 1):
            MP.addConstr(
                gp.quicksum(x[i, j, k] for j in range(len(Trip))) - gp.quicksum(x[j, i, k] for j in range(len(Trip))) ==
                b[i])
    # 测试通过，但有可能有直接从 start 到 end 的车辆，这样子这个车辆相当于没有用
    for i in range(1, len(Trip) - 1):
        MP.addConstr(gp.quicksum(x[i, j, k] for j in range(len(Trip)) if i < j for k in range(1, len(E_Bus) + 1)) == 1)

    # 测试通过，下三角为0
    for i in range(len(Trip)):
        for j in range(len(Trip)):
            if i >= j:
                MP.addConstr(gp.quicksum(x[i, j, k] for k in range(1, len(E_Bus) + 1)) == 0)

    # 测试通过
    for i in range(len(Trip) - 1):
        for j in range(1, len(Trip)):
            for k in range(1, len(E_Bus) + 1):
                MP.addConstr((Trip_time.values()[i] + Duration_time.values()[i]) * x[i, j, k] <= Trip_time.values()[j])

    # 测试通过，证明该测试案例仅考虑路网约束，不考虑电量约束的情况下，有多个解
    # 这里我再添加一个测试约束：每趟车不能跑多于4个trip，如果添加该约束依然有解，说明 可行域肯定不止一个解
    # for k in range(1,len(E_Bus)+1):
    #    MP.addConstr(gp.quicksum(x[i, j, k] for i in range(len(Trip)) for j in range(len(Trip))) <= 5)

    # Set Objective function, 这个目标函数我不确定，不过下面那个是 test2.py 测试过的
    MP.setObjective(z,sense=GRB.MINIMIZE)

    MP.optimize()
    print('MP RESULT:')

    # 测试电动公交车的路线输出
    x_array = eop.transform_decision_variable_to_array(x,len(Trip),len(E_Bus))
    print('-----------------------------------')
    eop.print_E_Bus_Path(len(E_Bus),x_array)
    print('-----------------------------------')

except:
    print("wow")