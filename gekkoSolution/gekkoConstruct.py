#!/usr/bin/env python
# -*- coding:utf-8 -*-
import math

from gekkoSolution.customException import NotFoundError
from utils.logger import Logger
from utils.utils import check_nan, check_nan_or_zero

logger = Logger(__name__, log_file_path='../log/gekko_optimization.log').get()


# 多目标使用线性加权法
class GekkoConstruct:
    def __init__(self, optimization_problem):
        self.pb = optimization_problem

    def build(self):
        pass


class SubjectiveConstruct(GekkoConstruct):
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


class VarConstruct(GekkoConstruct):
    def build(self):
        for k in self.pb.data.Ingredients:
            if not math.isnan(self.pb.data.UP[k]):
                self.pb.prob.Equation(self.pb.ingredient_vars[k] <= self.pb.data.UP[k])
            if not math.isnan(self.pb.data.Down[k]):
                self.pb.prob.Equation(self.pb.ingredient_vars[k] >= self.pb.data.Down[k])


class VarGroupConstruct(GekkoConstruct):
    def build(self):
        for g in self.pb.data.Group.values():
            up = self.pb.data.Group_up[g[0]]
            down = self.pb.data.Group_down[g[0]]
            if not math.isnan(up):
                self.pb.prob.Equation(sum(self.pb.ingredient_vars[element] for element in g) <= up)
            if not math.isnan(down):
                self.pb.prob.Equation(sum(self.pb.ingredient_vars[element] for element in g) >= down)


# 以下为目标函数
class PriceObjectiveConstruct(GekkoConstruct):
    def __init__(self, optimization_problem):
        GekkoConstruct.__init__(self, optimization_problem)
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


class IngredientObjectiveConstruct(GekkoConstruct):
    def __init__(self, optimization_problem, ingredient_name, maximum=False):
        GekkoConstruct.__init__(self, optimization_problem)
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


class RObjectiveConstruct(GekkoConstruct):
    def __init__(self, optimization_problem, maximum=True):
        GekkoConstruct.__init__(self, optimization_problem)
        cao_index = self.pb.data.Ingredients_list_name_index.get('CaO'.lower())
        sio2_index = self.pb.data.Ingredients_list_name_index.get('SiO2'.lower())
        if cao_index is not None and sio2_index is not None:
            logger.info('finding cao_index is %s, sio2_index is %s', cao_index, sio2_index)

            cao_dic = self.pb.data.Ingredients_list[cao_index]
            sio2_dic = self.pb.data.Ingredients_list[sio2_index]
            r_dic = {
                i: 0 if check_nan_or_zero(cao_dic[i]) or check_nan_or_zero(sio2_dic[i]) else cao_dic[i] / sio2_dic[i]
                for i in self.pb.data.Ingredients
            }
            ingredient_per = sum(self.pb.ingredient_vars[k] * check_nan(r_dic[k])
                                 * (100 - check_nan(self.pb.data.H2O[k])) / 100
                                 for k in self.pb.data.Ingredients)
            # 最小值
            self._obj = ingredient_per / (100 - self.pb.h_2_0)
            if maximum:
                self._obj = -self._obj
        else:
            self._obj = 0
            logger.error('R=CaO/SiO2 obj failed! finding cao_index is %s, sio2_index is %s', cao_index, sio2_index)

    def get_obj(self):
        return self._obj


'''
    烧损，目标低烧损
'''


class SSObjectiveConstruct(GekkoConstruct):
    def __init__(self, optimization_problem, maximum=False):
        GekkoConstruct.__init__(self, optimization_problem)
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
class ObjectiveConstructBuilder(GekkoConstruct):
    def __init__(self, optimization_problem, *objectives):
        GekkoConstruct.__init__(self, optimization_problem)
        # 使用Intermediates分割函数，防止函数太长报错@error: Max Equation Length
        self._obj = sum(self.pb.prob.Intermediate(objective[0].get_obj() * objective[1]) for objective in objectives)

    def get_obj(self):
        return self._obj

    def build(self):
        self.pb.prob.Obj(self._obj)
