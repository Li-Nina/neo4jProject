#!/usr/bin/env python
# -*- coding:utf-8 -*-
import time

from ratioSolution.algorithmAPI import _default_weights_list_cal, _goal_fcn_list, _custom_weights_list_cal
from ratioSolution.construct import ObjectiveConstructBuilder, IngredientObjectiveConstruct, PriceObjectiveConstruct, \
    SSObjectiveConstruct, RObjectiveConstruct, IngredientsFixed
from ratioSolution.problem import Problem
from ratioSolution.util import cal_weights
from utils.util import number_scalar

try:
    step = 0.001  # 循环计算步长
    iters = 1  # 循环次数

    start = time.time()

    lp = Problem("../data/template-validate-20190408.xls")
    goal_fcn = _goal_fcn_list(lp.data)
    weights_all = _default_weights_list_cal(lp.data, goal_fcn)
    # weights_ = _custom_weights_list_cal([{'TFe': 1}], lp.data, goal_fcn)
    # weights_ = _custom_weights_list_cal([{'SiO2': 1}], lp.data, goal_fcn)
    # weights_ = _custom_weights_list_cal([{'COST': 1}], lp.data, goal_fcn)
    # weights_ = _custom_weights_list_cal([{'R': 1}], lp.data, goal_fcn)
    # weights_ = _custom_weights_list_cal([{'SS': 1}], lp.data, goal_fcn)
    # weights_ = _custom_weights_list_cal([{'AL2O3': 1}], lp.data, goal_fcn)
    weights_ = _custom_weights_list_cal([{'Cr': 1}], lp.data, goal_fcn)
    print(weights_all)
    print(weights_)
    weights = weights_[0]

    cao_index = lp.data.Ingredients_list_name_index.get('CaO'.lower())
    sio2_index = lp.data.Ingredients_list_name_index.get('SiO2'.lower())

    tfe_index = lp.data.Ingredients_list_name_index.get('TFe'.lower())

    r_enable = False
    if cao_index is not None and sio2_index is not None:
        r_enable = True

    lp.remove_construct("objective")
    objectives = ObjectiveConstructBuilder(lp,
                                           # (PriceObjectiveConstruct(lp), weights['cost']),
                                           # (IngredientObjectiveConstruct(lp, ingredient_name="TFe", maximum=True),
                                           #  weights['tfe']),
                                           # (IngredientObjectiveConstruct(lp, ingredient_name="SiO2", maximum=False),
                                           #  weights['sio2']),
                                           # (IngredientObjectiveConstruct(lp, ingredient_name="al2o3", maximum=False),
                                           #  weights['al2o3']),
                                           (IngredientObjectiveConstruct(lp, ingredient_name="Cr", maximum=False),
                                            weights['cr']),
                                           # (RObjectiveConstruct(lp), weights['r']),
                                           # (SSObjectiveConstruct(lp), weights['ss'])
                                           )
    lp.add_construct("objective", objectives)

    lp.build()

    lp.prob.options.IMODE = 3  # steady state optimization

    objfcn = objectives.get_obj()  # 目标函数公式
    objfcnval = None  # 上一次目标函数计算值
    for i in range(iters):
        if objfcnval is not None:  # 防止objfcnval为0，不写if objfcnval
            obj_scalar = number_scalar(objfcnval)
            lp.prob.Equation(objfcn >= objfcnval + step * obj_scalar)
            print("objfcn >= {0} + {1} = {2}".format(objfcnval, step * obj_scalar,
                                                     objfcnval + step * obj_scalar))

        # Solve simulation
        lp.solve(disp=True)
        print("======<<<", lp.get_objfcnval())

        IngredientsFixed(lp, 'cr', maximum=False)
        # IngredientsFixed(lp, 'tfe', maximum=True)
        lp.solve(disp=True)

        lp.print_solve()
        print(lp.get_price_result())
        ingredient_result = lp.get_ingredient_result()
        print(ingredient_result)
        if r_enable:
            print("R = ", ingredient_result[cao_index] / ingredient_result[sio2_index])  # 碱度R=CaO/SiO2，目标高碱度
        print("objfcnval ============================================================> ", lp.get_objfcnval())

        # ingredient_result[tfe_index]
        if objfcnval is None:  # 最优结果
            lp.write_excel()

        objfcnval = lp.get_objfcnval()
        print("-------->", objfcnval)
        lp.write_excel("../data/results/result" + str(i) + ".xlsx")

    end = time.time()
except Exception as e:
    print(repr(e))
