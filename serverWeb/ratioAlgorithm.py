#!/usr/bin/env python
# -*- coding:utf-8 -*-
import json
import logging
import traceback
from collections import namedtuple

from flask import jsonify, request, Blueprint

from ratioSolution.algorithmAPI import ratio_algorithm
from utils.config import APP_LOG_NAME
from utils.util import convert_namedtuple, allowed_file

MODEL_DICT = {}
ResponseJson = namedtuple("ResponseJson", ['status', 'msg', 'result'])

mod = Blueprint('ratioAlgorithm', __name__)
logger = logging.getLogger(APP_LOG_NAME + "." + __name__)


@mod.route('/')
def index():
    return 'ratioAlgorithm server .........'


@mod.route('/calculate', methods=['GET', 'POST'])
def ratio_algorithm_api():
    """
    @see https://zhuanlan.zhihu.com/p/23731819?refer=flask
    需要2个参数：
    1、(必有)file文件，excel模板，表单name=file
    2、(可选)POST传参，参数名data，格式json，json包含5个key
    {"top_n": 2, "steps": [0.1, 0.01], "custom_weights_list": [{"tfe": 1}, {"al2o3": 1}, {"tfe": 1, "Al2O3": 1}], "subjective_grain_size": 1, "var_group": 0}
    """
    try:
        file = request.files['file']
        if file and allowed_file(file.filename):
            # request.args获取GET请求参数，request.form获取POST表单数据，request.values获取所有数据
            data = request.values.get('data')
            data_dict = json.loads(data) if data else {}
            top_n = data_dict.get('top_n')
            steps = data_dict.get('steps')
            custom_weights_list = data_dict.get('custom_weights_list')

            _ctrl_dic = {'subjective_grain_size': data_dict.get('subjective_grain_size'),
                         'var_group': data_dict.get('var_group')}

            rst_list = ratio_algorithm(file, top_n=top_n, steps=steps, custom_weights_list=custom_weights_list,
                                       ctrl_constructs_dict=_ctrl_dic)
            return jsonify(convert_namedtuple(ResponseJson(status=0,
                                                           msg='ok',
                                                           result=rst_list
                                                           )))
    except Exception:
        logger.error(traceback.format_exc())
        return jsonify(convert_namedtuple(ResponseJson(status=1,
                                                       msg='ERROR! please check the parameters',
                                                       result={}
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
