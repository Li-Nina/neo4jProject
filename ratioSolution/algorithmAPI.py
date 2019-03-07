#!/usr/bin/env python
# -*- coding:utf-8 -*-
import logging

from ratioSolution.construct import ObjectiveConstructBuilder, IngredientObjectiveConstruct, PriceObjectiveConstruct, \
    RObjectiveConstruct, SSObjectiveConstruct
from ratioSolution.customException import NotFoundError
from ratioSolution.problem import Problem
from ratioSolution.util import cal_weights
from utils.config import APP_LOG_NAME
from utils.excelParse import ExcelParse
from utils.util import number_scalar_modified

logger = logging.getLogger(APP_LOG_NAME + "." + __name__)


def ratio_algorithm(excel_template, top_n=None, steps=None, custom_weights_list=None, ctrl_constructs_dict=None):
    """
    :param excel_template: excel模板文件或路径
    :param top_n: 每个步长给出前topN 结果
    :param steps: topN的计算步长
    :param custom_weights_list: 要计算的目标和权重,eg. [{Tfe:1},{Al2O3:1},{Tfe:1,Al2O3:1}] .默认计算所有目标和全部目标组合的1:1权重
    :param ctrl_constructs_dict: dict {'subjective_grain_size':1, 'var_group':0} 用于控制是否有粘附比限制和配料分组要求
    :return:result_list list格式
        [{
            "type": 0,                              # type=0单目标函数(单个最优)，type=1多目标函数，默认全部(综合排序)
            "obj": ["tfe"],                         # obj list, 优化目标对象
            "weight": [1],                          # weight list, 优化目标对象间比例
            "name": ["巴西粗粉", "高品澳粉", "高返"],   # name 比例对应的原料名称
            "data": [{                              # data jsonList<json>, 计算结果
                "step": 0.1,                        # step 结果步长
                "result": [                         # result list<list>, 该step下的多个比例结果
                    [1, 2, 3],
                    [4, 5, 6],
                    [7, 8, 9]
                ]
            }, {
                "step": 0.01,
                "result": [
                    [1, 2, 3],
                    [4, 5, 6],
                    [7, 8, 9]
                ]
            }, {
                "step": 0.001,
                "result": [
                    [1, 2, 3],
                    [4, 5, 6],
                    [7, 8, 9]
                ]
            }]
        }, {
            "type": 1,
            "obj": ["tfe", "al2o3", "ss"],
            "weight": [1, 1, 1],
            "name": ["巴西粗粉", "高品澳粉", "高返"],
            "data": [{
                "step": 0.1,
                "result": [
                    [1, 2, 3],
                    [4, 5, 6],
                    [7, 8, 9]
                ]
            }, {
                "step": 0.01,
                "result": [
                    [1, 2, 3],
                    [4, 5, 6],
                    [7, 8, 9]
                ]
            }, {
                "step": 0.001,
                "result": [
                    [1, 2, 3],
                    [4, 5, 6],
                    [7, 8, 9]
                ]
            }]
        }]
    """
    if top_n is None:
        top_n = 5
    if steps is None:
        steps = [0.1, 0.01, 0.001, 0.0001]

    excel_data = ExcelParse(excel_file=excel_template)
    # 可以计算的目标小写名称 ['cost', 'ss', 'tfe', 'al2o3', 'sio2', 'r']
    goal_fcn = _goal_fcn_list(excel_data)
    if custom_weights_list:
        # 根据custom_weights_list计算需要的目标和权重 [ {tfe:1}, {al2o3:1} , {tfe:1, al2o3:1} ]
        weights_list = _custom_weights_list_cal(custom_weights_list, excel_data, goal_fcn)
    else:
        # 默认计算的所有目标和权重 [ {tfe:1}, {al2o3:1} , {tfe:1, al2o3:1} ]
        weights_list = _default_weights_list_cal(excel_data, goal_fcn)
    logger.info("------> %s", weights_list)

    result_list = []
    for weight in weights_list:
        _sub_rst = {'type': 0 if len(weight) == 1 else 1,
                    'obj': list(weight.keys()),
                    'weight': list(weight.values()),
                    'name': [excel_data.Ingredients_names["var_" + k] for k in excel_data.Ingredients]
                    }
        _data = []
        for step in steps:
            # 可变参数函数接收到一个tuple，info函数里msg = msg % args,args是一个tuple，因此可以指定多个%s
            logger.info("cal... step is %s, weight is %s", step, weight)
            lp = Problem(excel_data=excel_data, excel_type='data', ctrl_constructs_dict=ctrl_constructs_dict)
            objectives = ObjectiveConstructBuilder(lp, *_objectives_list(lp, weight))
            lp.add_construct("objective", objectives)  # 目标函数self._constructs["objective"]在此处生成
            lp.build()
            lp.prob.options.IMODE = 3  # steady state optimization

            objfcn = objectives.get_obj()  # 目标函数公式
            objfcnval = None  # 上一次目标函数计算值

            _sub_data = {'step': step}
            _rst_list = []
            for i in range(top_n):
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
                _rst_list.append(lp.get_result())

            _sub_data['result'] = _rst_list
            _data.append(_sub_data)
        _sub_rst['data'] = _data
        result_list.append(_sub_rst)
    return result_list


def _goal_fcn_list(excel_data):
    """
    :return: 可以计算的目标名称，需小写,其中必包含cost和ss，最长为['cost', 'ss', 'tfe', 'al2o3', 'sio2', 'r']
    """
    _goal_list = ['cost', 'ss']
    tfe_index = excel_data.Ingredients_list_name_index.get('TFe'.lower())
    al2o3_index = excel_data.Ingredients_list_name_index.get('Al2O3'.lower())
    cao_index = excel_data.Ingredients_list_name_index.get('CaO'.lower())
    sio2_index = excel_data.Ingredients_list_name_index.get('SiO2'.lower())
    if tfe_index is not None:
        _goal_list.append('tfe')
    if al2o3_index is not None:
        _goal_list.append('al2o3')
    if sio2_index is not None:
        _goal_list.append('sio2')
    if cao_index is not None and sio2_index is not None:
        _goal_list.append('r')
    return _goal_list


def _objectives_list(lp, weights):
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


def _default_weights_list_cal(excel_data, goal_list):
    weights_list = []
    total_dic = {}
    for i in goal_list:
        weights_list.append({i: 1})
        total_dic[i] = 1
    weights_list.append(cal_weights(excel_data, **total_dic))
    return weights_list


def _custom_weights_list_cal(custom_weights_list, excel_data, goal_fcn):
    weights_list = []
    for custom_weight in custom_weights_list:
        if all(_.lower() in goal_fcn for _ in custom_weight.keys()):
            if len(custom_weight) == 1:
                weights_list.append({k.lower(): 1 for k, v in custom_weight.items()})
            else:
                weights_list.append(cal_weights(excel_data, **custom_weight))
        else:
            raise ValueError('custom_weights_list is incorrect!')
    return weights_list
