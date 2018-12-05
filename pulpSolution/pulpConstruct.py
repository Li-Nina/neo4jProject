#!/usr/bin/env python
# -*- coding:utf-8 -*-
import math

from pulp import lpSum

from utils.utils import check_nan


class PulpConstruct:
    def __init__(self):
        pass

    def build(self, min_price_problem):
        pass


class ObjectivePulpConstruct(PulpConstruct):
    def build(self, pb):
        pb.prob += lpSum(
            [check_nan(pb.data.Cost[k]) * pb.ingredient_vars[k]
             * (1 - check_nan(pb.data.H2O[k]) / 100) / 100 for k in pb.data.Ingredients]
            + [check_nan(pb.data.Cost[k]) * pb.ingredient_vars[k] * pb.data.H2O[k] / 10000
               for k in pb.data.Ingredients]
            + [check_nan(pb.data.Cost[k]) * pb.ingredient_vars[k] * pb.data.SS[k] / 10000
               for k in pb.data.Ingredients]
        )


class SubjectivePulpConstruct(PulpConstruct):
    def build(self, pb):
        pb.prob += lpSum([pb.ingredient_vars[k] for k in pb.data.Ingredients]) == 100
        for Element in pb.data.Ingredients_list:
            if not math.isnan(Element["down"]):
                pb.prob += lpSum([pb.ingredient_vars[k] * check_nan(Element[k])
                                  * (100 - check_nan(pb.data.H2O[k])) / 100
                                  for k in pb.data.Ingredients]) >= Element["down"] * (100 - pb.h_2_0)

            if not math.isnan(Element["up"]):
                pb.prob += lpSum([pb.ingredient_vars[k] * check_nan(Element[k])
                                  * (100 - check_nan(pb.data.H2O[k])) / 100
                                  for k in pb.data.Ingredients]) <= Element["up"] * (100 - pb.h_2_0)


class VarPulpConstruct(PulpConstruct):
    def build(self, pb):
        for k in pb.data.Ingredients:
            if not math.isnan(pb.data.UP[k]):
                pb.prob += pb.ingredient_vars[k] <= pb.data.UP[k]
            if not math.isnan(pb.data.Down[k]):
                pb.prob += pb.ingredient_vars[k] >= pb.data.Down[k]


class VarGroupPulpConstruct(PulpConstruct):
    def build(self, pb):
        for g in pb.data.Group.values():
            up = pb.data.Group_up[g[0]]
            down = pb.data.Group_down[g[0]]
            if not math.isnan(up):
                pb.prob += lpSum(pb.ingredient_vars[element] for element in g) <= up
            if not math.isnan(down):
                pb.prob += lpSum(pb.ingredient_vars[element] for element in g) >= down


class FeObjectivePulpConstruct(PulpConstruct):
    def build(self, pb):
        fe = pb.data.Ingredients_list[0]
        pb.prob += lpSum([pb.ingredient_vars[k] * check_nan(fe[k])
                          * (100 - check_nan(pb.data.H2O[k])) / 100
                          for k in pb.data.Ingredients]) - (100 - pb.h_2_0)


class SiObjectivePulpConstruct(PulpConstruct):
    def build(self, pb):
        fe = pb.data.Ingredients_list[1]
        pb.prob += lpSum([pb.ingredient_vars[k] * check_nan(fe[k])
                          * (100 - check_nan(pb.data.H2O[k])) / 100
                          for k in pb.data.Ingredients]) - (100 - pb.h_2_0)

