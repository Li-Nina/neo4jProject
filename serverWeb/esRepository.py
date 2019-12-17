import logging
import csv
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from elasticsearch_dsl import connections
from config import CLUSTER_NODES
import pymysql
import openpyxl
import os
import time



logger = logging.getLogger(__name__)
logger.warning("getting connection to es ...")
es = Elasticsearch([CLUSTER_NODES])
my_index = 'con_pro_2'
my_doc_type = '_doc'


# connections.create_connection(hosts=[CLUSTER_NODES], timeout=20)
# client = Elasticsearch()

#
# def searchExpert():
#     s = Search(using=client, index="my-index") \
#         .filter("term", category="search") \
#         .query("match", title="python") \
#         .exclude("match", description="beta")
#
#     s.aggs.bucket('per_tag', 'terms', field='tags') \
#         .metric('max_lines', 'max', field='lines')
#
#     response = s.execute()
#
#     for hit in response:
#         print(hit.meta.score, hit.title)
#
#     for tag in response.aggregations.per_tag.buckets:
#         print(tag.key, tag.max_lines.value)
# -*- coding:UTF-8 -*-
# 创建索引
def create_indexs_es():
    _index_mappings = {
        "mappings": {
            "dynamic": "true",  # 动态的
            "properties": {
                "ExpertID": {
                    "type": "text",
                    "index": False
                },
                "fieldID": {
                    "type": "text",
                    "index": False
                },
                "name": {
                    "type": "text"
                },
                "college": {
                    "type": "text",
                    "analyzer": "ik_max_word"
                },
                "education": {
                    "type": "text",
                    "analyzer": "ik_max_word"
                },
                "degree": {
                    "type": "text",
                    "analyzer": "ik_max_word"
                },
                "job": {
                    "type": "text",
                    "analyzer": "ik_max_word"
                },
                "subject": {
                    "type": "text",
                    "analyzer": "ik_max_word"
                },
                "phone": {
                    "type": "text"
                },

                "address": {
                    "type": "text",
                    "analyzer": "ik_smart"  # 粗粒度分词
                },
                "research": {
                    "type": "text",
                    "analyzer": "ik_max_word"
                },

                "department": {
                    "type": "text",
                    "analyzer": "ik_max_word"
                },
                "title": {
                    "type": "text",
                    "analyzer": "ik_max_word"
                },
                "email": {
                    "type": "text"
                },
                "field": {
                    "type": "text",
                    "analyzer": "ik_max_word"
                },
                "project": {
                    "type": "text",
                    "analyzer": "ik_smart"  # 粗粒度分词
                }
            }
        }
    }
    if es.indices.exists(index=my_index) is not True:
        res = es.indices.create(index=my_index, body=_index_mappings)
        print("无索引，创建它:\n", res)
    else:
        print("索引已经存在，跳过创建！")


# 删除索引
def delete_index():
    if es.indices.exists(index=my_index) is True:
        res = es.indices.delete(index=my_index)


# 从CSV文件中读取数据，并存储到es中
def index_data_from_csv(csvfile):
    """
    :param csvfile: csv文件，包括完整路径
    """
    # 取CSV数据
    with open(csvfile, 'r', encoding='utf-8', newline='') as f:
        list_data = csv.reader(f)
        # 循环成字典形式，插入数据
        index = 0

        for item in list_data:
            doc = {}
            if index > 0:  # 第一行是标题
                doc['Expert_ID'] = item[0]
                # doc['fieldID'] = item[1]
                doc['name'] = item[2]
                doc['college'] = item[3]
                doc['education'] = item[4]
                doc['degree'] = item[5]
                doc['job'] = item[6]
                # doc['职称'] = item[7]
                doc['subject'] = item[8]
                doc['phone'] = item[9]
                doc['address'] = item[10]
                doc['research'] = item[11]
                doc['department'] = item[12]
                doc['title'] = item[13]
                doc['email'] = item[14]
                doc['field'] = item[15]
                doc['project'] = item[16]
                # print(doc)
                res = es.index(index=my_index, doc_type=my_doc_type, body=doc,id=doc['Expert_ID'])
                # print(res)
            index += 1
            # print(index)


# 根据请求体查询
def get_data_by_body(input):
    # dsl = {
    #     "query": {
    #         "match": {
    #             "领域": "区块链"
    #         }
    #     }
    # }
    dsl = {
        "query": {
            "multi_match": {
                "query": input,
                "type": "best_fields",
                # "type": "most_fields",
                # "fields" : ["学历", "领域",'单位','职务','职称','学科','研究方向','身份','领域','项目']
                "fields": ['college', 'education', 'degree', 'job', 'field', 'subject', 'research', 'department',
                           'title', 'project'],
                "tie_breaker": 0.3

            }
        }

    }
    res = es.search(index=my_index, body=dsl)
    return res
#
def get_data_from_mysql():
    """
    从MySQL数据库中读取数据
    :return: 元组
    """
    try:
        # 2.建立与数据库连接 TODO: 用户名root，密码x5
        conn = pymysql.connect(host="localhost", user="root", password="x5", database="expertserverbig",port=3306,charset="UTF8")

        # 3.获取游标
        cursor = conn.cursor()
    except ConnectionError as e:
        print("数据库连接异常 或 获取游标异常！", e)
        return []

    try:
        # TODO: Java组的数据没有expert_id这些数据，所以加上了expert_id is not null
        select_sql = "select expert_id, fieldId, name, college, education, degree, job, professional, subject, phonenumber, address, research, department, title, email, field, project from texpert_info  where expert_id is not null;"
        rows = cursor.execute(select_sql)
        if rows == 0:
            print('数据库没有数据')
            return
        # 移动指针，0代表移动几个位置，absolute表示回到头部，即：从头部移动0个位置cursor.scroll(0, 'absolute')
        # cursor.scroll(0, 'absolute')
        # 取出所有数据，返回的格式是：((), (),...) 元组套元组
        data_all = cursor.fetchall()

        # 将数据拼接成[{key:value}]的形式
        mysql_list = []
        for item in data_all:
            doc = {}
            doc['Expert_ID'] = item[0]  # 专家id  +
            # doc['fieldID'] = item[1]  # +
            doc['name'] = item[2]  # name
            doc['college'] = item[3]  # 单位  +
            doc['education'] = item[4]  # 学历  +
            doc['degree'] = item[5]  # 学位  +
            doc['job'] = item[6]  # 职务  +
            # doc['职称'] = item[7]  # professional
            doc['subject'] = item[8]  # 学科  +
            doc['phone'] = item[9]  # 工作电话  phonenumber
            doc['address'] = item[10]  # 地址  address
            doc['research'] = item[11]  # 研究方向  +
            doc['department'] = item[12]  # 所属部门  +
            doc['title'] = item[13]  # 身份  +
            doc['email'] = item[14]  # 邮箱 email
            doc['field'] = item[15]  # 领域  +
            doc['project'] = item[16]  # 项目  +
            mysql_list.append(doc)
        print(mysql_list)
        return mysql_list

    except pymysql.MySQLError as e:
        print('数据库操作异常，开始回滚', e)
        conn.rollback()
        return []
    finally:
        # 5：关闭游标、关闭连接
        cursor.close()
        conn.close()

# 导入数据到es中
def import_index_data(index_data):
    for data in index_data:
        es.index(index=my_index, doc_type=my_doc_type, body=data, id=data['Expert_ID'])
#解析excel文件
def parse_excel(excel_path):
    """
    excel_path: excel文件路径
    return: 解析后的字典
    """
    my_book = openpyxl.load_workbook(excel_path)
    my_sheet = my_book['Sheet1']
    # 开始解析数据
    doc = {}
    doc['Expert_ID'] = my_sheet.cell(2, 6).value
    doc['fieldID'] = my_sheet.cell(2, 8).value
    doc['name'] = my_sheet.cell(3, 2).value
    doc['college'] = my_sheet.cell(7, 2).value
    doc['education'] = my_sheet.cell(4, 2).value
    doc['degree'] = my_sheet.cell(4, 4).value
    doc['job'] = my_sheet.cell(4, 6).value
    doc['professional'] = my_sheet.cell(4, 8).value
    doc['subject'] = my_sheet.cell(5, 2).value
    doc['phone'] = my_sheet.cell(6, 2).value
    doc['address'] = my_sheet.cell(8, 2).value
    doc['research'] = my_sheet.cell(9, 2).value
    doc['department'] = my_sheet.cell(5, 6).value
    doc['title'] = my_sheet.cell(3, 8).value
    doc['email'] = my_sheet.cell(6, 6).value
    doc['field'] = my_sheet.cell(5, 8).value
    doc['project'] = my_sheet.cell(11, 2).value
    return doc

# 保存到数据库
def save_to_mysql(data):
    try:
        # 2.建立与数据库连接 TODO: 用户名root，密码x5
        conn = pymysql.connect(host="localhost",
                               user="root",
                               password="x5",
                               database="expertserverbig",
                               port=3306,
                               charset="UTF8")

        # 3.获取游标
        cursor = conn.cursor()
    except ConnectionError as e:
        print("数据库连接异常 或 获取游标异常！", e)
        return "数据保存失败"

    try:
        insert_sql = "insert into texpert_info(expert_id, fieldId, name, college, education, degree, " \
                     "job, professional, subject, phonenumber, address, research, department, " \
                     "title, email, field, project) " \
                     "value(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s);"
        # 这里字典的顺序和SQL语句参数的顺序一致，所以可以直接.values()
        rows = cursor.execute(insert_sql, args=list(data.values()))
        if rows == 0:
            return "数据保存失败，可能是SQL语句的问题"
        conn.commit()
        return "数据保存成功"

    except pymysql.MySQLError as e:
        print('数据库操作异常，开始回滚', e)
        conn.rollback()
        return "数据保存失败"
    finally:
        # 5：关闭游标、关闭连接
        cursor.close()
        conn.close()

# if __name__ == '__main__':
#     mysql_data = get_data_from_mysql()
#     # TODO: FieldID的索引时long类型，不能是字符串
#     import_index_data(mysql_data)