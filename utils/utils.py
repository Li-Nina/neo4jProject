#!/usr/bin/env python
# -*- coding:utf-8 -*-
import math
import numpy as np


def check_nan(num):
    return 0 if math.isnan(num) else num


def check_nan_or_zero(num):
    return math.isnan(num) or num == 0


if __name__ == '__main__':
    # a = [1, 2, 3]
    # c = a.copy()
    # c.append(6)
    # print(a)
    # print(c)
    # a = (1,2)
    # x = copy.deepcopy(a)
    # print(a)
    # print(x)
    # print(a == x)

    # lists = [{'x1': 1}, {'x2': 2}, {'x3': 3}]
    # mm = lists.copy()
    # mm.append({'x5': 5})
    # mm[0]['x1']=100
    # print(lists)
    # print(mm)

    a = {'x1': 0.01, 'x2': 0.11, 'x3': 11.5, 'x4': 0.06, 'x5': 0.01, 'x6': 0.01, 'x7': 9, 'x8': 40, 'x9': 0.65,
         'down': 0, 'up': 4}
    b = {'x1': 0.02, 'x2': 0.08, 'x3': 3, 'x4': 0.9, 'x5': 0, 'x6': 0.01, 'x7': 2.95, 'x8': 8, 'x9': 0.297142857142857,
         'down': 0, 'up': 1}
    c = {i: 0 if check_nan_or_zero(a[i]) or check_nan_or_zero(b[i]) else a[i] / b[i] for i in
         ['x1', 'x2', 'x3', 'x4', 'x5', 'x6', 'x7', 'x8', 'x9']}

    print(c)
