#!/usr/bin/env python
# -*- coding:utf-8 -*-
import logging
from logging.handlers import RotatingFileHandler


class LoggerHandler(object):

    def __init__(self, log_file_path=None):
        if not log_file_path:
            log_file_path = '../log/optimization.log'
        handler = RotatingFileHandler(log_file_path, mode='a', maxBytes=5 * 1024 * 1024,
                                      backupCount=20, encoding='utf-8', delay=0)
        formatter = logging.Formatter('%(asctime)s %(name)s %(module)s %(levelname)s = %(message)s')
        handler.setFormatter(formatter)
        handler.suffix = "%Y-%m-%d-%H-%M-%S.log"
        self._handler = handler

    def get(self):
        return self._handler
