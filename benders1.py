#!/usr/bin/env python3.7

# Copyright 2020, Haoyu Miao

# This example formulates and solves the following simple MILP model:
#  minimize
#        sum(x) + 7 * sum(y)
#  subject to
#        x(1)               + x(4) + x(5) = 8
#               x(2)               + x(5) = 3
#                      x(3) + x(4)        = 5
#        x <= diag([8,3,5,5,3]) * y
#        x >= 0, y binary
#        x \in R_{+}^{5*1}, y \in R^{5*1}

import gurobipy as gp
from gurobipy import GRB

def addBendersCuts(SP_Dual_obj,x):
    if SP_Dual.status == GRB.Status.UNBOUNDED:
        ray = SP_Dual.UnbdRay
        print(ray)
        MP.addConstr(8*ray[0]+3*ray[1]+5*ray[2]+\
                     8*ray[3]*y[0]+3*ray[4]*y[1]+5*ray[5]*y[2]+5*ray[6]*y[3]+3*ray[7]*y[4]<=0)
    elif SP_Dual.status == GRB.Status.OPTIMAL:
        MP.addConstr(8*Vdual1[0].x+3*Vdual1[1].x+5*Vdual1[2].x+\
                     8*Vdual2[0].x*y[0]+3*Vdual2[1].x*y[1]+\
                     5*Vdual2[2].x*y[2]+5*Vdual2[3].x*y[3]+3*Vdual2[4].x*y[4]<=z)
        SP_Dual_obj[0] = SP_Dual.ObjVal
        x.append(x1.pi)
        x.append(x2.pi)
        x.append(x3.pi)
        x.append(x4.pi)
        x.append(x5.pi)
        for i in range(1,6):
            print(globals()['x'+str(i)].pi)
    else:
        print(SP_Dual.status)

try:
    MP = gp.Model() # Benders Master Problem
    y = MP.addVars(5,vtype=GRB.BINARY,name="y")   # discrete variable
    z = MP.addVar(vtype=GRB.CONTINUOUS,name="z")  # objective value of SubProblem
    MP.update()
    MP.setObjective(7*gp.quicksum(y)+z,sense=GRB.MINIMIZE)
    #MP.setObjective(z, sense=GRB.MINIMIZE)

    SP_Dual = gp.Model() # dual of Benders SubProblem
    Vdual1 = SP_Dual.addVars(3,lb=-GRB.INFINITY,vtype=GRB.CONTINUOUS,name="Vdual1")       # dual variables of equalitity constraint
    Vdual2 = SP_Dual.addVars(5,lb=-GRB.INFINITY,ub=0,vtype=GRB.CONTINUOUS,name="Vdual2")  # dual variables of inequalitity constraints
    SP_Dual.update()
    # SP_Dual 的约束理论上应该是 == 1，但是 <= 1 也可以进行求解
    x1 = SP_Dual.addConstr(Vdual1[0]+Vdual2[0]<=1)
    x2 = SP_Dual.addConstr(Vdual1[1]+Vdual2[1]<=1)
    x3 = SP_Dual.addConstr(Vdual1[2]+Vdual2[2]<=1)
    x4 = SP_Dual.addConstr(Vdual1[0]+Vdual1[2]+Vdual2[3]<=1)
    x5 = SP_Dual.addConstr(Vdual1[0]+Vdual1[1]+Vdual2[4]<=1)

    SP_Dual.Params.InfUnbdInfo = 1 # 这个的作用是什么？

    iteration = 0
    SP_Dual_obj = [9999] # 定义了一个 list，并进行初始化
    x = []  # 这个 x 是什么？
    MP.optimize()

    while z.x < SP_Dual_obj[0]:
        if iteration == 0:
            SP_Dual.setObjective(8*Vdual1[0] + 3*Vdual1[1] + 5*Vdual1[2] +\
                                 8*Vdual2[0]*y[0].x + 3*Vdual2[1]*y[1].x + 5*Vdual2[2]*y[2].x +\
                                 5*Vdual2[3]*y[3].x + 3*Vdual2[4]*y[4].x,GRB.MAXIMIZE)
            SP_Dual.optimize()
            addBendersCuts(SP_Dual_obj,x)
            iteration = 1
        else:
            # Vdual2 是拉格朗日乘子，y是离散变量
            Vdual2[0].obj = 8 * y[0].x
            Vdual2[1].obj = 3 * y[1].x
            Vdual2[2].obj = 5 * y[2].x
            Vdual2[3].obj = 5 * y[3].x
            Vdual2[4].obj = 3 * y[4].x
            SP_Dual.setObjective(8 * Vdual1[0] + 3 * Vdual1[1] + 5 * Vdual1[2] + \
                                 8 * Vdual2[0] * y[0].x + 3 * Vdual2[1] * y[1].x + 5 * Vdual2[2] * y[2].x + \
                                 5 * Vdual2[3] * y[3].x + 3 * Vdual2[4] * y[4].x, GRB.MAXIMIZE)
            SP_Dual.optimize()
            addBendersCuts(SP_Dual_obj,x)
            iteration = iteration + 1
        MP.optimize()

except gp.GurobiError as e:
    print('Error code ' + str(e.errno) + ": " + str(e))

except AttributeError:
    print('Encountered an attribute error')



