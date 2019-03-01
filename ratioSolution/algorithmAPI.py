#!/usr/bin/env python
# -*- coding:utf-8 -*-
import json
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
    :param template: excel模板文件或路径
    :param iters: 循环次数
    :param steps: 循环计算步长
    :return:result_list json格式
        [{
            "type": 0,                          # type=0单目标函数(单个最优)，type=1多目标函数，默认全部(综合排序)
            "obj": ["tfe"],                     # obj list, 优化目标对象
            "weight": [1],                      # weight list, 优化目标对象间比例
            "data": [{                          # data jsonList<json>, 计算结果
                "step": 0.1,                    # step 结果步长
                "result": [                     # result list<list>, 该step下的多个比例结果
                    [1, 2, 3],
                    [4, 5, 6],
                    [7, 8, 9]
                ],
                "name": ["铁粉", "高反", "澳粉"]  # name 比例对应的原料名称
            }, {
                "step": 0.01,
                "result": [
                    [1, 2, 3],
                    [4, 5, 6],
                    [7, 8, 9]
                ],
                "name": ["铁粉", "高反", "澳粉"]
            }, {
                "step": 0.001,
                "result": [
                    [1, 2, 3],
                    [4, 5, 6],
                    [7, 8, 9]
                ],
                "name": ["铁粉", "高反", "澳粉"]
            }]
        }, {
            "type": 1,
            "obj": ["tfe", "al2o3", "ss"],
            "weight": [1, 1, 1],
            "data": [{
                "step": 0.1,
                "result": [
                    [1, 2, 3],
                    [4, 5, 6],
                    [7, 8, 9]
                ],
                "name": ["铁粉", "高反", "澳粉"]
            }, {
                "step": 0.01,
                "result": [
                    [1, 2, 3],
                    [4, 5, 6],
                    [7, 8, 9]
                ],
                "name": ["铁粉", "高反", "澳粉"]
            }, {
                "step": 0.001,
                "result": [
                    [1, 2, 3],
                    [4, 5, 6],
                    [7, 8, 9]
                ],
                "name": ["铁粉", "高反", "澳粉"]
            }]
        }]
    """
    if steps is None:
        steps = [0.1, 0.01, 0.001, 0.0001]

    lp = Problem(excel_file=template)
    goal_fcn = _goal_fcn_list(lp)
    # [ {Tfe:1}, {Al2O3:1} , {Tfe:1, Al2O3:1} ]
    weights_list = _weights_list_cal(lp, goal_fcn)
    result_list = []
    for weight in weights_list:
        _sub_rst = {'type': 0 if len(weight) == 1 else 1, 'obj': list(weight.keys()), 'weight': list(weight.values())}
        _data = []
        for step in steps:
            lp = Problem(excel_file=template)
            objectives = ObjectiveConstructBuilder(lp, *_objectives_list(lp, weight))
            lp.add_construct("objective", objectives)  # 目标函数self._constructs["objective"]在此处生成
            lp.build()
            lp.prob.options.IMODE = 3  # steady state optimization

            objfcn = objectives.get_obj()  # 目标函数公式
            objfcnval = None  # 上一次目标函数计算值

            _sub_data = {'step': step}
            _rst_list = []
            _name = None
            for i in range(iters):
                if objfcnval is not None:  # 防止objfcnval为0，不写if objfcnval
                    obj_scalar = number_scalar_modified(objfcnval)
                    lp.prob.Equation(objfcn >= objfcnval + step * obj_scalar)
                # Solve simulation
                try:
                    lp.solve(disp=False)
                except Exception:
                    # 没有最优解，跳出循环
                    break
                objfcnval = lp.get_objfcnval()
                _result, _name = lp.get_result()

                _rst_list.append(_result)

            _sub_data['result'] = _rst_list
            _sub_data['name'] = _name
            _data.append(_sub_data)
        _sub_rst['data'] = _data
        result_list.append(_sub_rst)

    return json.dumps(result_list, ensure_ascii=False)


def _goal_fcn_list(lp):
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


def _objectives_list(lp, weights):
    print(weights)
    name_list = list(weights.keys())
    _rst = []
    for name in name_list:
        if name.lower() == 'cost':
            _rst.append((PriceObjectiveConstruct(lp), weights['cost']))
        elif name.lower() == 'r':
            _rst.append((RObjectiveConstruct(lp), weights['r']))
        elif name.lower() == 'ss':
            _rst.append((SSObjectiveConstruct(lp), weights['ss']))
        elif name.lower() == 'tfe':
            _rst.append((IngredientObjectiveConstruct(lp, ingredient_name="TFe", maximum=True), weights['tfe']))
        elif name.lower() == 'sio2':
            _rst.append((IngredientObjectiveConstruct(lp, ingredient_name="SiO2", maximum=False), weights['sio2']))
        elif name.lower() == 'al2o3':
            _rst.append((IngredientObjectiveConstruct(lp, ingredient_name="Al2O3", maximum=False), weights['al2o3']))
        else:
            raise NotFoundError('objective not found!')
    return _rst


def _weights_list_cal(lp, goal_list):
    weights_list = []
    total_dic = {}
    for i in goal_list:
        weights_list.append({i.lower(): 1})
        total_dic[i.lower()] = 1
    weights_list.append(cal_weights(lp, **total_dic))
    return weights_list


if __name__ == '__main__':
    s = ratio_algorithm("../data/template.xlsx")
    print(s)
    print(len(s))
