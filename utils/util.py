#!/usr/bin/env python
# -*- coding:utf-8 -*-
import json
import math
import time

from utils.config import ALLOWED_EXTENSIONS, DELTA


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


def adjust_digit(num, digit):
    """
    优化结果按精度近似
    修改digit位实现增大num，并保证四舍五入不影响digit的上一位
    num始终为最小化的值，此函数目的为截取精度并向上取值。num为正配料求最小化，num为负配料求最大化。
    :param num: num
    :param digit: DIGIT + 1; 精确到DIGIT位，因此操作DIGIT的后一位
    :return: 近似放大后的优化结果值
    """
    if num == 0:
        return num
    _place = 10 ** digit
    _up = 0.1 ** digit
    val = int(num * _place)
    ones = abs(val) % 10

    if num > 0 and ones == 4:
        # num>0,即求abs(num)的最小值。此时num已经是最小值，返回值应放大num
        # 如果末尾为4，直接+1为5后存在四舍五入问题。
        for i in range(5):
            _place *= 10
            _up *= 0.1
            val = int(num * _place)
            ones = abs(val) % 10
            if ones != 9:
                break
    elif num < 0 and ones == 5:
        # num<0,即求abs(num)的最大值。此时abs(num)已经是最大值，返回值应放小abs(num),即放大num
        # 如果末尾为5，直接-1为4后存在四舍五入问题。
        for i in range(5):
            _place *= 10
            _up *= 0.1
            val = int(num * _place)
            ones = abs(val) % 10
            if ones != 0:
                if ones == 1:
                    _up *= 0.1
                break
    truncate = val / _place
    truncate += _up
    return truncate


def adjust_digit_size(num, digit, size_type):
    """
    约束条件上下限按精度近似
    :param num: 完全精度的上下限要求
    :param digit: 近似的位数
    :param size_type: 上限或下限,'up' or 'down'
    :return: 近似放大后的精度值
    """
    if num <= 0:
        return num

    _place_former = 10 ** (digit - 1)
    _place = _place_former * 10
    _up = 0.1 ** digit
    ones_former = abs(int(num * _place_former)) % 10  # 前一位小数，当为4时且后面全为9时坚决不能动，防止进位
    ones = abs(int(num * _place)) % 10

    if size_type == 'up':
        if ones == 9:
            for i in range(5):
                _place *= 10
                ones = abs(int(num * _place)) % 10
                _place_former *= 10
                _up *= 0.1
                if ones != 9:
                    return int(num * _place_former) / _place_former + 9 * _up
            if ones_former == 4:
                # 前一位小数为4且后5位都为9，直接返回原值
                return num
            else:
                # 前一位小数不为4且后5位都为9，第6位+1
                _place *= 10
                _up *= 0.1
                return int(num * _place) / _place + _up
        else:
            return int(num * _place_former) / _place_former + 9 * _up
    elif size_type == 'down':
        if ones_former == 5 and ones == 0:
            return int(num * _place_former) / _place_former
        else:
            rst = int(num * _place) / _place - _up
            return rst if rst > 0 else 0
    else:
        return num


def delta_fuc(low, high):
    down = float("-inf")
    up = float("inf")
    if not math.isnan(low):
        down = low + DELTA
    if not math.isnan(high):
        up = high - DELTA
    if down >= up:
        down = low
        up = high
    return down, up
