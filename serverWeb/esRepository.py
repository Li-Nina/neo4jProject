import logging
import csv
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from elasticsearch_dsl import connections
from config import CLUSTER_NODES

logger = logging.getLogger(__name__)
logger.warning("getting connection to es ...")
es = Elasticsearch([CLUSTER_NODES])
my_index = 'con_pro'
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
                    "type": "long"
                },
                "fieldID": {
                    "type": "long"
                },
                "姓名": {
                    "type": "text"
                },
                "单位": {
                    "type": "text",
                    "analyzer": "ik_max_word"
                },
                "学历": {
                    "type": "text",
                    "analyzer": "ik_max_word"
                },
                "学位": {
                    "type": "text",
                    "analyzer": "ik_max_word"
                },
                "职务": {
                    "type": "text",
                    "analyzer": "ik_max_word"
                },
                "职称": {
                    "type": "text",
                    "analyzer": "ik_max_word"
                },
                "学科": {
                    "type": "text",
                    "analyzer": "ik_max_word"
                },
                "工作电话": {
                    "type": "text"
                },

                "地址": {
                    "type": "text",
                    "analyzer": "ik_smart"  # 粗粒度分词
                },
                "研究方向": {
                    "type": "text",
                    "analyzer": "ik_max_word"
                },

                "所属部门": {
                    "type": "text",
                    "analyzer": "ik_max_word"
                },
                "身份": {
                    "type": "text",
                    "analyzer": "ik_max_word"
                },
                "邮箱": {
                    "type": "text"
                },
                "领域": {
                    "type": "text",
                    "analyzer": "ik_max_word"
                },
                "项目": {
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
        doc = {}
        for item in list_data:
            if index > 1:  # 第一行是标题
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
                # print(doc)
                res = es.index(index=my_index, doc_type=my_doc_type, body=doc)
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
                # "fields" : ["学历", "领域",'单位','职务','职称','学科','研究方向','身份','领域','项目']
                "fields": ['college', 'education', 'degree', 'job', 'field', 'subject', 'research', 'department',
                           'title', 'project']

            }
        }

    }
    res = es.search(index=my_index, body=dsl)
    return res
