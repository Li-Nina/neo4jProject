#!/usr/bin/python3
# -*- coding: utf-8 -*-
# author: 小马哥

import logging
from logging.handlers import RotatingFileHandler

from flask import request


class Logger(object):

    def __init__(self, name, log_file_path='./log/ratioServer.log'):
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        logger.handlers = []  # 在同一个python解释器下，getLogger name相同返回同一个logger
        logger.addHandler(MyHandler(log_file_path=log_file_path, use_addr_formatter=False).get())
        self._logger = logger

    def get(self):
        return self._logger


class MyHandler(object):

    def __init__(self, log_file_path=None, use_addr_formatter=False):
        if not log_file_path:
            log_file_path = './log/ratioServer.log'
        handler = RotatingFileHandler(log_file_path, mode='a', maxBytes=5 * 1024 * 1024,
                                      backupCount=20, encoding=None, delay=0)
        if use_addr_formatter:
            formatter = RequestFormatter('%(asctime)s %(remote_addr)s %(name)s %(levelname)s %(message)s')
            # formatter = RequestFormatter('%(asctime)s %(remote_addr)s requested %(url)s\n'
            #                              '%(name)s %(levelname)s %(message)s')
        else:
            formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
        handler.setFormatter(formatter)
        handler.suffix = "%Y-%m-%d-%H-%M-%S.log"
        self._handler = handler

    def get(self):
        return self._handler


class RequestFormatter(logging.Formatter):
    def format(self, record):
        if request:
            record.url = request.url
            record.remote_addr = request.remote_addr
        else:
            record.url = 'local'
            record.remote_addr = 'local'
        return super().format(record)
