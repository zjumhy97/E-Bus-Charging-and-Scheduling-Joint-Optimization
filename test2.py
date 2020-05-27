import numpy as np
import scipy.sparse as sp
import gurobipy as gp
from gurobipy import GRB
import E_Bus_Output as eop

L_test = list(range(1,13))
Trip,Trip_time,Duration_time = gp.multidict({
    "Trip_start" : [0,0],
    "Trip_1" : [1,2],"Trip_2" : [2,2],"Trip_3" : [3,2],#"Trip_4" : [4],"Trip_5" : [5],"Trip_6" : [6],
    #"Trip_7" : [7],"Trip_8" : [8],"Trip_9" : [9],"Trip_10" : [10],"Trip_11" : [11],"Trip_12" : [12],
    "Trip_end" : [100,100]
})
b = [0 for _ in range(len(Trip))]
b[0] = 1
b[-1] = -1

E_Bus, SOC_MIN, SOC_MAX, Battery_Capacity, Energy_per_Trip_Win, Energy_per_Trip_Sum = gp.multidict({
    "JL_1" : [30,100,160,47,65.8],
    "JL_2" : [30,100,160,47,65.8],
    "JL_3" : [30,100,160,47,65.8],
    #"JL_4" : [30,100,160,47,65.8],
    #"JL_5" : [30,100,160,47,65.8],
    #"JL_6" : [30,100,160,47,65.8],
    #"JL_7" : [30,100,160,47,65.8],
    #"JL_8" : [30,100,160,47,65.8],
    #"JL_9" : [30,100,160,47,65.8],
    #"JL_10" : [30,100,160,47,65.8],
})

# Master Problem
MP = gp.Model()
# Create Variables
x = MP.addVars(range(len(Trip)),range(len(Trip)),range(1,len(E_Bus)+1),vtype=GRB.BINARY,name="x")
MP.update()

for i in range(len(Trip)):
    for k in range(1,len(E_Bus)+1):
        MP.addConstr(gp.quicksum(x[i, j, k] for j in range(len(Trip))) - gp.quicksum(x[j, i, k] for j in range(len(Trip))) == b[i])


for i in range(1,len(Trip)-1):
    MP.addConstr(gp.quicksum(x[i,j,k] for j in range(len(Trip)) if i < j for k in range(1, len(E_Bus)+1)) == 1)

for i in range(len(Trip)):
    for j in range(len(Trip)):
        if i>=j:
            MP.addConstr(gp.quicksum(x[i,j,k] for k in range(1,len(E_Bus)+1)) == 0)

for i in range(len(Trip)-1):
    for j in range(1,len(Trip)):
        for k in range(1,len(E_Bus)+1):
            MP.addConstr((Trip_time.values()[i] + Duration_time.values()[i]) * x[i,j,k] <= Trip_time.values()[j])


MP.setObjective(gp.quicksum(x)- gp.quicksum(x[0,len(Trip)-1,k] for k in range(1,len(E_Bus)+1)) ,sense=GRB.MINIMIZE)

MP.optimize()
print("objval = ",MP.objVal)
x_array = eop.transform_decision_variable_to_array(x,len(Trip),len(E_Bus))
eop.print_E_Bus_Path(len(E_Bus),x_array)




