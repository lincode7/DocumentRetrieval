# -*- coding: utf-8 -*-
import json


def Mergelist(cls, *args):
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


def Mergedict(cls, *args):
    # """
    # 简单的字典合并，相同保留，不同加入，理想上A，B同k的v数据类型要一致，不一致也能加入就是了
    # :params: A，结果字典，B，被并入的字典
    # :return: A
    # """
    # print('before:',A,'+',B)'
    m = {}
    for one in args:
        for k, v in one.items():
            if k not in m.keys():
                m[k] = v
            else:
                m[k] = cls().Mergelist(m[k], v)
    return m


def Generate_exist(cls, table, titles):
    """
        根据已有数据生成过滤表
    """
    for i in titles:
        if {'title': i} not in table:
            table.append({'title': i})
    return table


def AddOneData(cls, Out, In):
    """
     初步整理爬取数据，每次加入一条数据，只用在src.search()中
     -param Out:list,前一次的结果，
     -param In:dict,本次加入的一条数据
     -return Out:结果
    """
    if Out == {}:
        Out = In
    elif In['title'] not in Out['title']:
        for k in Out.keys():
            Out[k] = cls().Mergelist(Out[k], In[k])
    elif In['u'] not in Out['u']:
        if len(Out['title']) > 1:
            index = list(Out['title']).index(In['title'])
            Out['u'][index] = cls().Mergelist(Out['u'][index], In['u'])
    elif len(Out['title']) == 1:
        Out['u'] = cls().Mergelist(Out['u'], In['u'])
    return Out


@classmethod
def _andData(cls, key, *args):
    """
        第二次整理，处理数据的交集
        ：params 格式一致来源不同的数据
        ：return 整理后的数据
    """
    d = {}
    all = cls().Mergedict(args)  # 未整合的所有数据
    same = args[0][key]
    for one in args[1:]:  # 找出对key列表进行与的结果
        same = set(same) & set(one[key])
    for i in list(same):
        index = all[key].index(i)  # 在所有数据中找到一条and数据的位置
        for k in all.keys():  # 添加一条结果数据
            d = cls().Mergedict(d, {key: all[key][index]})


def _orData(cls, *args):
    """
        第二次整理，处理数据的并集
        ：params 格式一致来源不同的数据
        ：return 整理后的数据
    """
    d = {}
    for one in args:
        input()


def _notData(cls, *args):
    input()


def _finalData(cls, *args):
    """
        最后一次整理数据，合并不同网页来源数据
        ：params 格式一致来源不同的数据
        ：return 整理后的数据
    """
    d = {}
    for one in args:
        if d:  # d不空，去重整合url
            # step1 从几次搜索结果去除重复的
            same = list(set(list(d['title'])) & set(list(one['title'])))
            not_in_d = list(
                set(list(one['title'])) - set(list(d['title'])))
            not_in_d.sort(key=one['title'].index)
            for i in same:  # 存在相同文章，整合url
                index_d = d['title'].index(i)
                index_one = one['title'].index(i)
                d['url'][index_d] = cls().Mergelist(
                    d['url'][index_d], one['url'][index_one])
            for i in not_in_d:  # 存在新文章，直接加入
                index_one = one['title'].index(i)
                d['title'].append(one['title'][index_one])
                d['author'].append(one['author'][index_one])
                d['date'].append(one['date'][index_one])
                d['url'].append(one['url'][index_one])
        else:  # d空就直接放进去
            d = one
    return d


def sortData(cls, data, order_res=False):
    """
    如果需要对最终结果排序
    :param data:
    :param order_res: F日期正序，T日期逆序
    :return:
    """
    o = {}
    zipped = zip(data['title'], data['author'], data['date'], data['url'])
    sortzip = sorted(zipped, key=lambda x: (x[3], x[0]), reverse=order_res)
    result = zip(*sortzip)
    t, a, d, u = [list(x) for x in result]
    o['title'] = t
    o['author'] = t
    o['date'] = t
    o['url'] = t
    return o


def replace_char(cls, old_string, char, index):
    '''
    字符串按索引位置替换字符
    '''
    old_string = str(old_string)
    # 新的字符串 = 老字符串[:要替换的索引位置] + 替换成的目标字符 + 老字符串[要替换的索引位置+1:]
    new_string = old_string[:index] + char + old_string[index + 1:]
    return new_string


def remove_empty(cls, dictA):
    '''
    fuc： 去除空键
    param： 一个字典，或者是一个字典列表
    return： 去除空键的字典
    '''
    if isinstance(dictA, dict):
        for key in list(dictA.keys()):
            if not dictA.get(key):
                del dictA[key]
    if isinstance(dictA, list):
        i = 0
        for one in list(dictA):
            if not isinstance(one, dict):
                break
            else:
                for key in one.keys():
                    if not dictA[i].get(key):  # noe与dictA对应一致
                        dictA.remove(one)
                        i = i - 1
                i = i + 1
    return dictA


def compare_date(cls, date1, date2):
    if '/' in date1:
        date1 = date1.split('/')
    if '-' in date1:
        date1 = date1.split('-')
    if '/' in date2:
        date2 = date2.split('/')
    if '-' in date2:
        date2 = date2.split('-')

    for i, j in zip(date1, date2):
        if i < j:
            return False
        elif i == j:
            continue
        else:
            return True
    return True


def year(cls, date):
    return date.split('/')[0]


def month(cls, date):
    return date.split('/')[1]


def json_print(cls, *args):
    for one in args:
        js = json.dumps(one,
                        sort_keys=True,
                        indent=4,
                        separators=(',', ':'))
        print(js)
        return js
