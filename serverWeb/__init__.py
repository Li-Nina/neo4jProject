#!/usr/bin/env python
# -*- coding:utf-8 -*-

import logging

from flask.logging import default_handler

from serverWeb import ratioAlgorithm
from serverWeb.config import LOG_PATH
from serverWeb.logger import MyHandler


def config_loggers(flask_app):
    flask_app.logger.removeHandler(default_handler)  # app.logger name = 'flask.app'
    flask_app.logger.handlers = []
    flask_app.logger.addHandler(MyHandler(log_file_path=LOG_PATH, use_url_formatter=True).get())
    flask_app.logger.setLevel(logging.INFO)


from flask import Flask

app = Flask(__name__)
config_loggers(app)

app.register_blueprint(ratioAlgorithm.mod, url_prefix='/algo/ratioAlgorithm')
