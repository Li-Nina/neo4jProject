#!/usr/bin/env python
# -*- coding:utf-8 -*-
import time

from ratioSolution.algorithmAPI import _default_weights_list_cal, _goal_fcn_list, _custom_weights_list_cal
from ratioSolution.construct import ObjectiveConstructBuilder, IngredientObjectiveConstruct, PriceObjectiveConstruct, \
    SSObjectiveConstruct, RObjectiveConstruct
from ratioSolution.problem import Problem
from utils.config import DIGIT
from utils.util import adjust_digit, number_scalar_modified

try:
    step = 0.001  # 循环计算步长
    iters = 6  # 循环次数

    start = time.time()

    lp = Problem("../data/template-validate-20190408.xls")
    goal_fcn = _goal_fcn_list(lp.data)
    weights_all = _default_weights_list_cal(lp.data, goal_fcn)
    # weights_ = _custom_weights_list_cal([{'TFe': 1, 'SiO2': 1, 'COST': 1}], lp.data, goal_fcn)
    # weights_ = _custom_weights_list_cal([{'TFe': 1}], lp.data, goal_fcn)
    # weights_ = _custom_weights_list_cal([{'SiO2': 1}], lp.data, goal_fcn)
    weights_ = _custom_weights_list_cal([{'COST': 1}], lp.data, goal_fcn)
    # weights_ = _custom_weights_list_cal([{'R': 1}], lp.data, goal_fcn)
    # weights_ = _custom_weights_list_cal([{'SS': 1}], lp.data, goal_fcn)
    # weights_ = _custom_weights_list_cal([{'AL2O3': 1}], lp.data, goal_fcn)
    # weights_ = _custom_weights_list_cal([{'Cr': 1}], lp.data, goal_fcn)
    print(weights_all)
    print(weights_)
    weights = weights_[0]

    cao_index = lp.data.Ingredients_list_name_index.get('CaO'.lower())
    sio2_index = lp.data.Ingredients_list_name_index.get('SiO2'.lower())

    r_enable = False
    if cao_index is not None and sio2_index is not None:
        r_enable = True

    objectives = ObjectiveConstructBuilder(lp,
                                           (PriceObjectiveConstruct(lp), weights['cost']),
                                           # (IngredientObjectiveConstruct(lp, ingredient_name="TFe", maximum=True),
                                           #  weights['tfe']),
                                           # (IngredientObjectiveConstruct(lp, ingredient_name="SiO2", maximum=False),
                                           #  weights['sio2']),
                                           # (IngredientObjectiveConstruct(lp, ingredient_name="al2o3", maximum=False),
                                           #  weights['al2o3']),
                                           # (IngredientObjectiveConstruct(lp, ingredient_name="Cr", maximum=False),
                                           #  weights['cr']),
                                           # (RObjectiveConstruct(lp), weights['r']),
                                           # (SSObjectiveConstruct(lp), weights['ss'])
                                           )
    lp.add_construct("objective", objectives)
    lp.build()
    lp.prob.options.IMODE = 3  # steady state optimization
    objfcn = objectives.get_obj()  # 目标函数公式
    lp.solve(disp=True)
    objfcnval = lp.get_objfcnval()  # 单目标(初始)优化下的最优值(最小值)
    print("1111111----->", objfcnval)
    obj_val = adjust_digit(num=objfcnval, digit=DIGIT + 1)  # DIGIT+1位小数
    print("2222222----->", obj_val)
    obj_scalar = number_scalar_modified(obj_val)
    print("3333333----->", obj_scalar)
    plus_step = step * obj_scalar
    print("4444444----->", plus_step)
    print("@@@@@@@@@@@@", lp.prob._objectives)
    lp.prob._objectives.clear()
    lp.prob.Obj(PriceObjectiveConstruct(lp).get_obj())
    print("@@@@@@@@@@@@", lp.prob._objectives)
    for i in range(iters):
        print("@@@@@@@@@@@@", lp.prob._equations)
        if i > 0:
            lp.prob._equations.pop()
        lp.prob.Equation(objfcn == obj_val + i * plus_step)
        print("@@@@@@@@@@@@", lp.prob._equations)

        lp.solve(disp=True)
        print("======<<<", lp.get_objfcnval())

        lp.print_solve()
        print(lp.get_price_result())
        ingredient_result = lp.get_ingredient_result()
        print(ingredient_result)
        if r_enable:
            print("R = ", ingredient_result[cao_index] / ingredient_result[sio2_index])  # 碱度R=CaO/SiO2，目标高碱度
        print("objfcnval ============================================================> ", lp.get_objfcnval())

        if i == 0:  # 最优结果
            lp.write_excel()

        print("-------->", lp.get_objfcnval())
        lp.write_excel("../data/results/result" + str(i) + ".xlsx")

    end = time.time()
    print("time ------>:", end - start)
except Exception as e:
    print(repr(e))
