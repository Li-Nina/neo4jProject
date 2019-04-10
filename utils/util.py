#!/usr/bin/env python
# -*- coding:utf-8 -*-
import json
import math
import time

from utils.config import ALLOWED_EXTENSIONS


def check_nan(num):
    return 0 if math.isnan(num) else num


def check_nan_or_zero(num):
    return math.isnan(num) or num == 0


def number_scalar_modified(num):
    """
    计算一个数的量级，正数始终返回1，eg：150 --> 1, 0.0551 --> 0.01
    :param num:
    :return:
    """
    num = abs(num)
    if num >= 1:
        digits = 1
    else:
        digits = _float_scalar(num)
    return digits


def number_scalar(num):
    """
    计算一个数的量级，eg：150 --> 100, 0.0551 --> 0.01
    :param num:
    :return:
    """
    num = abs(num)
    if num >= 1:
        digits = 10 ** int(math.log10(num))
    else:
        digits = _float_scalar(num)
    return digits


def _float_scalar(num):
    """
    计算小数的量级，eg：0.0551 --> 0.01
    :param num:
    :return:
    """
    num = abs(num)
    n = 0
    while 1 > num > 0:
        num *= 10
        n += 1
    formats = '%0.' + str(n) + 'f'
    return float(formats % (0.1 ** n))


def adjust_digit(num, digit):
    # num始终为最小化的值，此函数目的为截取精度并向上取值。num为正配料求最小化，num为负配料求最大化。
    _place = 10 ** digit
    _up = 0.1 ** digit
    truncate = int(num * _place) / _place
    truncate += _up
    return truncate


# noinspection PyProtectedMember
def convert_namedtuple(nt, types='dict'):
    """
    将namedtuple转换为dict或json string
    @see https://stackoverflow.com/questions/26180528/python-named-tuple-to-dictionary
    @see https://gist.github.com/Integralist/b25185f91ebc8a56fe070d499111b447
    :param nt: namedtuple
    :param types: 转换类型，'dict','json','str'
    :return:
    """
    order_dic = nt._asdict()
    if types == 'dict':
        return dict(order_dic)
    elif types == 'json' or types == 'str':
        return json.dumps(order_dic, ensure_ascii=False)
    else:
        return order_dic


def current_time_millis():
    return int(round(time.time() * 1000))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
