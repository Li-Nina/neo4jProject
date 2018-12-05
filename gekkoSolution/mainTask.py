#!/usr/bin/env python
# -*- coding:utf-8 -*-
from gekkoSolution.gekkoConstruct import ObjectiveConstructBuilder, \
    PriceObjectiveConstruct, IngredientObjectiveConstruct
from gekkoSolution.gekkoProblem import GekkoProblem
from utils.logger import Logger

from utils.utils import cal_weights

logger = Logger(__name__).get()

# todo 打包，日志
lp = GekkoProblem("../../data/template.xlsx")

weights = cal_weights(lp, **{'TFe': 1, 'SiO2': 1, 'COST': 1})

lp.remove_construct("objective")
objectives = ObjectiveConstructBuilder(lp,
                                       (PriceObjectiveConstruct(lp), weights['cost']),
                                       (IngredientObjectiveConstruct(lp, ingredient_name="TFe", maximum=True),
                                        weights['tfe']),
                                       (IngredientObjectiveConstruct(lp, ingredient_name="SiO2", maximum=False),
                                        weights['sio2'])
                                       )
lp.add_construct("objective", objectives)

lp.build()

lp.prob.options.IMODE = 3  # steady state optimization

print(lp.prob)

# Solve simulation
lp.solve()
lp.print_solve()
print(lp.get_price())
print(lp.get_ingredient_result())

lp.write_to_excel("../../data/result.xlsx")
