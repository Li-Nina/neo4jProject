#!/usr/bin/env python
# -*- coding:utf-8 -*-
import math


def check_nan(num):
    return 0 if math.isnan(num) else num


def check_nan_or_zero(num):
    return math.isnan(num) or num == 0


'''
    计算一个数的量级，eg：150 --> 100, 0.0551 --> 0.01
'''


def number_scalar(num):
    num = abs(num)
    if num >= 1:
        digits = 10 ** int(math.log10(num))
    else:
        digits = _float_scalar(num)
    return digits


'''
    计算小数的量级，eg：0.0551 --> 0.01
'''


def _float_scalar(num):
    num = abs(num)
    n = 0
    while 1 > num > 0:
        num *= 10
        n += 1
    formats = '%0.' + str(n) + 'f'
    return float(formats % (0.1 ** n))
