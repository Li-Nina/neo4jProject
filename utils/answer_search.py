#!/usr/bin/env python3
# coding: utf-8
# File: answer_search.py
# Author: lhy<lhy_in_blcu@126.com,https://huangyong.github.io>
# Date: 18-10-5

from py2neo import Graph

class AnswerSearcher:
    def __init__(self):
        self.g = Graph("http://localhost:7474", auth=("neo4j", "123456"))

        # self.g = Graph(
        #     host="127.0.0.1",
        #     http_port=7474,
        #     user="lhy",
        #     password="lhy123")

        self.num_limit = 20

    '''执行cypher查询，并返回相应结果'''
    def search_main(self, sqls):
        final_answers = []
        for sql_ in sqls:
            question_type = sql_['question_type']
            queries = sql_['sql']
            answers = []
            for query in queries:
                ress = self.g.run(query).data()
                answers += ress
            final_answer = self.answer_prettify(question_type, answers)
            if final_answer:
                final_answers.append(final_answer)
        return final_answers

    '''根据对应的qustion_type，调用相应的回复模板'''
    def answer_prettify(self, question_type, answers):
        final_answer = []
        if not answers:
            return ''

        if question_type == 'expert_education':
            desc = [i['m.education'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}的学历：{1}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'expert_degree':
            desc = [i['m.degree'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}的学位：{1}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'expert_job':
            desc = [i['m.job'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}的职务：{1}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'expert_title':
            desc = [i['m.title'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}的身份：{1}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'expert_department':
            desc = [i['m.department'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}的部门：{1}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'expert_email':
            desc = [i['m.email'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}的邮箱：{1}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'expert_address':
            desc = [i['m.address'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}的地址：{1}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'expert_phone':
            desc = [i['m.phone'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}的电话：{1}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'expert_desc':
            desc = [i['m.expert_id'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}的ID：{1}'.format(subject,  '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'expert_subject':
            desc = [i['m.name'] for i in answers]
            subject = answers[0]['n.name']
            final_answer = '{0}属于的学科是：{1}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'subject_expert':
            desc = [i['n.name'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '学科：{0}包括的专家有：{1}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'expert_field':
            desc = [i['n.name'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}的研究领域是：{1}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))
        elif question_type == 'field_expert':
            desc = [i['m.name'] for i in answers]
            subject = answers[0]['n.name']
            final_answer = '{0}领域包括的专家有：{1}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'expert_college':
            desc = [i['n.name'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}就职于：{1}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'expert_research':
            desc = [i['n.name'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}的研究方向是：{1}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'expert_project':
            desc = [i['n.name'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}参与的项目有：{1}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'project_expert':
            desc = [i['m.name'] for i in answers]
            subject = answers[0]['n.name']
            final_answer = '{0}参与的专家有：{1}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'project_field':
            desc = [i['n.name'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}涉及的领域有：{1}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

        return final_answer


if __name__ == '__main__':
    searcher = AnswerSearcher()