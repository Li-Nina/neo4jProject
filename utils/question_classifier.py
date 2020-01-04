#!/usr/bin/env python3
# coding: utf-8
# File: question_classifier.py
# Author: lhy<lhy_in_blcu@126.com,https://huangyong.github.io>
# Date: 18-10-4

import os
import ahocorasick

class QuestionClassifier:
    def __init__(self):
        cur_dir = '/'.join(os.path.abspath(__file__).split('/')[:-2])
        #　特征词路径
        self.expert_path = os.path.join(cur_dir, 'dict/expert.txt')
        self.college_path = os.path.join(cur_dir, 'dict/college.txt')
        self.field_path = os.path.join(cur_dir, 'dict/field.txt')
        self.research_path = os.path.join(cur_dir, 'dict/research.txt')
        self.subject_path = os.path.join(cur_dir, 'dict/subject.txt')
        self.project_path = os.path.join(cur_dir, 'dict/project.txt')
        # self.symptom_path = os.path.join(cur_dir, 'dict/symptom.txt')
        self.deny_path = os.path.join(cur_dir, 'dict/deny.txt')
        # 加载特征词
        self.expert_wds= [i.strip() for i in open(self.expert_path, encoding='utf-8') if i.strip()]
        self.college_wds= [i.strip() for i in open(self.college_path, encoding='utf-8') if i.strip()]
        self.field_wds= [i.strip() for i in open(self.field_path, encoding='utf-8') if i.strip()]
        self.research_wds= [i.strip() for i in open(self.research_path, encoding='utf-8') if i.strip()]
        self.subject_wds= [i.strip() for i in open(self.subject_path, encoding='utf-8') if i.strip()]
        self.project_wds= [i.strip() for i in open(self.project_path, encoding='utf-8') if i.strip()]
        # self.symptom_wds= [i.strip() for i in open(self.symptom_path, encoding='utf-8') if i.strip()]
        self.region_words = set(self.college_wds + self.expert_wds + self.field_wds + self.research_wds + self.subject_wds + self.project_wds )
        self.deny_words = [i.strip() for i in open(self.deny_path, encoding='utf-8') if i.strip()]
        # 构造领域actree
        self.region_tree = self.build_actree(list(self.region_words))
        # 构建词典
        self.wdtype_dict = self.build_wdtype_dict()
        # 问句疑问词
        self.subject_qwds = ['学科','专业', '包括', '涵盖', '有',' 包含','有哪些']
        self.field_qwds = ['领域', '研究领域','专业领域','属于','归于', ]
        self.college_qwds = ['工作单位', '单位','学校','科研机构','研究院','就职于', '工作', '就职', '上班','高就']
        self.research_qwds = ['研究方向', '研究', '专业领域']
        self.project_qwds = ['项目','参与项目', '参与', '参加', '主持', '负责','研发','设计','指导']
        self.pro_field_qwds = ['涉及','相关']

        self.education_qwds = ['学历', '毕业学历']
        self.degree_qwds = ['学位', '博士', '硕士','学士']
        self.job_qwds = ['职务', '任职','博导','硕士生导师']
        self.title_qwds = ['身份', '担任','系主任','院士','校长','教授','研究员']
        self.department_qwds = ['部门', '所属部门','哪个学院','实验室','会','所','部','系','中心']
        self.email_qwds = ['邮箱', '电子邮箱', 'email', 'e-mail','E-mail','EMAIL','电子邮件地址','邮件地址']
        self.address_qwds = ['地址', '地方','位置']
        self.phone_qwds = ['电话', '联系方式','手机号','手机','号码']

        print('model init finished ......')

        return

    '''分类主函数'''
    def classify(self, question):
        data = {}
        expert_dict = self.check_medical(question)
        if not expert_dict:
            return {}
        data['args'] = expert_dict
        #收集问句当中所涉及到的实体类型
        types = []
        for type_ in expert_dict.values():
            types += type_
        question_type = 'others'

        question_types = []

        # 学科
        if self.check_words(self.subject_qwds, question) and ('expert' in types):
            question_type = 'expert_subject'
            question_types.append(question_type)

        if self.check_words(self.subject_qwds, question) and ('subject' in types):
            question_type = 'subject_expert'
            question_types.append(question_type)

        # 领域
        if self.check_words(self.field_qwds, question) and ('expert' in types):
            question_type = 'expert_field'
            question_types.append(question_type)
        if self.check_words(self.field_qwds, question) and ('field' in types):
            question_type = 'field_expert'
            question_types.append(question_type)

        #工作单位
        if self.check_words(self.college_qwds, question) and ('expert' in types):
            question_type = 'expert_college'
            question_types.append(question_type)

        # 研究方向
        if self.check_words(self.research_qwds, question) and ('expert' in types):
            question_type = 'expert_research'
            question_types.append(question_type)

        # 项目
        if self.check_words(self.project_qwds, question) and ('expert' in types):
            question_type = 'expert_project'
            question_types.append(question_type)
        if self.check_words(self.project_qwds, question) and ('project' in types):
            question_type = 'project_expert'
            question_types.append(question_type)
        #项目-领域
        if self.check_words(self.pro_field_qwds, question) and ('project' in types):
            question_type = 'project_field'
            question_types.append(question_type)

        # 学历
        if self.check_words(self.education_qwds, question) and 'expert' in types:
            question_type = 'expert_education'
            question_types.append(question_type)

        # 学位
        if self.check_words(self.degree_qwds, question) and 'expert' in types:
            question_type = 'expert_degree'
            question_types.append(question_type)

        # 职务
        if self.check_words(self.job_qwds, question) and 'expert' in types:
            question_type = 'expert_job'
            question_types.append(question_type)

        #　身份
        if self.check_words(self.title_qwds, question) and 'expert' in types:
            question_type = 'expert_title'
            question_types.append(question_type)

        # 部门
        if self.check_words(self.department_qwds, question) and 'expert' in types:
            question_type = 'expert_department'
            question_types.append(question_type)

        # 邮箱
        if self.check_words(self.email_qwds, question) and 'expert' in types:
            question_type = 'expert_email'
            question_types.append(question_type)

        # 地址
        if self.check_words(self.address_qwds, question) and 'expert' in types:
            question_type = 'expert_address'
            question_types.append(question_type)

        # 电话
        if self.check_words(self.phone_qwds, question) and 'expert' in types :
            question_type = 'expert_phone'
            question_types.append(question_type)

        # 若没有查到相关的外部查询信息，那么则将该专家的描述信息返回
        if question_types == [] and 'expert' in types:
            question_types = ['expert_desc']

        # 若没有查到相关的外部查询信息，那么则将项目的描述信息返回
        if question_types == [] and 'project' in types:
            question_types = ['project_field']

        # 将多个分类结果进行合并处理，组装成一个字典
        data['question_types'] = question_types

        return data

    '''构造词对应的类型'''
    def build_wdtype_dict(self):
        wd_dict = dict()
        for wd in self.region_words:
            wd_dict[wd] = []
            if wd in self.expert_wds:
                wd_dict[wd].append('expert')
            if wd in self.college_wds:
                wd_dict[wd].append('college')
            if wd in self.field_wds:
                wd_dict[wd].append('field')
            if wd in self.research_wds:
                wd_dict[wd].append('research')
            if wd in self.subject_wds:
                wd_dict[wd].append('subject')
            # if wd in self.symptom_wds:
            #     wd_dict[wd].append('symptom')
            if wd in self.project_wds:
                wd_dict[wd].append('project')
        return wd_dict

    '''构造actree，加速过滤'''
    def build_actree(self, wordlist):
        actree = ahocorasick.Automaton()
        for index, word in enumerate(wordlist):
            actree.add_word(word, (index, word))
        actree.make_automaton()
        return actree

    '''问句过滤'''
    def check_medical(self, question):
        region_wds = []
        for i in self.region_tree.iter(question):
            wd = i[1][1]
            region_wds.append(wd)
        stop_wds = []
        for wd1 in region_wds:
            for wd2 in region_wds:
                if wd1 in wd2 and wd1 != wd2:
                    stop_wds.append(wd1)
        final_wds = [i for i in region_wds if i not in stop_wds]
        final_dict = {i:self.wdtype_dict.get(i) for i in final_wds}

        return final_dict

    '''基于特征词进行分类'''
    def check_words(self, wds, sent):
        for wd in wds:
            if wd in sent:
                return True
        return False


if __name__ == '__main__':
    handler = QuestionClassifier()
    while 1:
        question = input('input an question:')
        data = handler.classify(question)
        print(data)