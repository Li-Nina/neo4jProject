# -*- coding:UTF-8 -*-
"""
程序：从MySQL和CSV中获取数据存入到ES中
版本：1.0
作者：鬼义虎神
日期：2019年12月5日
原因：目前MySQL中的数据字段不全
临时解决方式：
    从MySQL读取数据后
        拼接
    从CSV读取的数据
         ||
    完整数据
        ||
       \_/
    ElasticSearch
"""
import os
import csv
import pymysql
from elasticsearch import Elasticsearch

es = Elasticsearch(['127.0.0.1:9200'])
my_index = 'mysql_csv'
my_doc_type = '_doc'


# 从数据库中读取数据，返回元组格式
def get_data_from_mysql():
    """
    从MySQL数据库中读取数据
    :return: 元组
    """
    try:
        # 2.建立与数据库连接
        conn = pymysql.connect(host="localhost", user="root", password="1237894560", database="food", port=3306,
                               charset="UTF8")

        # 3.获取游标
        cursor = conn.cursor()
    except ConnectionError as e:
        print("数据库连接异常 或 获取游标异常！", e)
        return []

    try:
        # TODO: 这里最好指定字段名
        select_sql = "select * from price"
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
            doc['id_m'] = item[0]
            doc['Expert_ID'] = item[1]
            doc['name_m'] = item[2]
            doc['price_m'] = item[3]
            doc['expenditure_m'] = item[4]
            doc['weight_m'] = item[5]
            doc['unit_m'] = item[6]
            doc['publish_date_m'] = item[7]
            # doc['isdelete_m'] = item[8]
            #
            doc['name'] = item[0]
            doc['phone'] = item[9]
            doc['address'] = item[10]
            doc['Expert_ID'] = item[0]
            doc['fieldID'] = item[1]
            doc['college'] = item[3]
            doc['education'] = item[4]
            doc['degree'] = item[5]
            doc['job'] = item[6]
            doc['subject'] = item[8]
            doc['research'] = item[11]
            doc['department'] = item[12]
            doc['title'] = item[13]
            doc['email'] = item[14]
            doc['field'] = item[15]
            doc['project'] = item[16]
            mysql_list.append(doc)
        return mysql_list

    except pymysql.MySQLError as e:
        print('数据库操作异常，开始回滚', e)
        conn.rollback()
        return []
    finally:
        # 5：关闭游标、关闭连接
        cursor.close()
        conn.close()


# 从CSV中读取数据，返回列表形式
def get_data_from_csv(csv_path):
    """
    :param csv_path: csv文件，包括完整路径
    :return 列表列表格式的数据
    """
    # 取CSV数据
    with open(csv_path, 'r', encoding='utf-8', newline='') as f:
        list_data = csv.reader(f)

        # 循环成字典形式，插入数据
        csv_list = []
        index = 1
        for item in list_data:
            doc = {}
            if index > 1:  # 第一行是标题，所以不读
                doc['Expert_ID'] = item[0]
                doc['fieldID'] = item[1]
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
                csv_list.append(doc)
            index += 1
        return csv_list


# 合并CSV和MySQL中读取数据的字段
def merge_mysql_csv_field(mysql_data, csv_data):
    # TODO: 初步思路是循环对比两个字典的Expert_ID，但是当数据量大的时候，效率会极低
    mysql_data_len = len(mysql_data)
    csv_data_len = len(csv_data)
    if mysql_data_len >= csv_data_len:
        for mysql_item in mysql_data:
            if len(csv_data) == 0:
                break

            for csv_item in csv_data:
                if str(csv_item['Expert_ID']) == str(mysql_item['Expert_ID']):
                    # 合并两个字典
                    mysql_item.update(csv_item)
                    csv_data.remove(csv_item)
                    break
        # 返回合并后的数据
        return mysql_data
    else:
        for csv_item in csv_data:
            if len(mysql_data) == 0:
                break

            for mysql_item in mysql_data:
                if str(csv_item['Expert_ID']) == str(mysql_item['Expert_ID']):
                    # 合并两个字典
                    csv_item.update(mysql_item)
                    mysql_data.remove(mysql_item)
                    break
        return csv_data


# 创建ES索引映射
def create_index_es():
    _index_mappings = {
        "mappings": {
            "dynamic": "true",  # 动态的
            "properties": {
                "ExpertID": {
                    "type": "long",
                },
                "fieldID": {
                    "type": "long",
                },
                "name": {
                    "type": "text",
                },
                "college": {
                    "type": "text",
                    "analyzer": "ik_max_word",
                    "copy_to": "all"
                },
                "education": {
                    "type": "text",
                    "analyzer": "ik_max_word",
                    "copy_to": "all"
                },
                "degree": {
                    "type": "text",
                    "analyzer": "ik_max_word",
                    "copy_to": "all"
                },
                "job": {
                    "type": "text",
                    "analyzer": "ik_max_word",
                    "copy_to": "all"
                },
                # "职称": {
                #     "type": "text",
                #     "analyzer": "ik_max_word"
                # },
                "subject": {
                    "type": "text",
                    "analyzer": "ik_max_word",
                    "copy_to": "all"
                },
                "phone": {
                    "type": "text",
                },
                "address": {
                    "type": "text",
                    "analyzer": "ik_smart",  # 粗粒度分词
                    "copy_to":"all"
                },
                "research": {
                    "type": "text",
                    "analyzer": "ik_max_word",
                    "copy_to": "all"
                },
                "department": {
                    "type": "text",
                    "analyzer": "ik_max_word",
                    "copy_to": "all"
                },
                "title": {
                    "type": "text",
                    "analyzer": "ik_max_word",
                    "copy_to": "all"
                },
                "email": {
                    "type": "text"
                },
                "field": {
                    "type": "text",
                    "analyzer": "ik_max_word",
                    "copy_to": "all"
                },
                "project": {
                    "type": "text",
                    "analyzer": "ik_smart",  # 粗粒度分词
                    "copy_to": "all"
                },
                "id_m": {
                    "type": "long",
                },
                "name_m": {
                    "type": "text",
                    "analyzer": "ik_max_word",
                    "copy_to": "all"
                },
                "price_m": {
                    "type": "float",
                },
                "expenditure_m": {
                    "type": "float",
                },
                "weight_m": {
                    "type": "float",
                },
                "unit_m": {
                    "type": "text",
                    "analyzer": "ik_max_word",  # 粗粒度分词
                    "copy_to": "all"
                },
                "publish_date_m": {
                    "type": "date",
                },
                "all": {
                    "type": "text",
                    "analyzer": "ik_max_word",
                }
            }
        }
    }

    if es.indices.exists(index=my_index) is not True:
        res = es.indices.create(index=my_index, body=_index_mappings)
        print("无索引映射，创建它:\n", res)
    else:
        print("索引已经存在，跳过创建！")


# 导入合并后的数据到es中
def import_index_data(index_data):
    for data in index_data:
        es.index(index=my_index, doc_type=my_doc_type, body=data)


if __name__ == '__main__':
    # 读取mysql的数据
    mysql_data = get_data_from_mysql()
    print('mysql_data的长度', len(mysql_data))
    # 读取csv的数据
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_data = get_data_from_csv(os.path.join(BASE_DIR, 'data/con_experts_pro.csv'))
    print('csv_data的长度', len(csv_data))
    # 合并mysql和csv数据的字段
    index_data = merge_mysql_csv_field(mysql_data, csv_data)
    print('index_data的长度', len(index_data))
    # 创建索引映射
    create_index_es()
    # 导入数据到es中
    import_index_data(index_data)
