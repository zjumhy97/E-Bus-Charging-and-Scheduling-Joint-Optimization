import gurobipy as gp
from gurobipy import GRB
import E_Bus_Output as eop

MP = gp.Model()
SP_Dual = gp.Model()

# 现在的问题是，我的对偶变量数目太多，而且只集中在 ray 的话，
def addBendersCuts_example(SP_Dual_obj,x_for_cut):
    if SP_Dual.status == GRB.Status.UNBOUNDED:
        ray = SP_Dual.UnbdRay
        MP.addConstr(8*ray[0]+3*ray[1]+5*ray[2]+\
                     8*ray[3]*y[0]+3*ray[4]*y[1]+5*ray[5]*y[2]+5*ray[6]*y[3]+3*ray[7]*y[4]<=0)
    elif SP_Dual.status == GRB.Status.OPTIMAL:
        MP.addConstr(8*Vdual1[0].x+3*Vdual1[1].x+5*Vdual1[2].x+\
                     8*Vdual2[0].x*y[0]+3*Vdual2[1].x*y[1]+\
                     5*Vdual2[2].x*y[2]+5*Vdual2[3].x*y[3]+3*Vdual2[4].x*y[4]<=z)
        SP_Dual_obj[0] = SP_Dual.ObjVal
        x_for_cut.append(x1.pi)
        x_for_cut.append(x2.pi)
        x_for_cut.append(x3.pi)
        x_for_cut.append(x4.pi)
        x_for_cut.append(x5.pi)
    else:
        print(SP_Dual.status)


            SP_Dual.setObjective(gp.quicksum((M1 * (-ua[i, j, k] - ub[i, j, k] + uc[i, j, k] + ud[i, j, k]) +
                                              M2 * (-ue[i, j, k] - uf[i, j, k] + ug[i, j, k] + uh[i, j, k])) * x[i,j,k].x \
                                             for i in range(len(Trip)) for j in range(len(Trip)) for k in
                                             range(1, len(E_Bus) + 1)) + \
                                 gp.quicksum((M1 * (-uc[i, j, k] - ud[i, j, k]) + M2 * (-ug[i, j, k] - uh[i, j, k])) \
                                             for i in range(len(Trip)) for j in range(len(Trip)) for k in
                                             range(1, len(E_Bus) + 1)) + \


                                 gp.quicksum(uj) * (- Sbar + delta) - \
                                 uk[0] * Sbar + \
                                 gp.quicksum(uk[i] for i in range(1,len(Trip)-1)) * delta - \
                                 miu * gp.quicksum(um), sense=GRB.MAXIMIZE)


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


                             sum(ray_split[9][i] for i in range(1, len(Trip) - 1)) * (- Sbar + delta) - \
                             ray_split[10][0] * Sbar + \
                             sum(ray_split[10][i] for i in range(1,len(Trip)-1)) * delta -\
                             miu * sum(ray_split[12][i, j, l] for i in range(len(Trip)) for j in range(len(Trip))
                                       for l in range(1, len(L_test) + 1)) <= 0 )



















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