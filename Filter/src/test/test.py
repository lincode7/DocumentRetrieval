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
    print(a.a, a.b, '\n',b.a, b.b)

def formatdate(date, fmt):
    return datetime.datetime.strptime(date, "")

def paramsformat_test(payload: dict, _payload: dict) -> dict:
    def f(obj, fmt) -> object:
        if obj and fmt:
            rg = '(?:\[)?(.*)(?:\])?'
            reg = '(?:\[)?((\w+):(.*)?)+(?:\])?'
            print(re.match(rg, fmt).groups())
            if isinstance(obj, list):
                pass
            elif isinstance(obj, str):
                pass
        return None

    params = {}
    for key in _payload.keys():
        # 从字符串中截取出转化的键与值的格式化模型
        reg = '(\w+):(.*)?'
        k, fmt = re.match(reg, _payload[key]).groups()
        # print(k, fmt)
        params[k] = f(payload[key], fmt) or payload[key]
        # return params
    pass


# 统一参数
payload = {
    "keyword": "protein",
    "title": "123",
    "author": "me",
    "date": ["2021/07/19","2021/09/10"]
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

paramsformat_test(payload, _payload1)
paramsformat_test(payload, _payload2)
paramsformat_test(payload, _payload3)



