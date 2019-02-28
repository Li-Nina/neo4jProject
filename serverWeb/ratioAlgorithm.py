#!/usr/bin/env python
# -*- coding:utf-8 -*-
import json
import logging
import traceback
from collections import namedtuple

from flask import jsonify, request, Blueprint
from utils.config import APP_LOG_NAME
from utils.util import convert_namedtuple, current_time_millis, allowed_file

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


@mod.route('/hello_world_file/<database>')
def hello_world_file(database):
    log(database)
    try:
        file = request.files['file']
        if file and allowed_file(file.filename):
            step = 0.001  # 循环计算步长
            iters = 5  # 循环次数
    except Exception as e:
        print(repr(e))
        logger.error(traceback.format_exc())
        return jsonify(convert_namedtuple(ResponseJson(status=1,
                                                       msg='OK,using model {}'.format('sss'),
                                                       result=str(e),
                                                       stamp=current_time_millis()
                                                       )))

    return 'nlp classification server database {}.........'.format(database)


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
