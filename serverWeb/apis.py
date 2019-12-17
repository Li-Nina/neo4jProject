#!/usr/bin/env python
# -*- coding:utf-8 -*-
import csv
import logging
# from serverWeb.esRepository import searchExpert
import os.path
import jieba
import time
import os
from flask import request, Flask, jsonify
from jieba.analyse.analyzer import ChineseAnalyzer
from whoosh.fields import *
from whoosh.index import create_in
from whoosh.index import open_dir
from whoosh.qparser import MultifieldParser

from config import INDEX_PATH
from serverWeb.esRepository import get_data_by_body, create_indexs_es, index_data_from_csv, get_data_from_mysql, \
    import_index_data
# from serverWeb.repository import getExpertsNodeList
import json
from serverWeb.esRepository import es, my_index, my_doc_type, parse_excel,save_to_mysql
from utils.util import fetchEduAndMajor
from utils.util2 import fetchEduAndMajor_es

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


# @app.route("/expert", methods=['GET', 'POST'])
# def expertsAndFiled():
#     inputs = request.values.get('input')
#     if not inputs:
#         return jsonify([])
#     f = fetchEduAndMajor(inputs)
#     logger.warning(">>>>>>>>>>>>>>> 学历:" + f.get('edu', 'NONE') + "... 专业:" + f.get('major', 'NONE'))
#
#     if 'edu' not in f or 'major' not in f:
#         return jsonify([])
#     rst = []
#     results = getExpertsNodeList(f['edu'], f['major'])
#     print(results)
#     for record in results:
#         exp = {**{"id": record["experts"].id}, **{"expert_ID": record["experts"]["Expert_ID"]},
#                **dict(record["experts"].items())}
#         exp.pop("Expert_ID")
#         rst.append({"experts": exp, "field": {**{"id": record["field"].id}, **dict(record["field"].items())}})
#
#     return jsonify(rst)


# @app.route("/essearch", methods=['GET', 'POST'])
# def esSearcher():
#     inputs = request.values.get('input')
#     if not inputs:
#         return jsonify([])
#     path = INDEX_PATH + "experts"
#     ix = open_dir(path)
#     with ix.searcher() as searcher:
#         # parser = QueryParser("project", schema=ix.schema)
#         mparser = MultifieldParser(["project", "filed", "degree", "college", "subject"], schema=ix.schema)
#         # keyword = parser.parse("863计划")  # 构造查询语句
#         keyword = mparser.parse(inputs)  # 构造查询语句
#         results = searcher.search(keyword, limit=10)
#         res = []
#         for result in results:
#             res.append(dict(result))
#         return jsonify(res)
#
#
# @app.route("/create_index", methods=['GET', 'POST'])
# def create_index():
#     analyzer = ChineseAnalyzer()
#     schema = Schema(name=ID(stored=True, unique=True), college=TEXT(stored=True, analyzer=analyzer),
#                     education=TEXT(stored=True, analyzer=analyzer), degree=TEXT(stored=True, analyzer=analyzer),
#                     job=TEXT(stored=True, analyzer=analyzer), subject=TEXT(stored=True, analyzer=analyzer),
#                     research=TEXT(stored=True, analyzer=analyzer), department=TEXT(stored=True, analyzer=analyzer),
#                     title=TEXT(stored=True, analyzer=analyzer), filed=TEXT(stored=True, analyzer=analyzer),
#                     project=TEXT(stored=True, analyzer=analyzer))  # 声明索引模式
#     path = INDEX_PATH + "experts"
#
#     if not os.path.exists(path):
#         os.mkdir(path)
#     ix = create_in(path, schema)
#     writer = ix.writer()
#
#     csv_file = open('data/con_experts_pro.csv', 'r', encoding="utf-8")
#     data = csv.reader(csv_file)
#     for i in data:
#         writer.add_document(
#             name=i[2],
#             college=i[3], education=i[4],
#             degree=i[5], job=i[6],
#             subject=i[8], research=i[11],
#             department=i[12], title=i[13],
#             filed=i[15], project=i[16]
#         )
#     writer.commit()
#     return "success"


# @app.route("/es_my_delete_index", methods=['GET', 'POST'])
# def es_my_delete_index():
#     delete_index()
#     return "success"
#
#在csv的基础上直接读mysql
#
# -*- coding:UTF-8 -*-
# 当数据库新增数据的时候，同时把数据添加到es中 TODO： 需要确定发过来的是[{}, {}]还是{}
@app.route('/create_es', methods=['GET', 'POST', 'PUT'])
def create_es():
    # 接收参数
    data = request.data
    data_dict = json.loads(data)
    doc = dict()
    doc['Expert_ID'] = data_dict.get('Expert_ID')
    # doc['fieldID'] = data_dict.get('fieldID')
    doc['name'] = data_dict.get('name')
    doc['college'] = data_dict.get('college')
    doc['education'] = data_dict.get('education')
    doc['degree'] = data_dict.get('degree')
    doc['job'] = data_dict.get('job')
    # doc['professional'] = data_dict.get('professional')
    doc['subject'] = data_dict.get('subject')
    doc['phone'] = data_dict.get('phone')
    doc['address'] = data_dict.get('address')
    doc['research'] = data_dict.get('research')
    doc['department'] = data_dict.get('department')
    doc['title'] = data_dict.get('title')
    doc['email'] = data_dict.get('email')
    doc['field'] = data_dict.get('field')
    doc['project'] = data_dict.get('project')
    # 校验参数--略
    # 数据处理
    res = es.index(index=my_index, doc_type=my_doc_type, body=doc, id=doc['Expert_ID'])
    # 返回相应
    return res['result']


# 当数据库“修改”数据的时候，同时修改es中的数据
@app.route('/update_es', methods=['POST', 'PATCH'])
def update_es():
    # 接收参数 TODO: 需要知道对方发来的数据是仅仅变更的字段，还是所有字段
    data = request.data
    data_dict = json.loads(data)
    doc = {}
    doc['Expert_ID'] = data_dict.get('Expert_ID')
    # doc['fieldID'] = data_dict.get('fieldID')
    doc['name'] = data_dict.get('name')
    doc['college'] = data_dict.get('college')
    doc['education'] = data_dict.get('education')
    doc['degree'] = data_dict.get('degree')
    doc['job'] = data_dict.get('job')
    # doc['professional'] = data_dict.get('professional')
    doc['subject'] = data_dict.get('subject')
    doc['phone'] = data_dict.get('phone')
    doc['address'] = data_dict.get('address')
    doc['research'] = data_dict.get('research')
    doc['department'] = data_dict.get('department')
    doc['title'] = data_dict.get('title')
    doc['email'] = data_dict.get('email')
    doc['field'] = data_dict.get('field')
    doc['project'] = data_dict.get('project')
    # 校验参数--略
    # 数据处理
    # 先删除原来的
    es.delete(index=my_index, doc_type=my_doc_type, id=doc['Expert_ID'])
    # 再创建新的
    res = es.index(index=my_index, doc_type=my_doc_type, body=doc, id=doc['Expert_ID'])
    return res['result']


# 当数据库“删除”数据的时候，同时把删除es中的数据
@app.route('/delete_es', methods=['GET', 'POST', 'DELETE'])
def delete_es():
    args = request.args
    id = args.get('Expert_ID')
    result = es.delete(index=my_index, doc_type=my_doc_type, id=id)
    return result['result']

@app.route("/es_my_create_index", methods=['GET', 'POST'])
def es_my_create_index():
    create_indexs_es()
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    index_data_from_csv(os.path.join(BASE_DIR, 'data/con_experts_pro.csv'))
    mysql_data = get_data_from_mysql()
    # TODO: FieldID的索引时long类型，不能是字符串
    import_index_data(mysql_data)
    return "success"
#将从excel中获取的文件保存到数据库和ES中
@app.route('/upload_expert', methods=['POST'])
def upload_excel():
    # 获取网页上的文件
    files = request.files
    expert_file = files.get('expert_file')
    if expert_file is None:
        return "文件读取失败", 503
    file_name = str(time.time()) + '.xlsx'  # 用时间戳当文件名
    file_path = os.path.join(app.static_folder + '/', file_name)
    # with open(file_path, 'wb') as f:
    #     f.write(expert_file.read())
    expert_file.save(file_path)
    print('为了保存文件，睡10秒')  # TODO：需要优化
    time.sleep(10)
    # 解析Excel内容
    doc = parse_excel(file_path)
    # 保存到ES中
    es.index(index=my_index, doc_type=my_doc_type, body=doc, id=doc['Expert_ID'])
    # 保存到数据库
    save_to_mysql(doc)
    # 重命名文件，以后好找
    new_file_name = str(doc['Expert_ID']) + '.xlsx'
    new_file_path = os.path.join(app.static_folder, new_file_name)
    os.rename(file_path, new_file_path)
    return '上传文件，并将内容保存到数据库和ES成功！'


@app.route("/es_my_get_data", methods=['GET', 'POST'])
def es_my_get_data():
    inputs = request.values.get('input')
    if not inputs:
        return jsonify([])
    ###############################################
    segments = fetchEduAndMajor_es(inputs)
    # segments = jieba.lcut(inputs)
    ###############################################
    rst = get_data_by_body(inputs)
    # ###############################################

    json_hit = [item['_source'] for item in rst['hits']['hits']]
    # return jsonify(json_hit)
    # ###############################################
    return jsonify({'json_hit': json_hit, 'segments': segments})
    ###############################################
