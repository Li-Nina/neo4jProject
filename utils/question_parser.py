#!/usr/bin/env python3
# coding: utf-8
# File: question_parser.py
# Author: lhy<lhy_in_blcu@126.com,https://huangyong.github.io>
# Date: 18-10-4

class QuestionPaser:

    '''构建实体节点'''
    def build_entitydict(self, args) -> object:
        entity_dict = {}
        for arg, types in args.items():
            for type in types:
                if type not in entity_dict:
                    entity_dict[type] = [arg]
                else:
                    entity_dict[type].append(arg)

        return entity_dict

    '''解析主函数'''
    def parser_main(self, res_classify):
        args = res_classify['args']
        entity_dict = self.build_entitydict(args)
        question_types = res_classify['question_types']
        sqls = []
        for question_type in question_types:
            sql_ = {}
            sql_['question_type'] = question_type
            sql = []

            if question_type == 'expert_subject':
                sql = self.sql_transfer(question_type, entity_dict.get('expert'))

            elif question_type == 'subject_expert':
                sql = self.sql_transfer(question_type, entity_dict.get('subject'))

            elif question_type == 'expert_field':
                sql = self.sql_transfer(question_type, entity_dict.get('expert'))

            elif question_type == 'field_expert':
                sql = self.sql_transfer(question_type, entity_dict.get('field'))

            elif question_type == 'expert_college':
                sql = self.sql_transfer(question_type, entity_dict.get('expert'))

            elif question_type == 'expert_research':
                sql = self.sql_transfer(question_type, entity_dict.get('expert'))

            elif question_type == 'expert_project':
                sql = self.sql_transfer(question_type, entity_dict.get('expert'))

            elif question_type == 'project_expert':
                sql = self.sql_transfer(question_type, entity_dict.get('project'))

            elif question_type == 'project_field':
                sql = self.sql_transfer(question_type, entity_dict.get('project'))

            elif question_type == 'expert_education':
                sql = self.sql_transfer(question_type, entity_dict.get('expert'))

            elif question_type == 'expert_degree':
                sql = self.sql_transfer(question_type, entity_dict.get('expert'))

            elif question_type == 'expert_job':
                sql = self.sql_transfer(question_type, entity_dict.get('expert'))

            elif question_type == 'expert_title':
                sql = self.sql_transfer(question_type, entity_dict.get('expert'))

            elif question_type == 'expert_department':
                sql = self.sql_transfer(question_type, entity_dict.get('expert'))

            elif question_type == 'expert_email':
                sql = self.sql_transfer(question_type, entity_dict.get('expert'))

            elif question_type == 'expert_address':
                sql = self.sql_transfer(question_type, entity_dict.get('expert'))

            elif question_type == 'expert_phone':
                sql = self.sql_transfer(question_type, entity_dict.get('expert'))

            elif question_type == 'expert_desc':
                sql = self.sql_transfer(question_type, entity_dict.get('expert'))

            if sql:
                sql_['sql'] = sql

                sqls.append(sql_)

        return sqls

    '''针对不同的问题，分开进行处理'''
    def sql_transfer(self, question_type, entities):
        if not entities:
            return []

        # 查询语句
        sql = []
        # 查询学历
        if question_type == 'expert_education':
            sql = ["MATCH (m:Expert) where m.name = '{0}' return m.name, m.education".format(i) for i in entities]

        # 查询学位
        elif question_type == 'expert_degree':
            sql = ["MATCH (m:Expert) where m.name = '{0}' return m.name, m.degree".format(i) for i in entities]

        # 查询职务
        elif question_type == 'expert_job':
            sql = ["MATCH (m:Expert) where m.name = '{0}' return m.name, m.job".format(i) for i in entities]

        # 查询身份
        elif question_type == 'expert_title':
            sql = ["MATCH (m:Expert) where m.name = '{0}' return m.name, m.title".format(i) for i in entities]

        # 查询部门
        elif question_type == 'expert_department':
            sql = ["MATCH (m:Expert) where m.name = '{0}' return m.name, m.department".format(i) for i in entities]

        # 查询邮件
        elif question_type == 'expert_email':
            sql = ["MATCH (m:Expert) where m.name = '{0}' return m.name, m.email".format(i) for i in entities]

        # 查询地址
        elif question_type == 'expert_address':
            sql = ["MATCH (m:Expert) where m.name = '{0}' return m.name, m.address".format(i) for i in entities]

        # 查询电话
        elif question_type == 'expert_phone':
            sql = ["MATCH (m:Expert) where m.name = '{0}' return m.name, m.phone".format(i) for i in entities]

        # 查询专家的相关介绍
        elif question_type == 'expert_desc':
            sql = ["MATCH (m:Expert) where m.name = '{0}' return m.name, m.expert_id".format(i) for i in entities]

        # 查询专家-学科
        elif question_type == 'expert_subject':
            sql = ["MATCH (m:Subject)-[r:include_in]->(n:Expert) where n.name = '{0}' return m.name, r.name, n.name".format(i) for i in entities]

        # 查询学科-专家
        elif question_type == 'subject_expert':
            sql = ["MATCH (m:Subject)-[r:include_in]->(n:Expert)  where m.name = '{0}' return m.name, r.name, n.name".format(i) for i in entities]

        # 查询专家-领域
        elif question_type == 'expert_field':
            sql = ["MATCH (m:Expert)-[r:belongs_to]->(n:Field) where m.name = '{0}' return m.name, r.name, n.name".format(i) for i in entities]

        # 查询领域-专家
        elif question_type == 'field_expert':
            sql = ["MATCH (m:Expert)-[r:belongs_to]->(n:Field) where n.name = '{0}' return m.name, r.name, n.name".format(i) for i in entities]

        # 查询专家-单位
        elif question_type == 'expert_college':
            sql = ["MATCH (m:Expert)-[r:work_in]->(n:College) where m.name = '{0}' return m.name, r.name, n.name".format(i) for i in entities]

        # 已知专家-研究方向
        elif question_type == 'expert_research':
            sql = ["MATCH (m:Expert)-[r:research_in]->(n:Research) where m.name = '{0}' return m.name, r.name, n.name".format(i) for i in entities]

        # 已知专家-项目
        elif question_type == 'expert_project':
            sql = ["MATCH (m:Expert)-[r:involved_in]->(n:Project) where m.name = '{0}' return m.name, r.name, n.name".format(i) for i in entities]

        # 查询项目-专家
        elif question_type == 'project_expert':
            sql = ["MATCH (m:Expert)-[r:involved_in]->(n:Project) where n.name = '{0}' return m.name, r.name, n.name".format(i) for i in entities]

        # 已知项目-领域
        elif question_type == 'project_field':
            sql = ["MATCH (m:Project)-[r:refer_to]->(n:Field) where m.name = '{0}' return m.name, r.name, n.name".format(i) for i in entities]

        return sql



if __name__ == '__main__':
    handler = QuestionPaser()
