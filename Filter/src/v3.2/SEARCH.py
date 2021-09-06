#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : SEARCH.py
# @Author: 胡煊林
# @Date  : 2021/8/26
# @Desc  : 向各个文献数据库请求的模块

import random
from threading import Thread
from abc import ABCMeta,abstractmethod

import requests;
from bs4 import BeautifulSoup;
from PyQt5.QtCore import pyqtSignal, QThread

class searchThread(QThread):
    """搜索子线程

    实现ui输入参数点击搜索后的搜索事项，把搜索下分到每一个文献数据库源的会话中，
    """

    __name = "搜索子线程"

    update_data = pyqtSignal(object)


class HttpServer(metaclass=ABCMeta):
    """Http会话抽象类

    建立一个http会话，随机User-Agent和proxy，维持后续通信。提供响应分析接口。
    """
    session = None
    __myheaders = None
    __myproxy = None

    def __init__(self, ):
        self.update()

    def __exit__(self):
        self.session.close()

    def update(self):
        '''更新一个session会话，刷新User-Agent和proxy'''

        # 断开当前会话
        if (self.session != None):
            self.session.close()

        # 建立新会话
        self.session = requests.Session()
        self.__myheaders["User-Agent"] = self.__randomAgent() or {}
        self.__myproxy = self.__randomproxy()

    @abstractmethod
    def analysis(self):
        '''分析请求响应的接口'''
        pass

    def __randomAgent(self):
        '''随机生成一个User-Agent'''
        return random.choice([])

    def __randomproxy(self):
        # return random.choice()
        pass

class Nature(HttpServer):
    """"""
    __name = "Nature"                               # 文献库对象
    __authority = "https://www.nature.com"          # 域名
    __url = "https://www.nature.com/search/ajax"    # 搜索url
    __nextpage = None                               # 是否存在搜索下一页内容
    __preread = None                                # 预读取页数，默认10页

    parameters = None                               # 请求参数字典

    def __init__(self,preread=None):
        super().__init__()
        self.__preread = preread or 10

    def __format(self, parameters):
        '''把通用请求参数字典格式化成Nature支持的请求参数字典

        :param parameters: 通用请求参数字典
        :return: Nature支持的请求参数字典
        '''

        pass

    def prepare(self, parameters):
        '''准备搜索

        :param parameters: 请求参数字典
        :param filter: 过滤表
        :return:
        '''

        pass

    def send(self):
        '''发送请求'''

        pass

    def analysis(self):
        pass