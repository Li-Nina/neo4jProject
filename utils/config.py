#!/usr/bin/env python
# -*- coding:utf-8 -*-

APP_LOG_NAME = 'flask.app'
LOG_PATH = "./log/ratioServer.log"
# LOG_PATH = "C:/Users/sun/PycharmProjects/optimizationproblem/log/ratioServer.log"
ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'xlsm', 'xltx', 'xltm', 'xlt', 'xml', 'xlam', 'xla', 'xlw', 'xlr'}
DIGIT = 2  # 除cost外，混合料元素、混合料其他优化条件(tfe,al2o3,sio2,ss,cr,r)要求的精度
DELTA = 0.0000000001
