import gurobipy as gp
from gurobipy import GRB

MP = gp.Model()
x = MP.addVars(2,vtype=GRB.CONTINUOUS,name="x")
for i in range(2):
    locals()['csrt_' + str(i) + '_' + str(i)] = MP.addConstr(x[i] <= 1)
MP.setObjective(gp.quicksum(x), GRB.MAXIMIZE)
MP.optimize()
for i in range(2):
    print(locals()['csrt_' + str(i) + '_' + str(i)].pi)
    # print('csrt.pi = ', csrt_0_0.pi)





