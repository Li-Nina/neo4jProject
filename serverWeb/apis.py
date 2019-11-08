#!/usr/bin/env python
# -*- coding:utf-8 -*-
import logging

from flask import request, Flask, jsonify

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
    print(inputs)
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
        exp = {**{"id": record["experts"].id, **{"expert_ID": record["experts"]["Expert_ID"]},
                  **dict(record["experts"].items())}}
        exp.pop("Expert_ID")
        rst.append({"experts": exp, "field": {**{"id": record["field"].id}, **dict(record["field"].items())}})

    return jsonify(rst)



from whoosh.index import create_in
from whoosh.fields import *
from jieba.analyse.analyzer import ChineseAnalyzer
import os.path
import csv
from whoosh.index import open_dir
from whoosh.qparser import QueryParser
from whoosh.qparser import MultifieldParser

def create_index():
    analyzer = ChineseAnalyzer()
    schema = Schema(name=ID(stored=True, unique=True), college=TEXT(stored=True, analyzer=analyzer),
                    education=TEXT(stored=True, analyzer=analyzer),degree=TEXT(stored=True, analyzer=analyzer),
                    job=TEXT(stored=True, analyzer=analyzer),subject=TEXT(stored=True, analyzer=analyzer),
                    research=TEXT(stored=True, analyzer=analyzer),department=TEXT(stored=True, analyzer=analyzer),
                    title=TEXT(stored=True, analyzer=analyzer),filed=TEXT(stored=True, analyzer=analyzer),
                    project=TEXT(stored=True, analyzer=analyzer))  # 声明索引模式
    if not os.path.exists("index"):
        os.mkdir("index")
    ix = create_in("index", schema)
    writer = ix.writer()

    csv_file = open('F:/con_experts_pro_3.csv', 'r',encoding="utf-8")
    data = csv.reader(csv_file)
    for i in data:
        # print(i)
        writer.add_document(
            name=i[2],
            college=i[3], education=i[4],
            degree=i[5], job=i[6],
            subject=i[8], research=i[11],
            department=i[12], title=i[13],
            filed=i[15], project=i[16]
        )


    writer.commit()
# create_index = create_index()
# if not os.path.exists("index"):  # 查询时没有索引文件，需先创建索引文件
#     create_index()
# ix = open_dir("index")  # 读取索引文件
create_index()
ix = open_dir("index")
with ix.searcher() as searcher:
    # parser = QueryParser("project", schema=ix.schema)
    mparser=MultifieldParser(["project", "filed", "degree","college","subject"],schema = ix.schema)
    # keyword = parser.parse("863计划")  # 构造查询语句
    keyword = mparser.parse("863计划 分布式 博士")  # 构造查询语句
    results = searcher.search(keyword, limit=10)
    res = []
    for result in results:
        print(dict(result))  # 打印查询结果
        res.append(dict(result))
    if not res:
        print("没有此内容！")


