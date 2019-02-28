#!/usr/bin/env python
# -*- coding:utf-8 -*-
import logging

from ratioSolution.construct import ObjectiveConstructBuilder, IngredientObjectiveConstruct, PriceObjectiveConstruct, \
    RObjectiveConstruct, SSObjectiveConstruct
from ratioSolution.customException import NotFoundError
from ratioSolution.problem import Problem
from ratioSolution.util import cal_weights
from utils.config import APP_LOG_NAME
from utils.util import number_scalar_modified

logger = logging.getLogger(APP_LOG_NAME + "." + __name__)


def ratio_algorithm(template, iters=5, steps=None):
    """
    :param template:
    :param iters:  循环次数
    :param steps: 循环计算步长
    :return:
    """
    if steps is None:
        steps = [0.1, 0.01, 0.001, 0.0001]

    lp = Problem(excel_file=template)
    goal_fcn = goal_fcn_list(lp)
    weights_list = weights_list_cal(lp, goal_fcn)

    for step in steps:
        for weight in weights_list:
            lp = Problem(excel_file=template)
            objectives = ObjectiveConstructBuilder(lp, *objectives_list(lp, weight))
            lp.add_construct("objective", objectives)  # 目标函数self._constructs["objective"]在此处生成
            lp.build()
            lp.prob.options.IMODE = 3  # steady state optimization

            objfcn = objectives.get_obj()  # 目标函数公式
            objfcnval = None  # 上一次目标函数计算值
            for i in range(iters):
                if objfcnval is not None:  # 防止objfcnval为0，不写if objfcnval
                    obj_scalar = number_scalar_modified(objfcnval)
                    lp.prob.Equation(objfcn >= objfcnval + step * obj_scalar)
                # Solve simulation
                try:
                    lp.solve(disp=True)
                except Exception as e:
                    # 没有最优解，跳出循环
                    break
                objfcnval = lp.get_objfcnval()
                result, names = lp.get_result()


def goal_fcn_list(lp):
    _goal_list = ['COST', 'SS']
    tfe_index = lp.data.Ingredients_list_name_index.get('TFe'.lower())
    al2o3_index = lp.data.Ingredients_list_name_index.get('Al2O3'.lower())
    cao_index = lp.data.Ingredients_list_name_index.get('CaO'.lower())
    sio2_index = lp.data.Ingredients_list_name_index.get('SiO2'.lower())
    if tfe_index is not None:
        _goal_list.append('TFe')
    if al2o3_index is not None:
        _goal_list.append('Al2O3')
    if sio2_index is not None:
        _goal_list.append('SiO2')
    if cao_index is not None and sio2_index is not None:
        _goal_list.append('R')
    return _goal_list


def objectives_list(lp, weights):
    name_list = list(weights.keys())
    _rst = []
    for name in name_list:
        if name.lower() == 'cost':
            _rst.append((PriceObjectiveConstruct(lp), weights['cost']))
        if name.lower() == 'r':
            _rst.append((RObjectiveConstruct(lp), weights['r']))
        if name.lower() == 'ss':
            _rst.append((SSObjectiveConstruct(lp), weights['ss']))
        if name.lower() == 'tfe':
            _rst.append((IngredientObjectiveConstruct(lp, ingredient_name="TFe", maximum=True), weights['tfe']))
        if name.lower() == 'sio2':
            _rst.append((IngredientObjectiveConstruct(lp, ingredient_name="SiO2", maximum=False), weights['sio2']))
        if name.lower() == 'al2o3':
            _rst.append((IngredientObjectiveConstruct(lp, ingredient_name="Al2O3", maximum=False), weights['al2o3']))
        else:
            raise NotFoundError('objective not found!')
    return _rst


def weights_list_cal(lp, goal_list):
    weights_list = []
    total_dic = {}
    for i in goal_list:
        weights_list.append({i: 1})
        total_dic[i] = 1
    weights_list.append(cal_weights(lp, **total_dic))
    return weights_list


if __name__ == '__main__':
    # ratio_algorithm("../data/template.xlsx")
    pass
