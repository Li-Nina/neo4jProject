#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
import re

import jieba
import synonyms

punctuation = '!，、\;:"？。'


def removePunctuation_es(text):
    text = re.sub(r'[{}]+'.format(punctuation), '', text)
    return text.strip()


def fetchEduAndMajor_es(text):
    words = ['语言对话与听觉', '区块链', '大数据', '虚拟现实与可视化技术', '人工智能与模式识别', '计算机视觉', '互联网',
             '多媒体技术', '分布式计算与系统', '硕士', '博士', '本科', '硕士以上', '不是博士', '不是硕士']
    for w in words:
        jieba.add_word(w, len(w) * 1000, 'nr')
    str_out = [w.strip() for w in list(jieba.lcut(removePunctuation_es(text), cut_all=False))]

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
                    str_out[i] = m
                    j = 1
                elif e in m and len(e) == 2:
                    r = synonyms.compare(e, m, seg=False)
                    s.append((e, m, r))
                    s.sort(key=lambda x: x[2], reverse=True)
                    str_out[i] = s[0][1]

    return str_out
