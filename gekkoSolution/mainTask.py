#!/usr/bin/env python
# -*- coding:utf-8 -*-
import time
import traceback

from gekkoSolution.gekkoConstruct import ObjectiveConstructBuilder, \
    PriceObjectiveConstruct, IngredientObjectiveConstruct, RObjectiveConstruct, SSObjectiveConstruct
from gekkoSolution.gekkoProblem import GekkoProblem
from gekkoSolution.gekkoUtils import cal_weights
from utils.const import GEKKO_LOG_NAME
from utils.logger import Logger
from utils.utils import number_scalar

logger = Logger(GEKKO_LOG_NAME, log_file_path='../log/gekko_optimization.log').get()

try:
    step = 0.001  # 循环计算步长
    iters = 5  # 循环次数

    start = time.time()

    lp = GekkoProblem()
    weights = cal_weights(lp, **{'TFe': 1, 'SiO2': 1, 'COST': 1, 'R': 1, 'SS': 1})
    # weights = cal_weights(lp, **{'COST': 1000, 'R': 1})
    # weights = cal_weights(lp, **{'R': 1})
    # weights = cal_weights(lp, **{'COST': 1})

    cao_index = lp.data.Ingredients_list_name_index.get('CaO'.lower())
    sio2_index = lp.data.Ingredients_list_name_index.get('SiO2'.lower())
    r_enable = False
    if cao_index is not None and sio2_index is not None:
        r_enable = True

    lp.remove_construct("objective")
    objectives = ObjectiveConstructBuilder(lp,
                                           # (PriceObjectiveConstruct(lp), weights['cost']),
                                           # (IngredientObjectiveConstruct(lp, ingredient_name="TFe", maximum=True),
                                           #  weights['tfe']),
                                           (IngredientObjectiveConstruct(lp, ingredient_name="SiO2", maximum=False),
                                            weights['sio2']),
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

        lp.print_solve()
        print(lp.get_price())
        ingredient_result = lp.get_ingredient_result()
        print(ingredient_result)
        if r_enable:
            print("R = ", ingredient_result[cao_index] / ingredient_result[sio2_index])  # 碱度R=CaO/SiO2，目标高碱度
        print("objfcnval ============================================================> ", lp.get_objfcnval())

        if objfcnval is None:  # 最优结果
            lp.write_to_excel()

        objfcnval = lp.get_objfcnval()
        lp.write_to_excel("../data/results/result" + str(i) + ".xlsx")

    end = time.time()
    logger.info("gekko_optimization task run successfully, runtime  is %s s:", end - start)
except Exception as e:
    print(repr(e))
    logger.error(traceback.format_exc())
