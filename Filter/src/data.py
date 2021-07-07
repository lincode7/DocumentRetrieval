# -*- coding: utf-8 -*-
import os, json, requests, time, datetime
from bs4 import BeautifulSoup
from Filter.src.otherfuc import *

class json_data:
    # """
    # log.json文件保存过滤表
    # """
    def __init__(self, FName="log.json"):
        # """
        # 初始化文件指针
        # :param: FName: 文件名
        # :return: none
        # """
        cwd = os.getcwd()
        self.file_path = os.path.join(cwd, 'json', FName)

        with open(self.file_path, mode='a', encoding='utf-8') as f:
            if os.path.getsize(self.file_path) == 0:
                json.dump([], f)

    def read(self):
        # """
        # 读取json文件
        # :param: none
        # :return: none
        # """
        with open(self.file_path, mode='r', encoding='utf-8') as f:
            return json.load(f)

    def write(self, data):
        # """
        # 覆盖json文件
        # :param: data 覆盖数据，list或dict格式数据
        # :return: none
        # """
        with open(self.file_path, mode='w', encoding='utf-8') as f:
            json.dump(data, f)

    def pich(self, item):
        # """
        # 添加数据
        # :param: 添加数据项
        # :return: none
        # """
        data = self.read()
        if item not in data:
            data.append(item)
            self.write(data)

    def drop(self, item):
        # """
        # 删除数据
        # :param: 添加数据项
        # :return: none
        # """
        data = self.read()
        if item in data:
            data.remove(item)
            self.write(data)


