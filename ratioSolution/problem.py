#!/usr/bin/env python
# -*- coding:utf-8 -*-
import logging
from collections import namedtuple

from gekko import GEKKO

from ratioSolution.construct import SubjectiveConstruct, VarConstruct, \
    VarGroupConstruct
from utils.config import APP_LOG_NAME
from utils.excelParse import ExcelParse
from utils.util import check_nan

logger = logging.getLogger(APP_LOG_NAME + "." + __name__)

'''
    最大支持114个变量（项目）,100+个元素
'''


class Problem:

    def __init__(self, excel_file="../data/template.xlsx", excel_data=None, excel_type='file', exclude=None):
        """
        初始化Problem，构建数据data。有两种方式，1、通过传入excel文件路径或文件内容；2、直接传入构建好的excel data
        :param excel_file: 构建data的第一种方式，excel文件路径或文件内容
        :param excel_data: 构建data的第二种方式，通过ExcelParse构建好的excel data
        :param excel_type: 指定使用哪种data构建方式，file或data
        :param exclude: 第一种方式构建data时，excel文件要略去的列
        """
        if excel_type == 'file':
            self.data = ExcelParse(excel_file=excel_file, exclude=exclude)
        elif excel_type == 'data':
            self.data = excel_data
        else:
            raise ValueError("Invalid excel_type. Expected one of: %s" % ['file', 'data'])
        self.prob = GEKKO(remote=False)  # Initialize gekko
        self.prob.options.SOLVER = 1  # APOPT is an MINLP solver
        # 构建变量字典 {'x1': GKVariable, 'x2': GKVariable, 'x3': GKVariable, ... , 'x9': GKVariable}
        self.ingredient_vars = {i: self.prob.Var(value=0, lb=0, ub=100) for i in self.data.Ingredients}
        self.h_2_0 = sum(self.ingredient_vars[k] * check_nan(self.data.H2O[k]) / 100 for k in self.data.Ingredients)
        self._constructs = {}
        self._init_constructs()

    def _init_constructs(self):
        # 目标函数self._constructs["objective"]在api处生成
        self._constructs["subjective"] = SubjectiveConstruct(self)
        self._constructs["var"] = VarConstruct(self)
        self._constructs["var_group"] = VarGroupConstruct(self)

    def build(self):
        for i in ["objective", "subjective", "var", "var_group", "custom"]:
            if self._constructs.get(i):
                self._constructs.get(i).build()

    def add_construct(self, name, custom):
        self._constructs[name] = custom

    def remove_construct(self, *keys):
        self._constructs = {k: v for k, v in self._constructs.items() if k not in keys}

    def solve(self, disp=True, debug=1, gui=False, **kwargs):
        self.prob.solve(disp, debug, gui, **kwargs)

    def print_solve(self):
        for k in self.data.Ingredients:
            print(self.data.Ingredients_names["var_" + k], "=", self.ingredient_vars[k].value)

    def get_ingredient_result(self):
        h_2_0 = sum(self.ingredient_vars[k].value[0] * check_nan(self.data.H2O[k]) / 100 for k in self.data.Ingredients)
        return [sum(self.ingredient_vars[k].value[0] * check_nan(Element[k]) * (100 - check_nan(self.data.H2O[k]))
                    / 100 for k in self.data.Ingredients) / (100 - h_2_0) for Element in self.data.Ingredients_list]

    def get_price(self):
        dry_price = sum(check_nan(self.data.Cost[k]) * self.ingredient_vars[k].value[0]
                        * (1 - check_nan(self.data.H2O[k]) / 100) / 100 for k in self.data.Ingredients)
        h20_per = sum(
            self.ingredient_vars[k].value[0] * check_nan(self.data.H2O[k]) / 100 for k in self.data.Ingredients)
        ss_per = sum(check_nan(self.data.SS[k]) * self.ingredient_vars[k].value[0]
                     * (1 - check_nan(self.data.H2O[k]) / 100) / 100 for k in self.data.Ingredients) / (
                         1 - h20_per / 100)
        wet_price = dry_price / (1 - h20_per / 100)
        obj_price = wet_price / (1 - ss_per / 100)

        Prices = namedtuple("Prices", ['dry_price', 'wet_price', 'obj_price'])
        return Prices(dry_price=dry_price, wet_price=wet_price, obj_price=obj_price)

    def get_objfcnval(self):
        return self.prob.options.objfcnval

    def get_result(self):
        """
        result:配比结果list 如[1,2,3,4,5]
        names:配比物料名称list 如[巴西粗粉,高品澳粉,高返,过筛镍矿]
        """
        return [self.ingredient_vars[k].value[0] for k in self.data.Ingredients]

    def write_to_excel(self, excel_file=None):
        # 配比计算成分 成本计算
        result = [self.ingredient_vars[k].value[0] for k in self.data.Ingredients]
        name_result = [self.data.Ingredients_names["var_" + k] + "="
                       + str(self.ingredient_vars[k].value) for k in self.data.Ingredients]

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
