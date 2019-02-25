#!/usr/bin/env python
# -*- coding:utf-8 -*-
import json
import logging
import time
import traceback
from collections import namedtuple
from flask import jsonify, request, Blueprint

from ratioSolution.construct import ObjectiveConstructBuilder, IngredientObjectiveConstruct
from ratioSolution.problem import Problem
from ratioSolution.utils import cal_weights
from serverWeb.config import APP_LOG_NAME
from utils.utils import number_scalar, convert_namedtuple, current_time_millis

MODEL_DICT = {}
ResponseJson = namedtuple("ResponseJson", ['status', 'msg', 'result', 'stamp'])

mod = Blueprint('ratioAlgorithm', __name__)
logger = logging.getLogger(APP_LOG_NAME + "." + __name__)


@mod.route('/')
def index():
    return 'ratioAlgorithm server .........'


@mod.route('/<database>')
def hello_world(database):
    log(database)
    return 'nlp classification server database {}.........'.format(database)


@mod.route('/<database>/single/<int:corpus_id>')
def classification_one(database, corpus_id):
    corpus_ids = request.args.get('id')
    space_id = request.args.get('spaceId')

    try:
        step = 0.001  # 循环计算步长
        iters = 5  # 循环次数

        start = time.time()

        lp = Problem()
        weights = cal_weights(lp, **{'TFe': 1, 'SiO2': 1, 'COST': 1, 'R': 1, 'SS': 1})
        # weights = cal_weights(lp, **{'COST': 1000, 'R': 1})
        # weights = cal_weights(lp, **{'R': 1})
        # weights = cal_weights(lp, **{'COST': 1})

        cao_index = lp.data.Ingredients_list_name_index.get('CaO'.lower())
        sio2_index = lp.data.Ingredients_list_name_index.get('SiO2'.lower())
        r_enable = False
        if cao_index is not None and sio2_index is not None:
            r_enable = True

        lp.remove_construct("objective")
        objectives = ObjectiveConstructBuilder(lp,
                                               # (PriceObjectiveConstruct(lp), weights['cost']),
                                               # (IngredientObjectiveConstruct(lp, ingredient_name="TFe", maximum=True),
                                               #  weights['tfe']),
                                               (IngredientObjectiveConstruct(lp, ingredient_name="SiO2", maximum=False),
                                                weights['sio2']),
                                               # (RObjectiveConstruct(lp), weights['r']),
                                               # (SSObjectiveConstruct(lp), weights['ss'])
                                               )
        lp.add_construct("objective", objectives)

        lp.build()

        lp.prob.options.IMODE = 3  # steady state optimization

        objfcn = objectives.get_obj()  # 目标函数公式
        objfcnval = None  # 上一次目标函数计算值
        for i in range(iters):
            if objfcnval is not None:  # 防止objfcnval为0，不写if objfcnval
                obj_scalar = number_scalar(objfcnval)
                lp.prob.Equation(objfcn >= objfcnval + step * obj_scalar)
                print("objfcn >= {0} + {1} = {2}".format(objfcnval, step * obj_scalar,
                                                         objfcnval + step * obj_scalar))

            # Solve simulation
            lp.solve(disp=True)

            lp.print_solve()
            print(lp.get_price())
            ingredient_result = lp.get_ingredient_result()
            print(ingredient_result)
            if r_enable:
                print("R = ", ingredient_result[cao_index] / ingredient_result[sio2_index])  # 碱度R=CaO/SiO2，目标高碱度
            print("objfcnval ============================================================> ", lp.get_objfcnval())

            if objfcnval is None:  # 最优结果
                lp.write_to_excel()

            objfcnval = lp.get_objfcnval()
            lp.write_to_excel("../data/results/result" + str(i) + ".xlsx")

        end = time.time()
        logger.info("gekko_optimization task run successfully, runtime  is %s s:", end - start)
    except Exception as e:
        print(repr(e))
        logger.error(traceback.format_exc())

    log('single classification done! insert_id is {}'.format(1))
    return jsonify(convert_namedtuple(ResponseJson(status=0,
                                                   msg='OK,using model {}'.format('sss'),
                                                   result=json.dumps('sss'),
                                                   stamp=current_time_millis()
                                                   )))


def __empty_model_error():
    return jsonify(convert_namedtuple(ResponseJson(status=1,
                                                   msg='ERROR! model must be trained first!',
                                                   result='ERROR!',
                                                   stamp=current_time_millis()
                                                   )))


def log(msg: str or dict = None):
    """
    :param msg: string 或 字典 {**logs, **msg_dict, **msg_str_dict}为字典合并写法
    :return:
    """
    if msg:
        if isinstance(msg, str):
            msg_dict = {'msg': msg}
        elif isinstance(msg, dict):
            msg_dict = msg
        else:
            msg_dict = {'msg': str(msg)}
    else:
        msg_dict = {}
    logger.info(json.dumps(msg_dict))
