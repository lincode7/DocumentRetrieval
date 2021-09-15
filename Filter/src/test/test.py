# -*- coding: utf-8 -*-
import json
import re
import sys, time, threading, datetime, copy
from threading import Thread


def threadjointest():
    st_time = time.time()
    t = []
    for i in range(10):
        a = Thread(target=test(i))
        a.setDaemon(True)
        a.start()
        t.append(a)
    for i in t:
        i.join()
    print('主线程结束！', threading.current_thread().name)
    print('一共用时：', time.time() - st_time)


def test(q):
    time.sleep(1)
    print(q)


# threadjointest()


def Mergelist(*args):
    # """
    # 合并list，不同项合并为list
    # :params: 一个或多个待合并数据
    # :return: 合并结果m
    # """
    m = []
    for one in args:
        if isinstance(one, list):
            m += one
            s = list(set(m))
            s.sort(key=m.index)
            m = s
        elif one not in m:
            m.append(one)
    return m


def Mergedict(*args):
    # """
    # 简单的字典合并，相同保留，不同加入，理想上A，B同k的v数据类型要一致，不一致也能加入就是了
    # :params: A，结果字典，B，被并入的字典
    # :return: A
    # """
    # print('before:',A,'+',B)'
    m = {}
    for one in args:
        for k, v in dict(one).items():
            if k not in m.keys():
                m[k] = v
            else:
                m[k] = Mergelist(m[k], v)
    return m


def _and(key, *args):
    d = {}
    all = Mergedict(args)
    print(all)
    same = args[0][key]
    for one in args[1:]:
        same = list(set(same) & set(one[key]))
    print(same)
    for i in same:
        index = all[key].index(i)  # 在所有数据中找到一条and数据的位置
        for k in all.keys():  # 添加一条结果数据
            d = Mergedict(d, {key: all[key][index]})


# for i in range(2,9,1):
#     print(i)

def del_key():
    a = {"A": 1, "B": 2}
    del a["A"]
    print(a)


def copytest():
    class A:
        def __init__(self):
            self.a = 1
            self.b = 2

    a = A()
    b = copy.deepcopy(a)
    a.a = 2
    a.b = 1
    print(a.a, a.b, '\n', b.a, b.b)


def formatdate(date, fmt):
    return datetime.datetime.strptime(date, "")

# 统一参数
payload = {
    "keyword": "protein",
    "title": "123",
    "author": "me",
    "date": ["2021/07/19", "2021/09/10"]
}
# 参数格式化json逻辑
_payload1 = {
    "keyword": "q:",
    "title": "title:",
    "author": "author:",
    "date": "date_range:yyyy-yyyy"
}
_payload2 = {
    "keyword": "qs:",
    "title": "title:",
    "author": "authors:",
    "date": "affiliations:yyyy-yyyy"
}
_payload3 = {
    "keyword": "rules:[field:q,value:]",
    "title": "rules:[field:title,value:]",
    "author": "rules:[field:author_surnames,value:]",
    "date": "rules:[field:pubdate,value:[yyyy-mm-dd,yyyy-mm-dd]]"
}



class str_dict:
    reg1 = '(\w+):?(.*?)?'  # 匹配单键值字典字符串  “key:value”
    reg2 = '(?:,?([^:^,]+):?([^:^,]+)?,?)+?'  # 匹配多键值字典字符串  “key1:value1,key2:value2,key3:value3”

    @classmethod
    def simple_str_to_dict(cls, s: str=None) -> dict:
        '''一对键值的字符串转字典,

        :param s: 字符串字典，例“key:value”
        :return: 从字符串翻译的对象

        - 基本操作
        >>> obj = str_dict.simple_str_to_dict("tag:animal")
        '''

        k, val = re.match(cls.reg1, s).groups() or None
        if k and val:
            return {k: val}
        return None

    @classmethod
    def simple_str_to_dict_with_value(cls, s: str, value: str=None) -> dict:
        '''一对键值的字符串转字典,可以修改@value定位的键值

        :param s: 字符串字典，支持缺省，例“key:@value” | “key:” | “key”
        :param value: 替换键值 value替换@value
        :return: 从字符串翻译的对象

        - 基本操作
        >>> obj = str_dict.simple_str_to_dict_with_value("tag:animal")
        >>> obj = str_dict.simple_str_to_dict_with_value("a:@value","name")
        >>> obj = str_dict.simple_str_to_dict_with_value("1:@value","name")
        >>> obj = str_dict.simple_str_to_dict_with_value("a_1:@value","name")
        >>> obj = str_dict.simple_str_to_dict_with_value("a-1:@value","name")
        >>> obj = str_dict.simple_str_to_dict_with_value("tag:","name")
        >>> obj = str_dict.simple_str_to_dict_with_value("tag","name")
        '''

        k, v = re.match(cls.reg1, s).groups()
        if k and v!=None:
            return {k: value or ""}
        return None

    @classmethod
    def little_complex_str_to_dict(cls, s: str, value: str=None) -> dict:
        '''多对键值的字符串转字典,可以修改@value定位的键值

        :param s:  字符串字典，支持缺省，例“key1:value，key2:value，key3:@value”
        :param value: 替换键值 value替换@value
        :return: 从字符串翻译的对象

        - 基本操作
        >>> # 完整字典字符串字典化
        >>> obj = str_dict.little_complex_str_to_dict("tag:animal,gender:0,name:cat",None)
        >>> # 不完整字典字符串缺值字典化
        >>> obj = str_dict.little_complex_str_to_dict("tag:animal,gender:0,name:@value",None)
        >>> # obj = str_dict.little_complex_str_to_dict("tag:animal,name:@value,gender:0",None)
        >>> # obj = str_dict.little_complex_str_to_dict("name:@value,tag:animal,gender:0",None)
        >>> # 不完整字典字符串赋值字典化
        >>> obj = str_dict.little_complex_str_to_dict("tag:animal,gender:0,name:@value","cat")
        >>> # obj = str_dict.little_complex_str_to_dict("tag:animal,name:@value,gender:0","cat")
        >>> # obj = str_dict.little_complex_str_to_dict("name:@value,tag:animal,gender:0","cat")
        >>> # 不完整字典字符串赋值字典化，赋值定位词@value缺省
        >>> obj = str_dict.little_complex_str_to_dict("tag:animal,gender:0,name:","cat")
        >>> # obj = str_dict.little_complex_str_to_dict("tag:animal,name:,gender:0","cat")
        >>> # obj = str_dict.little_complex_str_to_dict("name:,tag:animal,gender:1","cat")
        >>> # 不完整字典字符串赋值字典化，赋值定位词@value与键值分隔符:缺省
        >>> obj = str_dict.little_complex_str_to_dict("tag:animal,gender:0,name", "cat")
        >>> # obj = str_dict.little_complex_str_to_dict("tag:animal,name,gender:0", "cat")
        >>> # obj = str_dict.little_complex_str_to_dict("name,tag:animal,gender:0", "cat")
        '''

        L = re.findall(cls.reg2, s)
        obj = {}
        for (k,v) in L:
            if k and v!=None:
                if v in  ['@value','']:
                    obj[k] = value or ""
                else:
                    obj[k] = v
        return obj or None

    @classmethod
    def complex_str_to_dict(cls, s:str, value:object=None) -> object:
        '''多对键值的字符串转字典,可以修改@value定位的键值

        :param s:  字符串字典，支持缺省，例“key1:value，key2:value，key3:@value”
        :param value: 替换键值 value替换@value, value可能是字符串、列表、字典等
        :return: 从字符串翻译的对象

        - 基本操作
        '''

        L = re.findall(cls.reg2, s)
        obj = {}
        for (k, v) in L:
            if k and v:
                if v in  ['@value','']:
                    obj[k] = cls.complex_str_to_dict(value, None) # 如果value可以转化成字符串
                else:
                    obj[k] = v
            # elif k and v and value==None:

        return obj or None




