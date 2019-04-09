#!/usr/bin/env python
# -*- coding:utf-8 -*-
import logging
import math

from ratioSolution.customException import NotFoundError
from ratioSolution.util import cal_weights
from utils.config import APP_LOG_NAME
from utils.util import check_nan

logger = logging.getLogger(APP_LOG_NAME + "." + __name__)


# 多目标使用线性加权法
class Construct:
    def __init__(self, optimization_problem):
        self.pb = optimization_problem

    def build(self):
        pass


class SubjectiveConstruct(Construct):
    def build(self):
        self.pb.prob.Equation(sum(self.pb.ingredient_vars[k] for k in self.pb.data.Ingredients) == 100)
        # 烧损和水没有上下限限制,只计算其他元素上下限限制 ->20190339经博士确认
        elements_list = self.pb.data.Ingredients_list.copy()
        for Element in elements_list:
            ingredient_per = sum(self.pb.ingredient_vars[k] * check_nan(Element[k])
                                 * (100 - check_nan(self.pb.data.H2O[k]))
                                 for k in self.pb.data.Ingredients)
            if not math.isnan(Element["down"]):
                self.pb.prob.Equation(ingredient_per >= Element["down"] * (100 - self.pb.h_2_0) * (100 - self.pb.s_s))
            if not math.isnan(Element["up"]):
                self.pb.prob.Equation(ingredient_per <= Element["up"] * (100 - self.pb.h_2_0) * (100 - self.pb.s_s))


# todo
class IngredientsFixed(Construct):
    def __init__(self, optimization_problem, ingredient_name, maximum=False):
        Construct.__init__(self, optimization_problem)
        objfcnval = self.pb.get_objfcnval()
        print("mememe * ->", objfcnval)

        index = self.pb.data.Ingredients_list_name_index.get(ingredient_name.lower())
        ingredient = self.pb.data.Ingredients_list[index]
        ingredient_per = sum(self.pb.ingredient_vars[k] * check_nan(ingredient[k])
                             * (100 - check_nan(self.pb.data.H2O[k]))
                             for k in self.pb.data.Ingredients)
        self.pb.prob.Equation(ingredient_per == abs(objfcnval) * (100 - self.pb.h_2_0) * (100 - self.pb.s_s))
        # print("*******1->>", self.pb._objectives)
        self.pb.prob.Obj(PriceObjectiveConstruct(self.pb).get_obj())
        # print("*******2->>", self.pb._objectives)


class SubjectiveGrainSizeConstruct(Construct):
    def build(self):
        grain_size_small_per = sum(self.pb.ingredient_vars[k] * check_nan(self.pb.data.Grain_size_small[k])
                                   * (1 - check_nan(self.pb.data.H2O[k]) / 100)
                                   for k in self.pb.data.Ingredients) / 10000
        grain_size_large_per = sum(self.pb.ingredient_vars[k] * check_nan(self.pb.data.Grain_size_large[k])
                                   * (1 - check_nan(self.pb.data.H2O[k]) / 100)
                                   for k in self.pb.data.Ingredients) / 10000
        grain_size = grain_size_small_per / grain_size_large_per
        if not math.isnan(self.pb.data.Grain_size_restrict["down"]):
            self.pb.prob.Equation(grain_size >= self.pb.data.Grain_size_restrict["down"])
        if not math.isnan(self.pb.data.Grain_size_restrict["up"]):
            self.pb.prob.Equation(grain_size <= self.pb.data.Grain_size_restrict["up"])


class VarConstruct(Construct):
    def build(self):
        for k in self.pb.data.Ingredients:
            if not math.isnan(self.pb.data.UP[k]):
                self.pb.prob.Equation(self.pb.ingredient_vars[k] <= self.pb.data.UP[k])
            if not math.isnan(self.pb.data.Down[k]):
                self.pb.prob.Equation(self.pb.ingredient_vars[k] >= self.pb.data.Down[k])


class VarGroupConstruct(Construct):
    def build(self):
        for g in self.pb.data.Group.values():
            up = self.pb.data.Group_up[g[0]]
            down = self.pb.data.Group_down[g[0]]
            if not math.isnan(up):
                self.pb.prob.Equation(sum(self.pb.ingredient_vars[element] for element in g) <= up)
            if not math.isnan(down):
                self.pb.prob.Equation(sum(self.pb.ingredient_vars[element] for element in g) >= down)


# 以下为目标函数
'''
    成本最低
'''


class PriceObjectiveConstruct(Construct):
    def __init__(self, optimization_problem):
        Construct.__init__(self, optimization_problem)
        dry_price = sum(check_nan(self.pb.data.Cost[k]) * self.pb.ingredient_vars[k]
                        * (1 - check_nan(self.pb.data.H2O[k]) / 100) / 100 for k in self.pb.data.Ingredients)
        self._obj = (dry_price / (1 - self.pb.h_2_0 / 100)) / (1 - self.pb.s_s / 100)

    def get_obj(self):
        return self._obj


'''
    对应某个元素求混合料该元素的最大目标或最小目标
    :param ingredient_name:元素名称，如TFe，SiO2，Al2O3
'''


class IngredientObjectiveConstruct(Construct):
    def __init__(self, optimization_problem, ingredient_name, maximum=False):
        Construct.__init__(self, optimization_problem)
        index = self.pb.data.Ingredients_list_name_index.get(ingredient_name.lower())
        if index is not None:
            ingredient = self.pb.data.Ingredients_list[index]
            ingredient_per = sum(self.pb.ingredient_vars[k] * check_nan(ingredient[k])
                                 * (100 - check_nan(self.pb.data.H2O[k]))
                                 for k in self.pb.data.Ingredients)
            # 最小值
            self._obj = ingredient_per / ((100 - self.pb.h_2_0) * (100 - self.pb.s_s))
            if maximum:
                self._obj = -self._obj
        else:
            logger.error('ingredients ' + ingredient_name.lower() + ' not found!')
            raise NotFoundError('ingredients ' + ingredient_name.lower() + ' not found!')

    def get_obj(self):
        return self._obj


'''
    碱度R=CaO/SiO2，目标高碱度
'''


class RObjectiveConstruct(Construct):
    def __init__(self, optimization_problem):
        Construct.__init__(self, optimization_problem)
        cao = self.pb.prob.Intermediate(
            IngredientObjectiveConstruct(optimization_problem, 'CaO', maximum=True).get_obj())
        sio2 = self.pb.prob.Intermediate(
            IngredientObjectiveConstruct(optimization_problem, 'SiO2', maximum=False).get_obj())
        weight = cal_weights(optimization_problem.data, CaO=1, SiO2=1)
        self._obj = cao * weight['cao'] + sio2 * weight['sio2']

    def get_obj(self):
        return self._obj


'''
    烧损，目标低烧损
'''


# todo
class SSObjectiveConstruct(Construct):
    def __init__(self, optimization_problem, maximum=False):
        Construct.__init__(self, optimization_problem)
        ingredient_per = sum(self.pb.ingredient_vars[k] * check_nan(self.pb.data.SS[k])
                             * (100 - check_nan(self.pb.data.H2O[k])) / 100
                             for k in self.pb.data.Ingredients)
        # 最小值
        self._obj = ingredient_per / (100 - self.pb.h_2_0)
        if maximum:
            self._obj = -self._obj

    def get_obj(self):
        return self._obj


# 目标函数生成器，传入多个目标与权重的元组 eg:(obj1,0.5),(obj2,0.3),(obj3,0.2)
class ObjectiveConstructBuilder(Construct):
    def __init__(self, optimization_problem, *objectives):
        Construct.__init__(self, optimization_problem)
        # 使用Intermediates分割函数，防止函数太长报错@error: Max Equation Length
        self._obj = sum(self.pb.prob.Intermediate(objective[0].get_obj() * objective[1]) for objective in objectives)

    def get_obj(self):
        return self._obj

    def build(self):
        self.pb.prob.Obj(self._obj)
