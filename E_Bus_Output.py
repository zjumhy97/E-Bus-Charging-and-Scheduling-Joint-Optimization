#!/usr/bin/env python3.7

# Copyright 2020, Haoyu Miao

# The E_Bus_Output function file

import numpy as np
from itertools import accumulate

def print_E_Bus_Path(len_E_Bus,x_array):
    """
    :param len_E_Bus: length of E_Bus fleet, e.g. len(E_Bus)
    :param x_array: the output of the (transform_decision_variable_to_array)
    :return:
    Print the Trip path of each E_Bus
    NOTED: If the optimization result is wrong, like one E_Bus has more than one path, the output path is incredible
    Example: for E_Bus 1, one path is (0,4), another path is (1,2,3,1), the wrong result is limited by constraints.
    """
    path = []
    for k in range(1,len_E_Bus+1):
        k_nonzero = np.nonzero(x_array[:,:,k])
        path_k = []
        for i in range(len(k_nonzero)):
            path_k = np.union1d(path_k,k_nonzero[i])
        path = ((path,) + (path_k,))
        print("Path_E_Bus(",k ,"):", path_k)


def transform_decision_variable_to_array(x,len_Trip,len_E_Bus):
    """
    :param x: the decision variable of gurobipy
    :param len_Trip: the length of Trip, e.g. len(Trip)
    :param len_E_Bus: the length of E_Bus, e.g. len(E_Bus)
    :return: x_array: 3 dimension array, value is {0,1}
    """
    x_array = np.zeros((len_Trip,len_Trip,len_E_Bus+1))
    for i in range(len_Trip):
        for j in range(len_Trip):
            for k in range(1,len_E_Bus+1):
                x_array[i,j,k] = x[i,j,k].x
    return x_array


def list_split_to_given_length(list,given_length):
    list_new = [list[x - y: x] for x,y in zip(accumulate(given_length),given_length)]
    return list_new