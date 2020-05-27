import numpy as np
import gurobipy as gp
from gurobipy import GRB
import E_Bus_Output as eop

# test3.py is test for the Benders SubProblem

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

# 有一些新添加的变量
c = np.zeros(len(L_test)+1)
for i in range(len(L_test)+1):
    c[i] = 0.637 # 电价

d = 10 # 峰值功率对应的电价

# K 和 I 两个还需要定义
I = np.zeros((len(Trip),len(Trip),len(L_test)+1))
for i in range(len(Trip)):
    for j in range(len(Trip)):
        for l in range(1,len(L_test)+1):
            if l >= Trip_time.values()[i] + Duration_time.values()[i] and l <= Trip_time.values()[j] - 1 :
                I[i,j,l] = 1

K = np.zeros((len(Trip),len(Trip)))
for i in range(len(Trip)):
    for j in range(len(Trip)):
        if Trip_time.values()[i] + Duration_time.values()[i] <= Trip_time.values()[j]:
            K[i,j] = 1

miu = 1000
M1 = 10000
M2 = 10000
delta = 47
Sbar = 160


# 定义 x_array 以供测试
x_array = np.zeros((5,5,4))
x_array[0,2,1] = 1
x_array[2,4,1] = 1
x_array[0,4,2] = 1
x_array[0,1,3] = 1
x_array[1,3,3] = 1
x_array[3,4,3] = 1




SP_Dual = gp.Model()
ua = SP_Dual.addVars(range(len(Trip)),range(len(Trip)),range(1,len(E_Bus)+1),lb=0,vtype=GRB.CONTINUOUS,name="ua")
ub = SP_Dual.addVars(range(len(Trip)),range(len(Trip)),range(1,len(E_Bus)+1),lb=0,vtype=GRB.CONTINUOUS,name="ub")
uc = SP_Dual.addVars(range(len(Trip)),range(len(Trip)),range(1,len(E_Bus)+1),lb=0,vtype=GRB.CONTINUOUS,name="uc")
ud = SP_Dual.addVars(range(len(Trip)),range(len(Trip)),range(1,len(E_Bus)+1),lb=0,vtype=GRB.CONTINUOUS,name="ud")
ue = SP_Dual.addVars(range(len(Trip)),range(len(Trip)),range(1,len(E_Bus)+1),lb=0,vtype=GRB.CONTINUOUS,name="ue")
uf = SP_Dual.addVars(range(len(Trip)),range(len(Trip)),range(1,len(E_Bus)+1),lb=0,vtype=GRB.CONTINUOUS,name="uf")
ug = SP_Dual.addVars(range(len(Trip)),range(len(Trip)),range(1,len(E_Bus)+1),lb=0,vtype=GRB.CONTINUOUS,name="ug")
uh = SP_Dual.addVars(range(len(Trip)),range(len(Trip)),range(1,len(E_Bus)+1),lb=0,vtype=GRB.CONTINUOUS,name="uh")
ui = SP_Dual.addVars(range(len(Trip)),range(1,len(E_Bus)+1),lb=0,vtype=GRB.CONTINUOUS,name="ui")
uj = SP_Dual.addVars(range(len(Trip)),range(1,len(E_Bus)+1),lb=0,vtype=GRB.CONTINUOUS,name="uj")
uk = SP_Dual.addVars(range(len(Trip)),range(len(Trip)),range(1,len(L_test)+1),lb=0,vtype=GRB.CONTINUOUS,name="uk") # 不确定
ul = SP_Dual.addVars(range(len(Trip)),range(len(Trip)),range(1,len(L_test)+1),lb=0,vtype=GRB.CONTINUOUS,name="ul") # 不确定
um = SP_Dual.addVars(range(1,len(L_test)+1),lb=0,vtype=GRB.CONTINUOUS,name="um") # um represent the \lambda in the paper

SP_Dual.update()


for i in range(len(Trip)):
    for j in range(len(Trip)):
        for l in range(1,len(L_test)):
            locals()['csrt1_'+str(i)+'_'+str(j)+'_'+str(l)]= \
                SP_Dual.addConstr(c[l]*I[i,j,l] - uk[i,j,l] + ul[i,j,l] + gp.quicksum((ug[i,j,k] - uh[i,j,k]) \
                            for k in range(1,len(E_Bus)+1)) * I[i,j,l] + um[l]*I[i,j,l] >= 0)

csrt2 = SP_Dual.addConstr(d - gp.quicksum(um) >= 0)

for i in range(len(Trip)):
    for j in range(len(Trip)):
        for k in range(1,len(E_Bus)+1):
            locals()['csrt3_'+str(i)+'_'+str(j)+'_'+str(k)]=\
                SP_Dual.addConstr(-ua[i,j,k]+ub[i,j,k]-uc[i,j,k]+ud[i,j,k]+K[i,j]*(-ui[j,k]+uj[j,k]) >= 0)
            locals()['csrt4_'+str(i)+'_'+str(j)+'_'+str(k)]=\
                SP_Dual.addConstr(-ue[i,j,k]+uf[i,j,k]-ug[i,j,k]+uh[i,j,k]+K[i,j]*(-ui[j,k]+uj[j,k]) >= 0)
            locals()['csrt5_'+str(i)+'_'+str(j)+'_'+str(k)]=\
                SP_Dual.addConstr(uc[i,j,k]-ud[i,j,k] >= 0)



#SP_Dual.setObjective(gp.quicksum((M1*(-ua[i,j,k]-ub[i,j,k]+uc[i,j,k]+ud[i,j,k])+ \
 #                                M2*(-ue[i,j,k]-uf[i,j,k]+ug[i,j,k]+uh[i,j,k]))*x[i,j,k].x \
  #                               for i in range(len(Trip)) for j in range(len(Trip)) for k in range(1,len(E_Bus)+1)) + \
   #                  gp.quicksum((M1*(-uc[i,j,k]-ud[i,j,k])+M2*(-ug[i,j,k]-uh[i,j,k])) \
    #                             for i in range(len(Trip)) for j in range(len(Trip)) for k in range(1,len(E_Bus)+1)) + \
     #                gp.quicksum((delta*ui[j,k]+Sbar*uj[j,k]) for j in range(len(Trip)) for k in range(1,len(E_Bus)+1))-\
      #               miu * gp.quicksum(ul),sense=GRB.MAXIMIZE)

SP_Dual.setObjective(gp.quicksum((M1*(-ua[i,j,k]-ub[i,j,k]+uc[i,j,k]+ud[i,j,k])+ \
                                 M2*(-ue[i,j,k]-uf[i,j,k]+ug[i,j,k]+uh[i,j,k]))*x_array[i,j,k-1] \
                                 for i in range(len(Trip)) for j in range(len(Trip)) for k in range(1,len(E_Bus)+1)) + \
                     gp.quicksum((M1*(-uc[i,j,k]-ud[i,j,k])+M2*(-ug[i,j,k]-uh[i,j,k])) \
                                 for i in range(len(Trip)) for j in range(len(Trip)) for k in range(1,len(E_Bus)+1)) + \
                     gp.quicksum((delta*ui[j,k]+Sbar*uj[j,k]) for j in range(len(Trip)) for k in range(1,len(E_Bus)+1))-\
                     miu * gp.quicksum(ul),sense=GRB.MAXIMIZE)

SP_Dual.optimize()



