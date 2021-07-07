# -*- coding: utf-8 -*-
import sys, time, threading, datetime
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

