## PART I. Parameters

## Time Slot L
# test: form 6:00 - 8:00, 12 time slots
L_test = list(range(1,13))

## Time Table & Trip
# Trip_start and Trip_end are virtual vertex in the graph
Trip,Trip_time,Duration_time = gp.multidict({
    "Trip_start" : [0,0],
    "Trip_1" : [1,6],"Trip_2" : [2,6],"Trip_3" : [3,6],"Trip_4" : [4,6],"Trip_5" : [5,6],"Trip_6" : [6,6],
    "Trip_7" : [7,6],"Trip_8" : [8,6],"Trip_9" : [9,6],"Trip_10" : [10,6],"Trip_11" : [11,6],"Trip_12" : [12,6],
    "Trip_end" : [100,0],
})
# Constant b for the constraint
b = [0 for _ in range(len(Trip))]
b[0] = 1
b[-1] = -1

## Bus Fleet K
E_Bus, SOC_MIN, SOC_MAX, Battery_Capacity, Energy_per_Trip_Win, Energy_per_Trip_Sum = gp.multidict({
    "JL_1" : [30,100,160,47,65.8],
    "JL_2" : [30,100,160,47,65.8],
    "JL_3" : [30,100,160,47,65.8],
    "JL_4" : [30,100,160,47,65.8],
    "JL_5" : [30,100,160,47,65.8],
    "JL_6" : [30,100,160,47,65.8],
    "JL_7" : [30,100,160,47,65.8],
    "JL_8" : [30,100,160,47,65.8],
    "JL_9" : [30,100,160,47,65.8],
    "JL_10" : [30,100,160,47,65.8],
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
