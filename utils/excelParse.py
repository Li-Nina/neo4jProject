#!/usr/bin/env python
# -*- coding:utf-8 -*-
import math
from collections import namedtuple

import pandas as pd


class ExcelParse:
    def __init__(self, excel_file, exclude=None):
        if exclude is None:
            exclude = {"配比"}
        self._var_nums = None
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

    def read_vars(self, exclude):
        Vars = namedtuple("Vars",
                          ['ingredients', 'ingredients_names', 'ingredients_list', 'ingredients_list_name_index',
                           'cost', 'h2_o', 'up', 'down', 'group', 'group_down', 'group_up', 'ss'])

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
            ss=ss
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
