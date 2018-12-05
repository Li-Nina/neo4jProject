#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging

from utils.loggerHandler import LoggerHandler


class Logger(object):

    def __init__(self, name, log_file_path=None):
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        logger.handlers = []
        logger.addHandler(LoggerHandler(log_file_path).get())
        self._logger = logger

    def get(self):
        return self._logger
