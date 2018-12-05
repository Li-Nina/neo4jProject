#!/usr/bin/env python
# -*- coding:utf-8 -*-
from collections import namedtuple

from pulp import *

from pulpSolution.pulpConstruct import ObjectivePulpConstruct, SubjectivePulpConstruct, VarPulpConstruct, \
    VarGroupPulpConstruct
from utils.excelParse import ExcelParse
from utils.logger import Logger
from utils.utils import check_nan

logger = Logger(__name__, log_file_path='../log/pulp_optimization.log').get()


class PulpProblem:

    def __init__(self, excel_file="../data/template.xlsx", exclude=None, name="The Optimization Problem"):
        self.data = ExcelParse(excel_file=excel_file, exclude=exclude)
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
        dry_price = sum(check_nan(self.data.Cost[k]) * self.ingredient_vars[k].value()
                        * (1 - check_nan(self.data.H2O[k]) / 100) / 100 for k in self.data.Ingredients)
        h20_per = sum(self.ingredient_vars[k].value() * self.data.H2O[k] / 100 for k in self.data.Ingredients)
        ss_per = sum(check_nan(self.data.SS[k]) * self.ingredient_vars[k].value()
                     * (1 - check_nan(self.data.H2O[k]) / 100) / 100 for k in self.data.Ingredients) / (
                         1 - h20_per / 100)
        wet_price = dry_price / (1 - h20_per / 100)
        obj_price = wet_price / (1 - ss_per / 100)

        Prices = namedtuple("Prices", ['dry_price', 'wet_price', 'obj_price'])
        return Prices(dry_price=dry_price, wet_price=wet_price, obj_price=obj_price)

    def get_objfcnval(self):
        return value(self.prob.objective)

    def write_to_excel(self, excel_file=None):
        if self.get_solve_status() == "Optimal":
            # 配比计算成分
            # 成本计算
            result = [self.ingredient_vars[k].value() for k in self.data.Ingredients]
            name_result = [self.data.Ingredients_names[self.ingredient_vars[k].name] + "="
                           + str(self.ingredient_vars[k].value()) for k in self.data.Ingredients]
            logger.info("optimization result is: " + str(result))
            logger.info("optimization name_result is: " + str(name_result))
            self.data.write_solves(result, name_result)

            # 混合料计算成分
            ingredient_result_list = self.get_ingredient_result()
            prices = self.get_price()

            logger.info("optimization ingredient_result_list is: " + str(ingredient_result_list))
            logger.info("optimization prices is: " + str(prices))
            self.data.write_ingredient_result(ingredient_result_list)
            self.data.write_to_excel(excel_file, prices)
        else:
            raise Exception("Solution Not Found!")
