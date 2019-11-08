#!/usr/bin/env python
# -*- coding:utf-8 -*-

from serverWeb.apis import app

if __name__ == '__main__':
    # 此处启动测试服务器，部署时不会执行这里
    app.run(host='0.0.0.0', port=12020)
# pip freeze > requirements.txt
# pip install -r requirements.txt
# pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn -r requirements.txt

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
