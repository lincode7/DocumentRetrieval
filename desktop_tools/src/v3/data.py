#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : DATA.py
# @Author: 胡煊林
# @Date  : 2021/8/26
# @Desc  : 处理返回数据：合并，过滤，排序等


import os, json, sqlite3


class DataFormat:
    flag = ["payload", "result"]

    def __init__(self, type:str):
        if self.flag.index(type):
            self.title = None
            self.author = None
            self.publishDate = None
            self.type = None
            self.dio = None
        else:
            self.rules = None
            self.dateSt = None
            self.dateEnd = None
            self.order = None


class JSONIF:
    """初始化文件指针,不存在则创建

    :param: FName: 文件名，默认log.json文件保存日志
    :return: none
    """
    path = None

    def __init__(self, FName="log.json"):
        self.path = os.path.join(".", FName)
        try:
            with open(self.path, 'r', encoding='utf-8') as r:
                r.read()
        except:
            with open(self.path, 'w', encoding='utf-8') as w:
                json.dump([], w)

    def read(self):
        """读取json文件

        :param: none
        :return: none
        """
        with open(self.path, mode='r', encoding='utf-8') as f:
            return json.load(f)

    def write(self, data):
        """覆盖写json文件

        :param: conf 覆盖数据，list或dict格式数据
        :return: none
        """
        with open(self.path, mode='w', encoding='utf-8') as f:
            json.dump(data, f)

    def add(self,item):
        """直接添加数据，不判断重复

        :param data:
        :return:
        """
        data = self.read()
        if isinstance(data,dict):
            self.write([data,item])
        else:
            data.append(item)
            self.write(data)

    def pich(self, item):
        """去重添加数据

        :param: 添加数据项
        :return: none
        """
        data = self.read()
        if item not in data:
            data.append(item)
            self.write(data)

    def drop(self, item):
        """删除数据

        :param: 添加数据项
        :return: none
        """
        data = self.read()
        if item in data:
            data.remove(item)
            self.write(data)


class DBIF:
    """
    数据库操作接口
    """

    def __init__(self):
        pass
