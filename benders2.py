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
# 这个测试案例是考虑25个time slots
c = [5,5,5,5,5,5,5,5,5,
     2,2,2,2,2,2,2,
     6,6,6,6,6,6,6,6,6]


d = 0 # 峰值功率对应的电价，测试时先将 d = 0，暂时不考虑峰值功率的影响，先考虑基本功率

# K 和 I 两个还需要定义
# I 表示在第i个trip和第j个trip之间，在第l个time slot内可以充电
I = np.zeros((len(Trip),len(Trip),len(L_test)+1))
for i in range(1, len(Trip) - 1):
    for j in range(1, len(Trip) - 1):
        for l in range(1,len(L_test) + 1):
            if l >= Trip_time.values()[i] + Duration_time.values()[i] and l <= Trip_time.values()[j] - 1 :
                I[i,j,l] = 1

K = np.zeros((len(Trip),len(Trip)))
for i in range(len(Trip)):
    for j in range(len(Trip)):
        if Trip_time.values()[i] + Duration_time.values()[i] <= Trip_time.values()[j]:
            K[i,j] = 1

miu = 17
M1 = 1000
M2 = 1000
delta = 50
Sbar = 150

# write data to file
filename = "E_Bus_iteration_data.txt"


## PART II. Benders Decomposition
def addBendersCuts(SP_Dual_obj, x_for_cut):
    if SP_Dual.status == GRB.Status.UNBOUNDED:
        ray = SP_Dual.UnbdRay

        # 测试 print ray
        print(ray)
        print(sum(ray))

        split_length = [len(Trip) * len(Trip) * len(E_Bus), len(Trip) * len(Trip) * len(E_Bus),
                        len(Trip) * len(Trip) * len(E_Bus), len(Trip) * len(Trip) * len(E_Bus),
                        len(Trip) * len(Trip) * len(E_Bus), len(Trip) * len(Trip) * len(E_Bus),
                        len(Trip) * len(Trip) * len(E_Bus), len(Trip) * len(Trip) * len(E_Bus),
                        len(Trip) - 2, len(Trip) - 2, len(Trip) - 1,
                        len(Trip) * len(Trip) * len(L_test), len(Trip) * len(Trip) * len(L_test),
                        len(L_test)]

        print('split_length = ', split_length)

        ray_split = eop.list_split_to_given_length(ray, split_length)

        print(ray_split[0])
        print(ray_split[8])
        print(ray_split[9])
        print(ray_split[12])

        MP.addConstr(sum((M1 * (- ray_split[0][i * len(Trip) * len(E_Bus) + j * len(E_Bus) + k - 1] -
                                ray_split[1][i * len(Trip) * len(E_Bus) + j * len(E_Bus) + k - 1] +
                                ray_split[2][i * len(Trip) * len(E_Bus) + j * len(E_Bus) + k - 1] +
                                ray_split[3][i * len(Trip) * len(E_Bus) + j * len(E_Bus) + k - 1]) +
                          M2 * (- ray_split[4][i * len(Trip) * len(E_Bus) + j * len(E_Bus) + k - 1] -
                                ray_split[5][i * len(Trip) * len(E_Bus) + j * len(E_Bus) + k - 1] +
                                ray_split[6][i * len(Trip) * len(E_Bus) + j * len(E_Bus) + k - 1] +
                                ray_split[7][i * len(Trip) * len(E_Bus) + j * len(E_Bus) + k - 1])) * x[i, j, k] \
                         for i in range(len(Trip)) for j in range(len(Trip)) for k in
                         range(1, len(E_Bus) + 1)) + \
                     sum((M1 * (- ray_split[2][i * len(Trip) * len(E_Bus) + j * len(E_Bus) + k - 1] -
                                ray_split[3][i * len(Trip) * len(E_Bus) + j * len(E_Bus) + k - 1]) +
                          M2 * (-ray_split[6][i * len(Trip) * len(E_Bus) + j * len(E_Bus) + k - 1] -
                                ray_split[7][i * len(Trip) * len(E_Bus) + j * len(E_Bus) + k - 1])) \
                         for i in range(len(Trip)) for j in range(len(Trip)) for k in
                         range(1, len(E_Bus) + 1)) + \
                     sum(ray_split[9][i - 1] for i in range(1, len(Trip) - 1)) * (- Sbar + delta) - \
                     ray_split[10][0] * Sbar + \
                     sum(ray_split[10][i] for i in range(1, len(Trip) - 1)) * delta - \
                     miu * sum(ray_split[12][i * len(Trip) * len(E_Bus) + j * len(E_Bus) + l - 1] \
                               for i in range(len(Trip)) for j in range(len(Trip))
                               for l in range(1, len(L_test) + 1)) <= 0)


    elif SP_Dual.status == GRB.Status.OPTIMAL:
        MP.addConstr(sum((M1 * (-ua[i, j, k].x - ub[i, j, k].x + uc[i, j, k].x + ud[i, j, k].x) +
                          M2 * (-ue[i, j, k].x - uf[i, j, k].x + ug[i, j, k].x + uh[i, j, k].x)) * x[i, j, k] \
                         for i in range(len(Trip)) for j in range(len(Trip)) for k in
                         range(1, len(E_Bus) + 1)) + \
                     sum((M1 * (-uc[i, j, k].x - ud[i, j, k].x) + M2 * (-ug[i, j, k].x - uh[i, j, k].x)) \
                         for i in range(len(Trip)) for j in range(len(Trip)) for k in
                         range(1, len(E_Bus) + 1)) + \
                     sum(uj[i].x for i in range(1, len(Trip) - 1)) * (- Sbar + delta) - uk[0].x * Sbar + \
                     sum(uk[i].x for i in range(1, len(Trip) - 1)) * delta - \
                     miu * sum(um[i, j, l].x for i in range(len(Trip)) for j in range(len(Trip))
                               for l in range(1, len(L_test) + 1)) <= z)

        SP_Dual_obj[0] = SP_Dual.objVal

        # 为 x_for_cut 添加Dual 的 constraint 的 price 值，这个下面的内容得改
        # 这里有问题

        for i in range(len(Trip)):
            for j in range(len(Trip)):
                for l in range(1, len(L_test) + 1):
                    x_for_cut.append(globals()['csrt1_' + str(i) + '_' + str(j) + '_' + str(l)].pi)
                    if globals()['csrt1_' + str(i) + '_' + str(j) + '_' + str(l)].pi != 0:
                        print("q_{%s,%s}^%s = %s" % (i, j, l, globals()['csrt1_' + str(i) + '_' + str(j) + '_' + str(l)].pi))

        x_for_cut.append(csrt2.pi)

        for i in range(len(Trip)):
            for j in range(len(Trip)):
                for k in range(1, len(E_Bus) + 1):
                    x_for_cut.append(globals()['csrt3_' + str(i) + '_' + str(j) + '_' + str(k)].pi)

        for i in range(len(Trip)):
            for j in range(len(Trip)):
                for k in range(1, len(E_Bus) + 1):
                    x_for_cut.append(globals()['csrt4_' + str(i) + '_' + str(j) + '_' + str(k)].pi)

        for i in range(len(Trip)):
            x_for_cut.append(globals()['csrt5_' + str(i)].pi)
            print("S_",str(i),"=", globals()['csrt5_' + str(i)].pi)

    else:
        print(SP_Dual.status)


try:
    # LowerBound and UpperBound
    LB = -100000000000
    UB = 100000000000

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

    # Set Objective function, 这个目标函数我不确定，不过下面那个是 test2.py 测试过的
    MP.setObjective(gp.quicksum(x) + z,sense=GRB.MINIMIZE)

    # MP.setObjective(z - 2 * gp.quicksum(x[0,len(Trip)-1,k] for k in range(1,len(E_Bus)+1)) ,sense=GRB.MINIMIZE)

    SP_Dual = gp.Model()
    ua = SP_Dual.addVars(range(len(Trip)), range(len(Trip)), range(1, len(E_Bus) + 1), lb=0, vtype=GRB.CONTINUOUS,
                         name="ua")
    ub = SP_Dual.addVars(range(len(Trip)), range(len(Trip)), range(1, len(E_Bus) + 1), lb=0, vtype=GRB.CONTINUOUS,
                         name="ub")
    uc = SP_Dual.addVars(range(len(Trip)), range(len(Trip)), range(1, len(E_Bus) + 1), lb=0, vtype=GRB.CONTINUOUS,
                         name="uc")
    ud = SP_Dual.addVars(range(len(Trip)), range(len(Trip)), range(1, len(E_Bus) + 1), lb=0, vtype=GRB.CONTINUOUS,
                         name="ud")
    ue = SP_Dual.addVars(range(len(Trip)), range(len(Trip)), range(1, len(E_Bus) + 1), lb=0, vtype=GRB.CONTINUOUS,
                         name="ue")
    uf = SP_Dual.addVars(range(len(Trip)), range(len(Trip)), range(1, len(E_Bus) + 1), lb=0, vtype=GRB.CONTINUOUS,
                         name="uf")
    ug = SP_Dual.addVars(range(len(Trip)), range(len(Trip)), range(1, len(E_Bus) + 1), lb=0, vtype=GRB.CONTINUOUS,
                         name="ug")
    uh = SP_Dual.addVars(range(len(Trip)), range(len(Trip)), range(1, len(E_Bus) + 1), lb=0, vtype=GRB.CONTINUOUS,
                         name="uh")
    ui = SP_Dual.addVars(range(1, len(Trip) - 1), lb=0, vtype=GRB.CONTINUOUS, name="ui")
    uj = SP_Dual.addVars(range(1, len(Trip) - 1), lb=0, vtype=GRB.CONTINUOUS, name="uj")
    uk = SP_Dual.addVars(range(len(Trip) - 1), lb=-GRB.INFINITY, vtype=GRB.CONTINUOUS, name="uk")
    ul = SP_Dual.addVars(range(len(Trip)), range(len(Trip)), range(1, len(L_test) + 1), lb=0, vtype=GRB.CONTINUOUS,
                         name="ul")
    um = SP_Dual.addVars(range(len(Trip)), range(len(Trip)), range(1, len(L_test) + 1), lb=0, vtype=GRB.CONTINUOUS,
                         name="um")
    un = SP_Dual.addVars(range(1, len(L_test) + 1), lb=0, vtype=GRB.CONTINUOUS, name="un")


    SP_Dual.update()
    # 添加 SP_Dual 的 constraints
    for i in range(len(Trip)):
        for j in range(len(Trip)):
            for l in range(1, len(L_test) + 1):
                globals()['csrt1_' + str(i) + '_' + str(j) + '_' + str(l)] = SP_Dual.addConstr(
                        c[l - 1] * I[i, j, l] - ul[i, j, l] + um[i, j, l] + I[i, j, l] * gp.quicksum(ug[i, j, k] - uh[i, j, k] \
                        for k in range(1, len(E_Bus) + 1)) + un[l] * I[i, j, l] >= 0)


    csrt2 = SP_Dual.addConstr(d - gp.quicksum(un) >= 0)

    for i in range(len(Trip)):
        for j in range(len(Trip)):
            if j == 0:
                for k in range(1, len(E_Bus)+1):
                    globals()['csrt3_' + str(i) + '_' + str(j) + '_' + str(k)] = \
                        SP_Dual.addConstr(-ua[i, j, k] + ub[i, j, k] - uc[i, j, k] + ud[i, j, k] >= 0)
            elif j == len(Trip) - 1:
                for k in range(1, len(E_Bus)+1):
                    globals()['csrt3_' + str(i) + '_' + str(j) + '_' + str(k)] = \
                        SP_Dual.addConstr(-ua[i, j, k] + ub[i, j, k] - uc[i, j, k] + ud[i, j, k] >= 0)
            else:
                for k in range(1, len(E_Bus) + 1):
                    globals()['csrt3_' + str(i) + '_' + str(j) + '_' + str(k)] = \
                        SP_Dual.addConstr(-ua[i, j, k] + ub[i, j, k] - uc[i, j, k] + ud[i, j, k] - uk[j] >= 0)

    for i in range(len(Trip)):
        for j in range(len(Trip)):
            if j == 0:
                for k in range(1, len(E_Bus)+1):
                    globals()['csrt4_' + str(i) + '_' + str(j) + '_' + str(k)] = \
                        SP_Dual.addConstr(-ue[i, j, k] + uf[i, j, k] - ug[i, j, k] + uh[i, j, k] >= 0)
            elif j == len(Trip) - 1:
                for k in range(1, len(E_Bus)+1):
                    globals()['csrt4_' + str(i) + '_' + str(j) + '_' + str(k)] = \
                        SP_Dual.addConstr(-ue[i, j, k] + uf[i, j, k] - ug[i, j, k] + uh[i, j, k] >= 0)
            else:
                for k in range(1, len(E_Bus) + 1):
                    globals()['csrt4_' + str(i) + '_' + str(j) + '_' + str(k)] = \
                        SP_Dual.addConstr(-ue[i, j, k] + uf[i, j, k] - ug[i, j, k] + uh[i, j, k] - uk[j] >= 0)

    for i in range(len(Trip)):
        if i == 0:
            globals()['csrt5_' + str(i)] = SP_Dual.addConstr(gp.quicksum(uc[i, j, k] - ud[i, j, k]
                for j in range(len(Trip)) for k in range(1, len(E_Bus) + 1)) + uk[i]  >= 0)
        elif i == len(Trip) - 1:
            globals()['csrt5_' + str(i)] = SP_Dual.addConstr(gp.quicksum(uc[i, j, k] - ud[i, j, k]
                for j in range(len(Trip)) for k in range(1, len(E_Bus) + 1))  >= 0)
        else:
            globals()['csrt5_' + str(i)] = SP_Dual.addConstr(gp.quicksum(uc[i ,j, k] - ud[i, j, k]
                for j in range(len(Trip)) for k in range(1, len(E_Bus)+1)) - ui[i] + uj[i] + uk[i] >= 0)


    SP_Dual.Params.InfUnbdInfo = 1

    iteration = 0
    SP_Dual_obj = [9999]
    x_for_cut = []
    MP.optimize()
    print('MP RESULT:')

    # 测试电动公交车的路线输出

    x_array = eop.transform_decision_variable_to_array(x,len(Trip),len(E_Bus))
    print('-----------------------------------')
    eop.print_E_Bus_Path(len(E_Bus),x_array)
    print('-----------------------------------')

    while z.x < SP_Dual_obj[0]:
        print('z value =', z.x)
        print('iteration = ', iteration)
        print('SP_Dual_obj[0] = ', SP_Dual_obj[0])
        print('-----------------------------------')

        if iteration == 0:
            SP_Dual.setObjective(gp.quicksum((M1 * (-ua[i, j, k] - ub[i, j, k] + uc[i, j, k] + ud[i, j, k]) +
                                              M2 * (-ue[i, j, k] - uf[i, j, k] + ug[i, j, k] + uh[i, j, k])) * x[i,j,k].x \
                                             for i in range(len(Trip)) for j in range(len(Trip)) for k in
                                             range(1, len(E_Bus) + 1)) + \
                                 gp.quicksum((M1 * (-uc[i, j, k] - ud[i, j, k]) + M2 * (-ug[i, j, k] - uh[i, j, k])) \
                                             for i in range(len(Trip)) for j in range(len(Trip)) for k in
                                             range(1, len(E_Bus) + 1)) + \
                                 gp.quicksum(uj) * (- Sbar + delta) - uk[0] * Sbar + \
                                 gp.quicksum(uk[i] for i in range(1,len(Trip)-1)) * delta - \
                                 miu * gp.quicksum(um), sense=GRB.MAXIMIZE)
            SP_Dual.optimize()

            #if SP_Dual.status == GRB.OPTIMAL:
            #    UB = min(UB, SP_Dual_obj[0])


            addBendersCuts(SP_Dual_obj,x_for_cut)

            iteration = 1
        else:
            SP_Dual.setObjective(gp.quicksum((M1 * (-ua[i, j, k] - ub[i, j, k] + uc[i, j, k] + ud[i, j, k]) +
                                              M2 * (-ue[i, j, k] - uf[i, j, k] + ug[i, j, k] + uh[i, j, k])) * x[i, j, k].x \
                                             for i in range(len(Trip)) for j in range(len(Trip)) for k in
                                             range(1, len(E_Bus) + 1)) + \
                                 gp.quicksum((M1 * (-uc[i, j, k] - ud[i, j, k]) + M2 * (-ug[i, j, k] - uh[i, j, k])) \
                                             for i in range(len(Trip)) for j in range(len(Trip)) for k in
                                             range(1, len(E_Bus) + 1)) + \
                                 gp.quicksum(uj) * (- Sbar + delta) - uk[0] * Sbar + \
                                 gp.quicksum(uk[i] for i in range(1, len(Trip) - 1)) * delta - \
                                 miu * gp.quicksum(um), sense=GRB.MAXIMIZE)

            SP_Dual.optimize()
            addBendersCuts(SP_Dual_obj,x_for_cut)
            iteration = iteration + 1

        # 测试
        if SP_Dual_obj[0] == 300:
            break

        MP.optimize()
        MP.write("model_MP.lp")

        # 打印 E_Bus Trip 路径
        x_array = eop.transform_decision_variable_to_array(x, len(Trip), len(E_Bus))
        print('-----------------------------------')
        eop.print_E_Bus_Path(len(E_Bus), x_array)
        print('-----------------------------------')


        str_iteration = "Iteration: %s \n" % iteration
        with open(filename, 'a') as f:
            f.write("***************************************************************************\n")
            f.write(str_iteration)
            for i in range(len(Trip)):
                f.write("S_%s = %s  " % (i, globals()['csrt5_' + str(i)].pi))
            f.write("\nz.x = %s  SP_Dual_obj[0] = %s\n" % (z.x, SP_Dual_obj[0]))
            if SP_Dual.Status == GRB.UNBOUNDED:
                f.write("SP_Dual: UNBOUNDED")
            elif SP_Dual.Status == GRB.OPTIMAL:
                f.write("SP_Dual: OPTIMAL")
            else:
                f.write("SP_Dual: Others")
            f.write("\n***************************************************************************\n\n\n")

        print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx %s  %s\n" % (iteration, SP_Dual_obj[0]))

except gp.GurobiError as e:
    print('Error code ' + str(e.errno) + ": " + str(e))

except AttributeError:
    print('Encountered an attribute error')












