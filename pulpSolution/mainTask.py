#!/usr/bin/env python
# -*- coding:utf-8 -*-
import traceback

# lp = MinPriceProblem("../data/template.xlsx")
from pulpSolution.pulpConstruct import FeObjectivePulpConstruct
from pulpSolution.pulpProblem import PulpProblem
from utils.logger import Logger

logger = Logger(__name__, log_file_path='../log/pulp_optimization.log').get()

try:
    lp = PulpProblem()
    # lp.prob = LpProblem("maxPro", LpMaximize)
    # lp.remove_construct("objective")
    lp.add_construct("objective", FeObjectivePulpConstruct())
    # lp.add_construct("objective", SiObjectiveConstruct())
    lp.build()
    print(lp.prob)

    lp.solve()
    print(lp.get_solve_status())

    lp.print_solve()
    print(lp.get_ingredient_result())
    print(lp.get_price())

    lp.write_to_excel()
except Exception as e:
    print(repr(e))
    logger.error(traceback.format_exc())
