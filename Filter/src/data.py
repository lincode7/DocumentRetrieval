# -*- coding: utf-8 -*-
import os, sqlite3
from Filter.src.otherfuc import *

class JSONIF:
    """
    json文件操作接口，支持创建，读取，覆盖，增加，删除
    :param: FName: 文件名，默认log文件
    :return: none
    """
    def __init__(self, FName="log.json"):
        cwd = os.getcwd()
        self.file_path = os.path.join(cwd, 'json', FName)
        # 文件不在就创建
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

    def write(self, data:dict):
        # """
        # 覆盖json文件
        # :param: data 覆盖数据，list或dict格式数据
        # :return: none
        # """
        with open(self.file_path, mode='w', encoding='utf-8') as f:
            json.dump(data, f)

    def pich(self, item:dict):
        # """
        # 添加数据
        # :param: 添加数据项
        # :return: none
        # """
        data = self.read()
        if item not in data:
            data.append(item)
            self.write(data)

    def drop(self, item:dict):
        # """
        # 删除数据
        # :param: 添加数据项
        # :return: none
        # """
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
