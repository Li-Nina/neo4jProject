#!/usr/bin/env python
# -*- coding:utf-8 -*-
import csv
import logging
# from serverWeb.esRepository import searchExpert
import os.path
import uuid

import jieba
import time
import os
from flask import request, Flask, jsonify, render_template, make_response, send_from_directory
from flask_cors import CORS
from jieba.analyse.analyzer import ChineseAnalyzer
from whoosh.fields import *
from whoosh.index import create_in
from whoosh.index import open_dir
from whoosh.qparser import MultifieldParser

from config import INDEX_PATH
from serverWeb.esRepository import get_data_by_body, create_indexs_es, index_data_from_csv, get_data_from_mysql, \
    import_index_data, modify_is_download
# from serverWeb.repository import getExpertsNodeList
import json
from serverWeb.esRepository import es, my_index, my_doc_type, parse_excel, parse_word, save_to_mysql, unzip_file, \
    untar_file, unrar_file, ungz_file
from utils.chatbot_graph import ChatBotGraph
from utils.util import fetchEduAndMajor
from utils.util2 import fetchEduAndMajor_es


def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'OPTIONS,HEAD,PUT,GET,POST,DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization,x-requested-with'
    return response


app = Flask(__name__, static_url_path='')
# CORS(app)
app.config['JSON_AS_ASCII'] = False  # jsonify返回的json串支持中文显示
app.after_request(after_request)

logger = logging.getLogger(__name__)
handler = ChatBotGraph()

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
# 上传word文档
@app.route('/upload_expert_word', methods=['POST'])
def upload_word():
    # 获取网页上的文件
    files = request.files
    expert_file = files.get('expert_file_word')
    if expert_file.filename == '':
        return "请上传文件", 503
    file_name = str(time.time()) + '.docx'  # 用时间戳当文件名
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print(BASE_DIR)
    file_path = os.path.join(BASE_DIR, 'data\\word\\' + file_name)
    expert_file.save(file_path)
    # 解析Excel内容
    docx = parse_word(file_path)
    # 保存到数据库 优化 1.如果expert_id已经存在则更新数据 2.如果expert_id不存在则新增数据
    result1 = save_to_mysql(docx)
    result2 = modify_is_download(docx['Expert_ID'], True)
    if (result1 == 'ERROR') or result2 == 'ERROR':
        return jsonify({"message": "ERROR"})
    try:
        # 先删除原来的
        es.delete(index=my_index, doc_type=my_doc_type, id=docx['Expert_ID'])
    except Exception as e:
        print("ES中不存在对应ID的文档，此处为新增操作，接下来直接新增ES即可。", e)
    # 再创建新的
    res = es.index(index=my_index, doc_type=my_doc_type, body=docx, id=docx['Expert_ID'])
    if (res['result'] != "created") and (res['result'] != "updated"):
        print("!!!!!!!数据库新增或更新数据后，ES中更新失败！")
        logger.error("!!!!!!!数据库新增或更新数据后，ES中更新失败！")
    # 重命名文件，以后好找
    new_file_name = str(docx['Expert_ID']).replace('\t', '') + '.docx'
    new_file_path = os.path.join(BASE_DIR, 'data\\word\\' + new_file_name)
    # 判断对应名字的文件是否存在，如果已存在，删除原来的文件保存新的文件
    if os.path.exists(new_file_path):
        os.remove(new_file_path)

    os.rename(file_path, new_file_path)

    # TODO: 修改数据库is_download字段为1

    return jsonify({"message": "SUCCESS"})


# 上传Excel
@app.route('/upload_expert', methods=['POST'])
def upload_excel():
    # 获取网页上的文件
    files = request.files
    expert_file = files.get('expert_file')
    if expert_file.filename == '':
        return "请上传文件", 503
    file_name = str(time.time()) + '.xlsx'  # 用时间戳当文件名
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(BASE_DIR, 'data/excel/' + file_name)
    expert_file.save(file_path)
    # 解析Excel内容
    doc = parse_excel(file_path)
    # 保存到数据库 优化 1.如果expert_id已经存在则更新数据 2.如果expert_id不存在则新增数据
    result1 = save_to_mysql(doc)
    result2 = modify_is_download(doc['Expert_ID'], True)
    if (result1 == 'ERROR') or result2 == 'ERROR':
        logger.error("上传Excel解析的数据保存到数据库或修改可下载字段失败！")
        return jsonify({"message": "ERROR"})

    # 重命名文件，以后好找
    new_file_name = str(doc['Expert_ID']) + '.xlsx'
    new_file_path = os.path.join(BASE_DIR, 'data/excel/' + new_file_name)
    # 判断对应名字的文件是否存在，如果已存在，删除原来的文件保存新的文件
    if os.path.exists(new_file_path):
        os.remove(new_file_path)

    os.rename(file_path, new_file_path)

    try:
        # 先删除原来的
        es.delete(index=my_index, doc_type=my_doc_type, id=doc['Expert_ID'])
    except Exception as e:
        print("ES中不存在对应ID的文档，此处为新增操作，接下来直接新增ES即可。", e)
    # 再创建新的
    res = es.index(index=my_index, doc_type=my_doc_type, body=doc, id=doc['Expert_ID'])
    if (res['result'] != "created") and (res['result'] != "updated"):
        print("!!!!!!!数据库新增或更新数据后，ES中更新失败！")
        logger.error("!!!!!!!数据库新增或更新数据后，ES中更新失败！")

    # TODO: 修改数据库is_download字段为1

    return jsonify({"message": "SUCCESS"})


# 下载Excel
@app.route("/download/<expert_id>", methods=['GET'])
def download_excel(expert_id):
    print("进入下载方法！！！！")
    # expert_id = filename.split(".", 1)[1]
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # TODO 这里如果只限定一种格式，上传的时候应该也只限定一种格式
    if os.path.exists(os.path.join(BASE_DIR, 'data/excel/', expert_id + ".xlsx")):
        # 需要知道2个参数, 第1个参数是本地目录的path, 第2个参数是文件名(带扩展名)
        response = make_response(
            send_from_directory(BASE_DIR + '/data/excel/', expert_id + ".xlsx", as_attachment=True))
        return response
    elif os.path.exists(os.path.join(BASE_DIR, 'data/word', expert_id + '.docx')):
        response = make_response(
            send_from_directory(BASE_DIR + '/data/word/', expert_id + ".docx", as_attachment=True))
        return response
    else:
        return jsonify({"message": "ERROR"})


# 上传压缩包
@app.route("/upload_package", methods=["POST"])
def upload_package():
    # 获取网页上的文件
    files = request.files
    package_file_obj = files.get('package_file')
    if package_file_obj.filename == '':
        return "上传文件为空", 503
    # 判断压缩包类型 zip、tar、rar、gz、tgz —— 略，都按zip处理
    ret_list = package_file_obj.filename.rsplit(".", maxsplit=1)
    if len(ret_list) != 2:
        return "请上传正确类型压缩包文件", 503

    # 方式：先保存压缩文件到本地，再对其进行解压，然后删除压缩文件
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # 上传的文件保存到的路径
    file_path = os.path.join(BASE_DIR, "data", package_file_obj.filename)
    package_file_obj.save(file_path)
    # 解压后的文件保存到的路径
    target_path = os.path.join(BASE_DIR, "data", str(uuid.uuid4()))

    if ret_list[1] == "zip":
        result = unzip_file(file_path, target_path)
    elif ret_list[1] == "tar":
        result = untar_file(file_path, target_path)
    elif ret_list[1] == "rar":
        result = unrar_file(file_path, target_path)
    elif ret_list[1] == "gz":
        result = ungz_file(file_path, target_path)
    else:
        return jsonify({"message": "ERROR"})

    # 删除原来的压缩包文件
    os.remove(file_path)

    if result != 'SUCCESS':
        return jsonify({"message": "ERROR"})

    return jsonify({"message": "SUCCESS"})


# 在csv的基础上直接读mysql
# 当数据库新增数据的时候，同时把数据添加到es中 TODO： 需要确定发过来的是[{}, {}]还是{}
# @app.route('/create_es', methods=['GET', 'POST', 'PUT'])
# def create_es():
#     # 接收参数
#     data = request.data
#     data_dict = json.loads(data)
#     doc = dict()
#     doc['Expert_ID'] = data_dict.get('Expert_ID')
#     # doc['fieldID'] = data_dict.get('fieldID')
#     doc['name'] = data_dict.get('name')
#     doc['college'] = data_dict.get('college')
#     doc['education'] = data_dict.get('education')
#     doc['degree'] = data_dict.get('degree')
#     doc['job'] = data_dict.get('job')
#     # doc['professional'] = data_dict.get('professional')
#     doc['subject'] = data_dict.get('subject')
#     doc['phone'] = data_dict.get('phone')
#     doc['address'] = data_dict.get('address')
#     doc['research'] = data_dict.get('research')
#     doc['department'] = data_dict.get('department')
#     doc['title'] = data_dict.get('title')
#     doc['email'] = data_dict.get('email')
#     doc['field'] = data_dict.get('field')
#     doc['project'] = data_dict.get('project')
#     # 校验参数--略
#     # 数据处理
#     res = es.index(index=my_index, doc_type=my_doc_type, body=doc, id=doc['Expert_ID'])
#     # 返回相应
#     return res['result']
#
#
# # 当数据库“修改”数据的时候，同时修改es中的数据
# @app.route('/update_es', methods=['POST', 'PATCH'])
# def update_es():
#     # 接收参数 TODO: 需要知道对方发来的数据是仅仅变更的字段，还是所有字段
#     data = request.data
#     data_dict = json.loads(data)
#     doc = {}
#     doc['Expert_ID'] = data_dict.get('Expert_ID')
#     # doc['fieldID'] = data_dict.get('fieldID')
#     doc['name'] = data_dict.get('name')
#     doc['college'] = data_dict.get('college')
#     doc['education'] = data_dict.get('education')
#     doc['degree'] = data_dict.get('degree')
#     doc['job'] = data_dict.get('job')
#     # doc['professional'] = data_dict.get('professional')
#     doc['subject'] = data_dict.get('subject')
#     doc['phone'] = data_dict.get('phone')
#     doc['address'] = data_dict.get('address')
#     doc['research'] = data_dict.get('research')
#     doc['department'] = data_dict.get('department')
#     doc['title'] = data_dict.get('title')
#     doc['email'] = data_dict.get('email')
#     doc['field'] = data_dict.get('field')
#     doc['project'] = data_dict.get('project')
#     # 校验参数--略
#     # 数据处理
#     # 先删除原来的
#     es.delete(index=my_index, doc_type=my_doc_type, id=doc['Expert_ID'])
#     # 再创建新的
#     res = es.index(index=my_index, doc_type=my_doc_type, body=doc, id=doc['Expert_ID'])
#     return res['result']
#
#
# # 当数据库“删除”数据的时候，同时把删除es中的数据
# @app.route('/delete_es', methods=['GET', 'POST', 'DELETE'])
# def delete_es():
#     args = request.args
#     id = args.get('Expert_ID')
#     result = es.delete(index=my_index, doc_type=my_doc_type, id=id)
#     return result['result']


@app.route("/es_my_create_index", methods=['GET', 'POST'])
def es_my_create_index():
    create_indexs_es()
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    index_data_from_csv(os.path.join(BASE_DIR, 'data/con_experts_pro.csv'))
    mysql_data = get_data_from_mysql()
    # TODO: FieldID的索引时long类型，不能是字符串
    import_index_data(mysql_data)
    return "success"


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


##################################################################
# 展示所有数据
@app.route('/experts')
def experts():
    # 接收参数--无
    # 校验参数--无
    # 数据处理
    experts = get_data_from_mysql()
    # 返回相应
    return jsonify(experts)


# 新增或修改数据
@app.route("/update_expert", methods=["POST"])
def update_expert():
    # 接收参数
    data = request.data
    data_dict = json.loads(data)

    # 校验参数
    if not data_dict["Expert_ID"]:
        return jsonify({"message": "ERROR"})
    # 在ES中并没有这一项，但是数据库的插入语句中有
    doc = {"Expert_ID": "", "fieldID": "", "name": "", "title": "", "education": "", "degree": "", "job": "",
           "professional": "", "subject": "", "college": "", "email": "", "field": "", "department": "", "phone": "",
           "address": "", "research": "", "project": ""}
    doc.update(data_dict)
    # 数据处理——增加到数据库
    result = save_to_mysql(doc)
    if result != "SUCCESS":
        return jsonify({"message": "ERROR"})
    try:
        # 先删除原来的
        es.delete(index=my_index, doc_type=my_doc_type, id=data_dict['Expert_ID'])
    except Exception as e:
        print("ES中不存在对应ID的文档，此处为新增操作，接下来直接新增ES即可。", e)
    # 再创建新的
    res = es.index(index=my_index, doc_type=my_doc_type, body=data_dict, id=data_dict['Expert_ID'])
    if (res['result'] != "created") and (res['result'] != "updated"):
        print("!!!!!!!数据库新增或更新数据后，ES中更新失败！")
        logger.error("!!!!!!!数据库新增或更新数据后，ES中更新失败！")
    # 返回响应
    return jsonify({"message": "SUCCESS"})


# 删除数据
@app.route("/delete_expert")
def delete_expert():
    args = request.args
    id = args.get('Expert_ID')
    # 删除数据库中的数据
    result1 = save_to_mysql({"Expert_ID": id})
    result2 = modify_is_download(id, False)
    if (result1 == 'ERROR') or result2 == 'ERROR':
        return jsonify({"message": "ERROR"})
    try:
        # 先删除原来的
        es.delete(index=my_index, doc_type=my_doc_type, id=id)
    except Exception as e:
        print("ES中不存在对应ID的文档，不用删除了", e)

    # TODO 修改is_download字段为0
    # 删除项目中的对应的文件（应该没必要）
    # 返回响应
    return jsonify({"message": "SUCCESS"})

# 智能问答
@app.route("/chatbot", methods=["POST"])
def chat_bot():
    data = request.data
    data_dict = json.loads(data)
    question = data_dict.get('question')
    if not question.strip():
        return jsonify({"message": "SUCCESS", "data": "您只有输入问题小智才能帮您解答呦(●'◡'●)"})
    for hello in ["你好", "您好", "hello", "HELLO", "hi", "HI"]:
        if question in hello or hello in question:
            return jsonify({"message": "SUCCESS", "data": "您好，有什么可以帮助您的吗？"})

    answer = handler.chat_main(question)
    return jsonify({"message": "SUCCESS", "data": answer})