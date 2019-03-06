#!/usr/bin/env python
# -*- coding:utf-8 -*-
import math
from collections import namedtuple

import pandas as pd


class ExcelParse:
    def __init__(self, excel_file, exclude=None):
        """
        1. Ingredients: 配料标号 （项目列）
            <list>: ['x1', 'x2', 'x3', 'x4', 'x5', 'x6', 'x7', 'x8', 'x9']
        2. Ingredients_names: 配料名称 (项目列)
            <dict>: {'var_x1': '巴西粗粉', 'var_x2': '高品澳粉', 'var_x3': '高返', 'var_x4': '过筛镍矿', 'var_x5': '塞拉利昂粉', 'var_x6': 'FMG低品澳粉', 'var_x7': '铁泥', 'var_x8': '干渣粉', 'var_x9': '重力除尘灰'}
        3. Ingredients_list: 每个元素list，配料对应的元素含量 (n个元素列)
            <list>:
            [
            {'x1': 59.95, 'x2': 61.5, 'x3': 52, 'x4': 49.15, 'x5': 57.8, 'x6': 57.87, 'x7': 51.9, 'x8': 24, 'x9': 34.5, 'down': 55.9, 'up': 63},
            {'x1': 11.55, 'x2': 2.5, 'x3': 5.5, 'x4': 4.3, 'x5': 1.75, 'x6': 5.71, 'x7': 2.3, 'x8': 10, 'x9': 6.1525, 'down': 4.5, 'up': 5.5},
            {'x1': 0.01, 'x2': 0.11, 'x3': 11.5, 'x4': 0.06, 'x5': 0.01, 'x6': 0.01, 'x7': 9, 'x8': 40, 'x9': 0.65, 'down': 0, 'up': 4},
            {'x1': 0.02, 'x2': 0.08, 'x3': 3, 'x4': 0.9, 'x5': 0, 'x6': 0.01, 'x7': 2.95, 'x8': 8, 'x9': 0.29, 'down': 0, 'up': 1},
            {'x1': 0.98, 'x2': 2, 'x3': 3.1, 'x4': 5.65, 'x5': 6.78, 'x6': 2.21, 'x7': 0.68, 'x8': 3.5, 'x9': 2.93, 'down': 0, 'up': 3},
            {'x1': 0, 'x2': nan, 'x3': 0.29, 'x4': 0, 'x5': nan, 'x6': nan, 'x7': 1.11, 'x8': 0, 'x9': 0.44, 'down': 0, 'up': 0.3},
            {'x1': 0.05, 'x2': 0.03, 'x3': 0.068, 'x4': 0.036, 'x5': 0.085, 'x6': 0.05, 'x7': 0.087, 'x8': 0.62, 'x9': 0.037, 'down': 0, 'up': 0.1},
            {'x1': nan, 'x2': nan, 'x3': 0.01, 'x4': 2.06, 'x5': 0, 'x6': nan, 'x7': 0, 'x8': 0, 'x9': nan, 'down': 0, 'up': 0.18}
            ]
        4. Ingredients_list_name_index: 元素list，元素名称和对应的index (元素名称行)
            <dict>: {'tfe': 0, 'sio2': 1, 'cao': 2, 'mgo': 3, 'al2o3': 4, 'mno': 5, 'p': 6, 'cr': 7}
        5. Cost: 配料对应的价格 (价格列)
            <dict>: {'x1': 566.5, 'x2': 600.5, 'x3': 500, 'x4': 431.41, 'x5': 498.01, 'x6': 466.84, 'x7': 500, 'x8': 100, 'x9': 500, 'down': nan, 'up': nan}
        6. H2O: 配料对应的水含量 (H2O列)
            <dict>: {'x1': 6, 'x2': 7.3, 'x3': 0, 'x4': 31.5, 'x5': 11.12, 'x6': 8, 'x7': 20, 'x8': 6, 'x9': 2.49, 'down': nan, 'up': nan}
        7. UP: 配料对应的配比最高上限要求 (上限列)
            <dict>: {'x1': 15, 'x2': 15, 'x3': 12.5, 'x4': 15, 'x5': 20, 'x6': 40, 'x7': 0.6, 'x8': 2.5, 'x9': 0.57, 'down': nan, 'up': nan}
        8. Down:配料对应的配比最低下限要求 (下限列)
            <dict>: {'x1': 8, 'x2': 8, 'x3': 12.5, 'x4': 8, 'x5': 8, 'x6': 30, 'x7': 0.6, 'x8': 2.5, 'x9': 0.57, 'down': nan, 'up': nan}
        9. Group: 配料的分组情况 (分组列)
            <dict>: {1: ['x1', 'x3'], 2: ['x2', 'x5'], 3: ['x8', 'x9']}
        10. Group_down: 配料的分组配比下限 (分组下限列)
            <dict>: {'x1': 8, 'x2': 9, 'x3': 8, 'x4': nan, 'x5': 9, 'x6': nan, 'x7': nan, 'x8': 2.5, 'x9': 2.5, 'down': nan, 'up': nan}
        11. Group_up: 配料的分组配比上限 (分组上限列)
            <dict>: {'x1': 15, 'x2': 10, 'x3': 15, 'x4': nan, 'x5': 10, 'x6': nan, 'x7': nan, 'x8': 3, 'x9': 3, 'down': nan, 'up': nan}
        12. SS: 配料对应的烧损 (烧损列)
            <dict>: {'x1': 2.63, 'x2': 6, 'x3': 1, 'x4': 13.63, 'x5': 9.5, 'x6': 9, 'x7': 4.36, 'x8': 2, 'x9': 31.3, 'down': nan, 'up': nan}
        13. Grain_size_small: 配料对应的<0.25mm粒级 (<0.25mm列)
            <dict>: {'x1': 20, 'x2': 10, 'x3': 23, 'x4': 12, 'x5': 12, 'x6': 13, 'x7': 25, 'x8': 30, 'x9': 30, 'down': nan, 'up': nan}
        14. Grain_size_large: 配料对应的>1.00mm粒级 (>1.00mm列)
            <dict>: {'x1': 50, 'x2': 59, 'x3': 44, 'x4': 43, 'x5': 56, 'x6': 42, 'x7': 52, 'x8': 45, 'x9': 44, 'down': nan, 'up': nan}
        15. Grain_size_restrict: 配料对应的粘附比,计算公式为 <0.25mm/>1.00mm;只用到up和down上下限约束数据 (粘附比列)
            <dict>: {'x1': 0.4, 'x2': 0.1, 'x3': 0.5, 'x4': 0.2, 'x5': 0.2, 'x6': 0.3, 'x7': 0.4, 'x8': 0.6, 'x9': 0.6, 'down': 0.2, 'up': 0.4}

        :param exclude: 不读哪列，默认不读'配比'列
        """
        if exclude is None:
            exclude = {"配比"}
        self._var_nums = None  # int, 模板中#所在的行标号,在read_vars方法中初始化
        self.excel_file = excel_file
        self._sheet = pd.read_excel(self.excel_file, skiprows=1)
        var = self.read_vars(exclude)
        self.Ingredients = var.ingredients
        self.Ingredients_names = var.ingredients_names
        self.Ingredients_list = var.ingredients_list
        self.Ingredients_list_name_index = var.ingredients_list_name_index
        self.Cost = var.cost
        self.H2O = var.h2_o
        self.UP = var.up
        self.Down = var.down
        self.Group = var.group
        self.Group_down = var.group_down
        self.Group_up = var.group_up
        self.SS = var.ss
        self.Grain_size_small = var.grain_size_small
        self.Grain_size_large = var.grain_size_large
        self.Grain_size_restrict = var.grain_size_restrict

    def read_vars(self, exclude):
        Vars = namedtuple("Vars",
                          ['ingredients', 'ingredients_names', 'ingredients_list', 'ingredients_list_name_index',
                           'cost', 'h2_o', 'up', 'down', 'group', 'group_down', 'group_up', 'ss',
                           'grain_size_small', 'grain_size_large', 'grain_size_restrict'])

        column1 = self._sheet["项目"]
        self._var_nums = column1[column1 == "#"].index[0]

        ingredients = ["x" + str(i + 1) for i in range(self._var_nums)]
        ingredients_names = {}

        ingredients_list = []
        ingredients_list_name_index = {}
        index = 0

        cost = {}
        h2_o = {}
        up = {}
        down = {}
        group = {}
        group_down = {}
        group_up = {}
        ss = {}
        grain_size_small = {}
        grain_size_large = {}
        grain_size_restrict = {}
        var_list_names = ["var_x" + str(i + 1) for i in range(self._var_nums)]
        var_list_items = ingredients.copy()
        var_list_items.append("down")
        var_list_items.append("up")
        for r in self._sheet.iteritems():
            if r[0] == "项目":
                ingredients_names = dict(zip(var_list_names, r[1][0:self._var_nums]))
            elif r[0] == "分组":
                for t in zip(ingredients, r[1][0:self._var_nums]):
                    if not math.isnan(t[1]):
                        if group.get(t[1]):
                            group[t[1]].append(t[0])
                        else:
                            group[t[1]] = [t[0]]
            else:
                dic = dict(zip(var_list_items, r[1][0:self._var_nums]
                               .append(r[1][[self._var_nums + 1, self._var_nums + 2]])))
                if r[0] == "H2O":
                    h2_o = dic
                elif r[0] == "烧损":
                    ss = dic
                elif r[0] == "<0.25mm":
                    grain_size_small = dic
                elif r[0] == ">1.00mm":
                    grain_size_large = dic
                elif r[0] == "粘附比":
                    grain_size_restrict = dic
                elif r[0] == "价格":
                    cost = dic
                elif r[0] == "下限":
                    down = dic
                elif r[0] == "上限":
                    up = dic
                elif r[0] == "分组下限":
                    group_down = dic
                elif r[0] == "分组上限":
                    group_up = dic
                elif r[0] not in exclude:
                    ingredients_list.append(dic)
                    ingredients_list_name_index[r[0].lower()] = index
                    index += 1

        return Vars(
            ingredients=ingredients,
            ingredients_names=ingredients_names,
            ingredients_list=ingredients_list,
            ingredients_list_name_index=ingredients_list_name_index,
            cost=cost,
            h2_o=h2_o,
            up=up,
            down=down,
            group=group,
            group_down=group_down,
            group_up=group_up,
            ss=ss,
            grain_size_small=grain_size_small,
            grain_size_large=grain_size_large,
            grain_size_restrict=grain_size_restrict
        )

    def write_ingredient_result(self, result):
        result.insert(0, "混合料")
        for i in range(len(self._sheet.columns) - len(result)):
            result.append(None)
        self._sheet.loc[self._var_nums + 4] = result

    def write_solves(self, result, name_result):
        self._sheet["配比"] = pd.Series(result)
        self._sheet["计算结果"] = pd.Series(name_result)

    def write_to_excel(self, excel_file=None, prices=None):
        if excel_file is None:
            excel_file = "../data/result.xlsx"
        writer = pd.ExcelWriter(excel_file, engine='xlsxwriter')
        self._sheet.to_excel(writer, sheet_name='result')

        workbook = writer.book
        cell_format = workbook.add_format({'bold': True, 'font_color': 'red'})
        worksheet = writer.sheets['result']
        # cell_format.set_num_format('0.000')
        i = list(self._sheet.columns).index("配比") + 1
        j = list(self._sheet.columns).index("价格") + 1
        worksheet.set_column(first_col=i, last_col=i, cell_format=cell_format)
        worksheet.set_row(row=self._var_nums + 5, cell_format=cell_format)
        if prices:
            worksheet.write(self._var_nums + 2, j + 1, '价格', cell_format)
            worksheet.write(self._var_nums + 2, j, prices.dry_price, cell_format)
            worksheet.write(self._var_nums + 3, j + 1, '扣水', cell_format)
            worksheet.write(self._var_nums + 3, j, prices.wet_price, cell_format)
            worksheet.write(self._var_nums + 4, j + 1, '扣水烧损', cell_format)
            worksheet.write(self._var_nums + 4, j, prices.obj_price, cell_format)

        writer.save()
