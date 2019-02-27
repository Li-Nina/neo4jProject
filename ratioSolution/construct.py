#!/usr/bin/env python
# -*- coding:utf-8 -*-
import logging
import math

from ratioSolution.customException import NotFoundError
from ratioSolution.util import cal_weights
from serverWeb.config import APP_LOG_NAME
from utils.utils import check_nan

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

        elements_list = self.pb.data.Ingredients_list.copy()
        elements_list.append(self.pb.data.SS)
        for Element in elements_list:
            ingredient_per = sum(self.pb.ingredient_vars[k] * check_nan(Element[k])
                                 * (100 - check_nan(self.pb.data.H2O[k])) / 100
                                 for k in self.pb.data.Ingredients)
            if not math.isnan(Element["down"]):
                self.pb.prob.Equation(ingredient_per >= Element["down"] * (100 - self.pb.h_2_0))
            if not math.isnan(Element["up"]):
                self.pb.prob.Equation(ingredient_per <= Element["up"] * (100 - self.pb.h_2_0))


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
        h20_per = sum(
            self.pb.ingredient_vars[k] * check_nan(self.pb.data.H2O[k]) / 100 for k in self.pb.data.Ingredients)
        ss_per = sum(check_nan(self.pb.data.SS[k]) * self.pb.ingredient_vars[k]
                     * (1 - check_nan(self.pb.data.H2O[k]) / 100) / 100 for k in self.pb.data.Ingredients) / (
                         1 - h20_per / 100)

        self._obj = (dry_price / (1 - h20_per / 100)) / (1 - ss_per / 100)

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
                                 * (100 - check_nan(self.pb.data.H2O[k])) / 100
                                 for k in self.pb.data.Ingredients)
            # 最小值
            self._obj = ingredient_per / (100 - self.pb.h_2_0)
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
        weight = cal_weights(optimization_problem, CaO=1, SiO2=1)
        self._obj = cao * weight['cao'] + sio2 * weight['sio2']

    def get_obj(self):
        return self._obj


'''
    烧损，目标低烧损
'''


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
