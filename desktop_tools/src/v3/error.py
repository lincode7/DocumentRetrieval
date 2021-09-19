#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : error.py
# @Author: 胡煊林
# @Date  : 2021/8/26
# @Desc  : 处理程序运行过程中的异常，QT异常、Http请求异常等

import json, os, time

def coast_time(func):
    '''利用修饰器实现测试闭包，测试函数运行时间

    :param func: 函数名
    :return: 函数运行结果
    '''
    def fun(*args, **kwargs):
        t = time.perf_counter()
        result = func(*args, **kwargs)
        print(f'func {func.__name__} coast time:{time.perf_counter() - t:.8f} s')
        return result
    return fun

def record_log(func):
    '''记录函数异常日志

    :param log: 异常信息字典{type:"",code:"",desc:"",position:""}
    :return:
    '''
    def fun(*args, **kwargs):
        return func(*args, **kwargs)
    try:
        return fun
    except:
        print(f"error occur: {func.__name__}")

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

