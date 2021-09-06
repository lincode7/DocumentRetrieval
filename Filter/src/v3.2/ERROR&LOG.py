#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : ERROR&LOG.py
# @Author: 胡煊林
# @Date  : 2021/8/26
# @Desc  : 处理程序运行过程中的异常，QT异常、Http请求异常等

import json, os, time

def record_log(log:dict):
    pass

class myException(Exception):
    '''
    自定义异常检测报告
    1.资源文件异常
     1.1 rcc路径异常
     1.2 rcc内部异常
      1.2.1 ui异常
      1.2.2 字体异常
      1.2.3 qss异常
      1.2.4 图片异常

    2.网络异常
     2.1 404
     2.2 403
     2.3 501
    '''
    def __init__(self):
        pass
