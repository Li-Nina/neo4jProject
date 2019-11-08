#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
import re

import jieba
import synonyms

punctuation = '!，、\;:"？。'


def removePunctuation(text):
    text = re.sub(r'[{}]+'.format(punctuation), '', text)
    return text.strip()


def fetchEduAndMajor(text):
    words = ['语言对话与听觉', '区块链', '大数据', '虚拟现实与可视化技术', '人工智能与模式识别', '计算机视觉', '互联网',
             '多媒体技术', '分布式计算与系统', '学位', '硕士', '博士', '本科', '硕士以上', '不是博士', '不是硕士']
    for w in words:
        jieba.add_word(w, len(w) * 1000, 'nr')
    str_out = [w.strip() for w in list(jieba.cut(removePunctuation(text), cut_all=False))]

    s = []
    Education = {'硕士', '博士', '本科', '硕士以上', '不是博士', '不是硕士', '硕士学位', '博士学位'}
    field_list = ['语言对话与听觉', '区块链', '大数据', '虚拟现实与可视化技术', '人工智能与模式识别',
                  '计算机视觉', '互联网', '多媒体技术', '分布式计算与系统']
    f = {}
    for e in str_out:
        if e in Education:
            if e == '硕士以上' or e == '不是硕士':
                f['edu'] = '博士'
            elif e == '不是博士':
                f['edu'] = '硕士'
            else:
                f['edu'] = e[:2]
            break

    for n in str_out:
        for m in field_list:
            if n in m and len(n) > 2:
                f['major'] = m
                break
            elif len(n) > 0 and len(m) > 0:
                r = synonyms.compare(n, m, seg=False)
                s.append((n, m, r))

    if 'major' not in f.keys():
        s.sort(key=lambda x: x[2], reverse=True)
        f['major'] = s[0][1]

    return f
