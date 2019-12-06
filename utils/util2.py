#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
import re

import jieba
import synonyms
import pandas as pd

punctuation = '!，、\;:"？。'
def drop_stopwords(content,stopwords):
    content_clean = []
    all_words = []
    for word in content:
        if word in stopwords:
            continue
        content_clean.append(word)
        all_words.append(str(word))#str返回对象的字符串格式
    return content_clean,all_words

def removePunctuation_es(text):
    text = re.sub(r'[{}]+'.format(punctuation), '', text)
    return text.strip()


def fetchEduAndMajor_es(text):
    """

    :type text: object
    """
    # stopwords_all = [line.strip() for line in open('../data/stopwords.txt', encoding='UTF-8').readlines()]
    words = ['语言对话与听觉', '区块链', '大数据', '虚拟现实与可视化技术', '人工智能与模式识别', '计算机视觉', '互联网',
             '多媒体技术', '分布式计算与系统', '硕士', '博士', '本科', '硕士以上', '不是博士', '不是硕士']
    for w in words:
        jieba.add_word(w, len(w) * 1000, 'nr')
    remove_text = removePunctuation_es(text)
    remove_none = remove_text.replace(" ", "")
    remove_stop = remove_none.replace("的","")
    jieba_data = jieba.lcut(remove_stop)
    # remove_none = remove_text.replace(" ", "")
    # jieba_data = jieba.lcut(remove_none)
    # content_clean, all_words = drop_stopwords(jieba_data, stopwords_all)
    # str_out = [w.strip() for w in list(content_clean)]
    str_out = [w.strip() for w in list(jieba_data)]
    s = []
    Education = {'硕士', '博士', '本科', '硕士以上', '不是博士', '不是硕士', '硕士学位', '博士学位'}
    field_list = ['语言对话与听觉', '区块链', '大数据', '虚拟现实与可视化技术', '人工智能与模式识别',
                  '计算机视觉', '互联网', '多媒体技术', '分布式计算与系统']
    for i, e in enumerate(str_out):
        if e in Education:
            if e == '硕士以上' or e == '不是硕士':
                str_out[i] = '博士'
            elif e == '不是博士':
                str_out[i] = '硕士'
            else:
                str_out[i] = e[:2]
            break
        else:
            for m in field_list:
                if e in m and len(e) > 2:
                    str_out[i] = e
                    j = 1
                elif e in m and len(e) == 2:
                    r = synonyms.compare(e, m, seg=False)
                    s.append((e, m, r))
                    s.sort(key=lambda x: x[2], reverse=True)
                    str_out[i] = s[0][1]

    return str_out
# text = "请问AI方面的不是硕士 参与863 的专家有哪些？"
# text1 = fetchEduAndMajor_es(text)
# print(text1)