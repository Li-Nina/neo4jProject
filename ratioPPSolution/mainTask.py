#!/usr/bin/env python
# -*- coding:utf-8 -*-
import logging
import traceback

# lp = MinPriceProblem("../data/template.xlsx")
from ratioPPSolution.ppProblem import PPProblem
from utils.config import APP_LOG_NAME

logger = logging.getLogger(APP_LOG_NAME + "." + __name__)

try:
    lp = PPProblem()
    # lp.prob = LpProblem("maxPro", LpMaximize)
    # lp.remove_construct("objective")
    # lp.add_construct("objective", FeObjectivePulpConstruct())
    # lp.add_construct("objective", SiObjectiveConstruct())
    lp.build()
    print(lp.prob)

    lp.solve()
    print(lp.get_solve_status())

    lp.print_solve()
    print(lp.get_ingredient_result())
    print(lp.get_price())

    lp.write_excel()
except Exception as e:
    print(repr(e))
    logger.error(traceback.format_exc())
