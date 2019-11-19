#!/usr/bin/env python
# -*- coding:utf-8 -*-
import csv
import logging
# from serverWeb.esRepository import searchExpert
import os.path

from flask import request, Flask, jsonify
from jieba.analyse.analyzer import ChineseAnalyzer
from whoosh.fields import *
from whoosh.index import create_in
from whoosh.index import open_dir
from whoosh.qparser import MultifieldParser

from config import INDEX_PATH
from serverWeb.esRepository import get_data_by_body
from serverWeb.repository import getExpertsNodeList
from utils.util import fetchEduAndMajor


def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    return response


app = Flask(__name__, static_url_path='')
app.config['JSON_AS_ASCII'] = False  # jsonify返回的json串支持中文显示
app.after_request(after_request)

logger = logging.getLogger(__name__)


@app.route("/")
def get_index():
    return app.send_static_file('index.html')


@app.route("/expert", methods=['GET', 'POST'])
def expertsAndFiled():
    inputs = request.values.get('input')
    if not inputs:
        return jsonify([])
    f = fetchEduAndMajor(inputs)
    logger.warning(">>>>>>>>>>>>>>> 学历:" + f.get('edu', 'NONE') + "... 专业:" + f.get('major', 'NONE'))

    if 'edu' not in f or 'major' not in f:
        return jsonify([])
    rst = []
    results = getExpertsNodeList(f['edu'], f['major'])
    print(results)
    for record in results:
        exp = {**{"id": record["experts"].id}, **{"expert_ID": record["experts"]["Expert_ID"]},
               **dict(record["experts"].items())}
        exp.pop("Expert_ID")
        rst.append({"experts": exp, "field": {**{"id": record["field"].id}, **dict(record["field"].items())}})

    return jsonify(rst)


@app.route("/essearch", methods=['GET', 'POST'])
def esSearcher():
    inputs = request.values.get('input')
    if not inputs:
        return jsonify([])
    path = INDEX_PATH + "experts"
    ix = open_dir(path)
    with ix.searcher() as searcher:
        # parser = QueryParser("project", schema=ix.schema)
        mparser = MultifieldParser(["project", "filed", "degree", "college", "subject"], schema=ix.schema)
        # keyword = parser.parse("863计划")  # 构造查询语句
        keyword = mparser.parse(inputs)  # 构造查询语句
        results = searcher.search(keyword, limit=10)
        res = []
        for result in results:
            res.append(dict(result))
        return jsonify(res)


@app.route("/create_index", methods=['GET', 'POST'])
def create_index():
    analyzer = ChineseAnalyzer()
    schema = Schema(name=ID(stored=True, unique=True), college=TEXT(stored=True, analyzer=analyzer),
                    education=TEXT(stored=True, analyzer=analyzer), degree=TEXT(stored=True, analyzer=analyzer),
                    job=TEXT(stored=True, analyzer=analyzer), subject=TEXT(stored=True, analyzer=analyzer),
                    research=TEXT(stored=True, analyzer=analyzer), department=TEXT(stored=True, analyzer=analyzer),
                    title=TEXT(stored=True, analyzer=analyzer), filed=TEXT(stored=True, analyzer=analyzer),
                    project=TEXT(stored=True, analyzer=analyzer))  # 声明索引模式
    path = INDEX_PATH + "experts"

    if not os.path.exists(path):
        os.mkdir(path)
    ix = create_in(path, schema)
    writer = ix.writer()

    csv_file = open('data/con_experts_pro.csv', 'r', encoding="utf-8")
    data = csv.reader(csv_file)
    for i in data:
        writer.add_document(
            name=i[2],
            college=i[3], education=i[4],
            degree=i[5], job=i[6],
            subject=i[8], research=i[11],
            department=i[12], title=i[13],
            filed=i[15], project=i[16]
        )
    writer.commit()
    return "success"


# @app.route("/es_my_delete_index", methods=['GET', 'POST'])
# def es_my_delete_index():
#     delete_index()
#     return "success"
#
#
# @app.route("/es_my_create_index", methods=['GET', 'POST'])
# def es_my_create_index():
#     create_indexs_es()
#     index_data_from_csv('../data/con_experts_pro.csv')
#     return "success"


@app.route("/es_my_get_data", methods=['GET', 'POST'])
def es_my_get_data():
    inputs = request.values.get('input')
    if not inputs:
        return jsonify([])
    rst = get_data_by_body(inputs)
    return jsonify(rst['hits']['hits'])
