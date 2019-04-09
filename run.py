#!/usr/bin/env python
# -*- coding:utf-8 -*-

# todo,源码保护问题
# todo 1,混合料计算烧损更改，不除以h2o
# todo 2,最优需要考虑价格，算法修改
from serverWeb import app

if __name__ == '__main__':
    # 此处启动测试服务器，部署时不会执行这里
    app.run(host='0.0.0.0')
# pip freeze > requirements.txt
# pip install -r requirements.txt

# nohup gunicorn -w 2 -b 0.0.0.0:5000 run:app &
# nohup gunicorn -w 2 -b 0.0.0.0:5000 run:app >nohup.log 2>&1 &
"""
  nohup进程挂着不断
                 -w启动2个线程
                      -b绑定端口
                                              >stdout重定向
                                                         2>&1表示stderr重定向到stdout的位置
                                                              &表示这是一个后台程序 @see:
https://stackoverflow.com/questions/13338870/what-does-at-the-end-of-a-linux-command-mean
"""
