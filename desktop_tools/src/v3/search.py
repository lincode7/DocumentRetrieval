#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : search.py
# @Author: 胡煊林
# @Date  : 2021/8/26
# @Desc  : 处理后台http请求，向各个文献数据库发起请求

import random, datetime
from threading import Thread

from src.v3.data import *

import requests
from bs4 import BeautifulSoup
from PyQt5.QtCore import pyqtSignal, QThread


class searchThread(QThread):
    """搜索子线程

    实现ui输入参数点击搜索后的搜索事项，把搜索下分到每一个文献数据库源的会话中，
    """

    __name = "搜索子线程"

    update_data = pyqtSignal(object)


class HttpServer:
    """建立一个http会话，随机User-Agent和proxy，维持后续通信。

    主要接口是 update_session 和 request_analysis

    基本使用：
      >>> nature_conf = {"name": "1","authority": "http://www.000.com"}
      >>> nature = HttpServer(nature_conf)
      >>> nature.request_analysis(keyword="1", title="2", author="3", dateSt="1111/12/11", dateEnd="2222/01/09")
    """
    session = None
    __myheaders = {}
    __myproxy = {}
    __config = None

    def __init__(self, config=None):
        #: 初始化一个http会话
        #: config：json化的请求与相应分析逻辑
        self.update_session()
        self.__config = config or None

    def __exit__(self):
        self.session.close()

    def __randomAgent(self):
        '''随机生成一个User-Agent'''
        return random.choice([
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:65.0) Gecko/20100101 Firefox/65.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.3 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/18.17763',
            'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 7_0_4 like Mac OS X) AppleWebKit/537.51.1 (KHTML, like Gecko) CriOS/31.0.1650.18 Mobile/11B554a Safari/8536.25',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 8_3 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12F70 Safari/600.1.4',
            'Mozilla/5.0 (Linux; Android 4.2.1; M040 Build/JOP40D) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.59 Mobile Safari/537.36',
            'Mozilla/5.0 (Linux; U; Android 4.4.4; zh-cn; M351 Build/KTU84P) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30',
            "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
            "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
            "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
            "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
            "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
            "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
            "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
            "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
            "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
            "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
        ])

    def __randomproxy(self):
        '''随机生成一个代理ip，工具执行过程中，除了一开始的几页的预读，连续请求间隔基本和人的实际操作一致，暂时用不到'''
        # return random.choice([])
        pass

    def update_session(self):
        '''更新一个session会话，刷新User-Agent和proxy'''

        # 断开上一会话
        if (self.session != None):
            self.session.close()

        # 建立新会话
        self.session = requests.Session()
        self.__myheaders["User-Agent"] = self.__randomAgent() or {}
        self.__myproxy = self.__randomproxy()

    def __format_params(self, payload):
        '''格式化请求参数

        :param pyload: 外部传入统一参数
        :return 针对当前源格式化的请求参数
        '''

        # 搜索源参数配置正常
        if self.__config or self.__config["params"]:
            params = {
                self.__config["payload"]["keyword"]: payload["keyword"],
                self.__config["payload"]["title"]: payload["title"],
                self.__config["payload"]["author"]: payload["author"],
                self.__config["payload"]["dateSt"]: payload["dateSt"],
                self.__config["payload"]["dateEnd"]: payload["dateEnd"],
                self.__config["payload"]["dateRange"]: payload["dateRange"]
            }
        else:
            print("json配置缺少请求参数格式转换逻辑")

    def request_analysis(self, **kwargs):
        ''' 发出请求与分析请求响应的接口

        :param kwargs: 请求参数字典,传入格式一致,通过config的params字段格式化
        :return:
        '''
        #: 1 发送请求
        #: (1) 格式化请求参数
        payload = self.__format_params(kwargs)
        #: (2) 发送
        request_prepare = None
        if self.__config["method"]=="GET":

            request_prepare = requests.Request(method=self.__config["method"],
                                                url=self.__config["url"],
                                                headers=self.__myheaders,
                                                params=payload)
        #: 2 分析数据
        #: (1) 判断是否空
        #: (2) 提取数据
        pass
