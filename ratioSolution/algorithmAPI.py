#!/usr/bin/env python
# -*- coding:utf-8 -*-
import logging
import traceback
from ratioSolution.construct import ObjectiveConstructBuilder, IngredientObjectiveConstruct, PriceObjectiveConstruct, \
    RObjectiveConstruct, SSObjectiveConstruct
from ratioSolution.problem import Problem
from ratioSolution.util import cal_weights
from serverWeb.config import APP_LOG_NAME
from serverWeb.ratioAlgorithm import ResponseJson
from utils.utils import number_scalar, convert_namedtuple, current_time_millis

logger = logging.getLogger(APP_LOG_NAME + "." + __name__)


def ratio_algorithm(template):
    try:
        step = 0.001  # 循环计算步长
        iters = 5  # 循环次数

        lp = Problem(excel_file=template)

        weights = cal_weights(lp, **{'TFe': 1, 'SiO2': 1, 'Al2O3': 1, 'COST': 1, 'R': 1, 'SS': 1})
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
                                               (PriceObjectiveConstruct(lp), weights['cost']),
                                               (IngredientObjectiveConstruct(lp, ingredient_name="TFe", maximum=True),
                                                weights['tfe']),
                                               (IngredientObjectiveConstruct(lp, ingredient_name="SiO2",
                                                                             maximum=False),
                                                weights['sio2']),
                                               (IngredientObjectiveConstruct(lp, ingredient_name="Al2O3",
                                                                             maximum=False),
                                                weights['al2o3']),
                                               (RObjectiveConstruct(lp), weights['r']),
                                               (SSObjectiveConstruct(lp), weights['ss'])
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

        logger.info("gekko_optimization task run successfully")


    except Exception as e:
        print(repr(e))
        logger.error(traceback.format_exc())
        return convert_namedtuple(ResponseJson(status=1,
                                               msg='OK,using model {}'.format('sss'),
                                               result=str(e),
                                               stamp=current_time_millis()
                                               ))

    return 'nlp classification server database {}.........'.format('gggggggg')


def tes(*tt):
    print(tt)


if __name__ == '__main__':
    # ratio_algorithm("../data/template.xlsx")
    tes(*[1, 2, 3])
