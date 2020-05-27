import gurobipy as gp
from gurobipy import GRB
import numpy as np
from itertools import accumulate

#m = gp.Model("test1")
#x = m.addVars(2,3,4,lb=0,vtype=GRB.CONTINUOUS,name = "x")
#y = m.addVars(2,3,4,lb=0,vtype=GRB.CONTINUOUS,name="y")

#m.update()
#m.setObjective(gp.quicksum(x),sense=GRB.MAXIMIZE)


#for i in range(2):
#    for j in range(3):
#        for k in range(4):
#            locals()['v_'+str(i)+'_'+str(j)+'_'+str(k)]= m.addConstr(x[i,j,k]<=1)
#            m.addConstr(y[i,j,k]<=2)
#m.optimize()

#print("obj:", m.objVal)




# 暂存
# 结果输出的部分，要不单独放一个文件也行。
# print the Trip path of each E_Bus   (PASSED)
# NOTED: If the optimization result is wrong, like one E_Bus has more than one path, the output path is incredible
# Example: for E_Bus 1, one path is (0,4), another path is (1,2,3,1), the wrong result is limitted by constraints.
#x_array = np.zeros((len(Trip),len(Trip),len(E_Bus)+1))
#for i in range(len(Trip)):
#    for j in range(len(Trip)):
#        for k in range(1,len(E_Bus)+1):
#            x_array[i,j,k] = x[i,j,k].x
#path = []
#for k in range(1,len(E_Bus)+1):
#    k_nonzero = np.nonzero(x_array[:,:,k])
#    path_k = []
#    for i in range(len(k_nonzero)):
#        path_k = np.union1d(path_k,k_nonzero[i])
#    path = ((path,) + (path_k,))
#    print("Path_E_Bus(",k ,"):", path_k)


MP.addConstr(gp.quicksum((M1 * (- ray_split[0][i * len(Trip) * len(E_Bus) + j * len(E_Bus) + k - 1] -
                   ray_split[1][i * len(Trip) * len(E_Bus) + j * len(E_Bus) + k - 1] +
                   ray_split[2][i * len(Trip) * len(E_Bus) + j * len(E_Bus) + k - 1] +
                   ray_split[3][i * len(Trip) * len(E_Bus) + j * len(E_Bus) + k - 1]) +
            M2 * (- ray_split[4][i * len(Trip) * len(E_Bus) + j * len(E_Bus) + k - 1] -
                   ray_split[5][i * len(Trip) * len(E_Bus) + j * len(E_Bus) + k - 1] +
                   ray_split[6][i * len(Trip) * len(E_Bus) + j * len(E_Bus) + k - 1] +
                   ray_split[7][i * len(Trip) * len(E_Bus) + j * len(E_Bus) + k - 1])) * x[i,j,k] \
            for i in range(len(Trip)) for j in range(len(Trip)) for k in range(1, len(E_Bus) + 1)) + \
        gp.quicksum((M1 * (- ray_split[2][i * len(Trip) * len(E_Bus) + j * len(E_Bus) + k - 1] -
                   ray_split[3][i * len(Trip) * len(E_Bus) + j * len(E_Bus) + k - 1]) +
             M2 * (-ray_split[6][i * len(Trip) * len(E_Bus) + j * len(E_Bus) + k - 1] -
                   ray_split[7][i * len(Trip) * len(E_Bus) + j * len(E_Bus) + k - 1])) \
            for i in range(len(Trip)) for j in range(len(Trip)) for k in range(1, len(E_Bus) + 1)) + \
        gp.quicksum((delta * ray_split[8][j * len(E_Bus) + k - 1] +
             Sbar * ray_split[9][j * len(E_Bus) + k - 1]) \
            for j in range(len(Trip)) for k in range(1, len(E_Bus) + 1)) - \
        miu * gp.quicksum(ray_split[11])  <= 0)















