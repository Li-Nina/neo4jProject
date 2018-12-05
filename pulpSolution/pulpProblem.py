#!/usr/bin/env python
# -*- coding:utf-8 -*-

from pulp import *

from pulpSolution.pulpConstruct import ObjectivePulpConstruct, SubjectivePulpConstruct, VarPulpConstruct, \
    VarGroupPulpConstruct
from utils.ingredientsRead import IngredientsRead
from utils.utils import check_nan


class PulpProblem:

    def __init__(self, excel_file="../data/template.xlsx", exclude=None, name="The Optimization Problem"):
        self.data = IngredientsRead(excel_file=excel_file, exclude=exclude)
        self.prob = LpProblem(name, LpMinimize)
        # 构建Lp变量字典，变量名以var_开头，如var_x1，下界是0
        self.ingredient_vars = LpVariable.dicts("var", self.data.Ingredients, 0)
        self.h_2_0 = lpSum(
            [self.ingredient_vars[k] * check_nan(self.data.H2O[k]) / 100 for k in self.data.Ingredients])
        self._constructs = {}
        self._init_constructs()

    def _init_constructs(self):
        self._constructs["objective"] = ObjectivePulpConstruct()
        self._constructs["subjective"] = SubjectivePulpConstruct()
        self._constructs["var"] = VarPulpConstruct()
        self._constructs["var_group"] = VarGroupPulpConstruct()

    def build(self):
        for i in ["objective", "subjective", "var", "var_group", "custom"]:
            if self._constructs.get(i):
                self._constructs.get(i).build(self)

    def add_construct(self, name, custom):
        self._constructs[name] = custom

    def remove_construct(self, *keys):
        self._constructs = {k: v for k, v in self._constructs.items() if k not in keys}

    def solve(self):
        self.prob.solve()

    def get_solve_status(self):
        return LpStatus[self.prob.status]

    def print_solve(self):
        for k in self.data.Ingredients:
            print(self.data.Ingredients_names[self.ingredient_vars[k].name], "=", self.ingredient_vars[k].value())

    def get_ingredient_result(self):
        h_2_0 = lpSum([self.ingredient_vars[k].value() * check_nan(self.data.H2O[k])
                       / 100 for k in self.data.Ingredients])
        return [lpSum([self.ingredient_vars[k].value() * check_nan(Element[k]) * (100 - check_nan(self.data.H2O[k]))
                       / 100 for k in self.data.Ingredients]) / (100 - h_2_0)
                for Element in self.data.Ingredients_list]

    def get_price(self):
        return value(self.prob.objective)

    def write_to_excel(self, excel_file=None):
        if self.get_solve_status() == "Optimal":
            # 配比计算成分
            # 成本计算
            result = [self.ingredient_vars[k].value() for k in self.data.Ingredients]
            name_result = [self.data.Ingredients_names[self.ingredient_vars[k].name] + "="
                           + str(self.ingredient_vars[k].value()) for k in self.data.Ingredients]
            self.data.write_solves(result, name_result)

            # 混合料计算成分
            self.data.write_ingredient_result(self.get_ingredient_result())
            self.data.write_to_excel(excel_file, self.get_price())
        else:
            raise Exception("get_solve_status is not Optimal!")
