#!/usr/bin/env python
# -*- coding:utf-8 -*-
import math

from gekkoSolution.customException import NotFoundError, NumberError
from utils.logger import Logger
from utils.utils import check_nan
import numpy as np

logger = Logger(__name__, log_file_path='../log/gekko_optimization.log').get()


def cal_weights(pb, **kw):
    """
    :param pb:optimization_problem
    :param kw:每个目标的权重，其中价格的key为cost
              eg: tfe=1, sio2=3, cost=1
              eg: **{'tfe': 1, 'sio2': 3, 'cost': 1}
    :return dict: key=目标名称,value=计算的加权权重
    """
    name_scalar_weight = []
    unused = ['up', 'down']
    for key, value in kw.items():
        if key.lower() == 'cost':
            cost_list = [check_nan(v) for k, v in pb.data.Cost.items() if k not in unused]
            scalar = sum(cost_list) / len(cost_list)
        elif key.lower() == 'ss':
            scalar = _cal_scalar(pb.data.SS, unused)
        elif key.lower() == 'r':
            scalar = _cal_scalar_r(pb, unused)
        else:
            index = pb.data.Ingredients_list_name_index.get(key.lower())
            if index is not None:
                scalar = _cal_scalar(pb.data.Ingredients_list[index], unused)
            else:
                logger.error('ingredients ' + key.lower() + ' not found!')
                raise NotFoundError('ingredients ' + key.lower() + ' not found!')
        # [('cost', 500, 1), ('tfe', 50, 5), ('sio2', 5, 2), ('al2o3', 3, 1)]
        name_scalar_weight.append((key.lower(), scalar, value))

    # [('cost', 'tfe', 'sio2', 'al2o3'), (500, 50, 5, 3), (1, 5, 2, 1)]
    name_scalar_weight = list(zip(*name_scalar_weight))

    logger.info('name_scalar_weight is ' + str(name_scalar_weight))

    scalar = [100 / i for i in name_scalar_weight[1]]
    weight = np.multiply(np.array(scalar), np.array(list(name_scalar_weight[2]))).tolist()
    normalization_weight = [100 * i / sum(weight) for i in weight]

    name_weight_dict = dict(zip(name_scalar_weight[0], normalization_weight))
    logger.info('name_normalization_weight is ' + str(name_weight_dict))
    return name_weight_dict


def _cal_scalar(ing_dic, unused):
    if check_nan(ing_dic.get('up')) == 0 and check_nan(ing_dic.get('down')) == 0:
        # 根据平均值计算scalar
        lists = [check_nan(v) for k, v in ing_dic.items() if k not in unused]
        scalar = sum(lists) / len(lists)
    else:
        # 根据上下限计算scalar
        scalar = (check_nan(ing_dic.get('up')) + check_nan(ing_dic.get('down'))) / 2
    return scalar


def _cal_scalar_r(pb, unused):
    cao_index = pb.data.Ingredients_list_name_index.get('CaO'.lower())
    sio2_index = pb.data.Ingredients_list_name_index.get('SiO2'.lower())
    if cao_index is not None and sio2_index is not None:
        logger.info('_cal_scalar_r finding cao_index is %s, sio2_index is %s', cao_index, sio2_index)
        cao_dic = pb.data.Ingredients_list[cao_index]
        sio2_dic = pb.data.Ingredients_list[sio2_index]
        scalar = _cal_scalar(cao_dic, unused) / _cal_scalar(sio2_dic, unused)
        if math.isfinite(scalar):
            return scalar
        else:
            logger.error('R=CaO/SiO2 scalar failed! scalar is %s', scalar)
            raise NumberError('R=CaO/SiO2 scalar failed! scalar is %s', scalar)
    else:
        logger.error('R=CaO/SiO2 scalar failed! finding cao_index is %s, sio2_index is %s', cao_index, sio2_index)
        raise NotFoundError('R=CaO/SiO2 not found! cao_index is %s, sio2_index is %s', cao_index, sio2_index)
