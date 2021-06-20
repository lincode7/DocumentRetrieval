# -*- coding: utf-8 -*-
import os, json, requests, time, datetime
from bs4 import BeautifulSoup


# 纯功能类，无需实例化
class somehelp:
    @classmethod
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

    @classmethod
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

    @classmethod
    def Generate_exist(cls, table, titles):
        """
            根据已有数据生成过滤表
        """
        for i in titles:
            if {'title': i} not in table:
                table.append({'title': i})
        return table

    @classmethod
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

    @classmethod
    def _orData(cls, *args):
        """
            第二次整理，处理数据的并集
            ：params 格式一致来源不同的数据
            ：return 整理后的数据
        """
        d = {}
        for one in args:
            input()

    @classmethod
    def _notData(cls, *args):
        input()

    @classmethod
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

    @classmethod
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

    @classmethod
    def replace_char(cls, old_string, char, index):
        '''
        字符串按索引位置替换字符
        '''
        old_string = str(old_string)
        # 新的字符串 = 老字符串[:要替换的索引位置] + 替换成的目标字符 + 老字符串[要替换的索引位置+1:]
        new_string = old_string[:index] + char + old_string[index + 1:]
        return new_string

    @classmethod
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

    @classmethod
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

    @classmethod
    def year(cls, date):
        return date.split('/')[0]

    @classmethod
    def month(cls, date):
        return date.split('/')[1]

    @classmethod
    def json_print(cls, *args):
        for one in args:
            js = json.dumps(one,
                            sort_keys=True,
                            indent=4,
                            separators=(',', ':'))
            print(js)


# os.path.abspath(os.path.dirname(cwd) + os.path.sep + ".")  # 得到父目录


# json保存数据模块
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


# jf = json_data(r'nature_result.json')
# n = jf.read()
# jf = json_data(r'pubs_result.json')
# p = jf.read()
# jf = json_data(r'science_result.json')
# s = jf.read()

# t = time.time()
# d = somehelp._finalData(n,p,s)
# t1 = time.time()
# print(t1-t)

# jf = json_data(r'final.json')
# jf.write(d)
# d = jf.read()

# t = time.time()
# d = somehelp.sortData(d, 1)
# t1 = time.time()
# print(t1-t)

# jf = json_data(r'sortfinal.json')
# jf.write(d)


# 爬虫访问模块
class HttpServer:
    def __init__(self):
        # '''
        # 初始化，建立session
        # :param: none
        # :return: none
        # '''
        self.s = requests.Session()
        self.s.trust_env = False  # 禁用对代理和证书捆绑包的环境搜索
        self.header = {
            'User-Agent':
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11',
            'Accept-Encoding': 'gzip, deflate',
            'accept': '*/*',
            'Connection': 'keep-alive',
            'content-type': 'application/json;charset=utf-8'
        }

    def GET(self, url, payload=None):
        # '''
        # get方法
        # :param: 请求链接，请求头，请求参数
        # :return: 响应信息
        # '''
        req = requests.Request(method='GET',
                               url=url,
                               params=payload,
                               headers=self.header)
        prepared = self.s.prepare_request(req)
        return self.s.send(prepared)

    def POST(self, url, _files=None, _data=None, payload=None, _json=None):
        # '''
        # post方法
        # :param: 请求链接，请求头，请求体
        # :return: 响应信息
        # '''
        req = requests.Request(method='POST',
                               url=url,
                               files=_files,
                               data=_data,
                               params=payload,
                               json=_json,
                               headers=self.header)
        prepared = self.s.prepare_request(req)
        return self.s.send(prepared)


# 搜索实现
class Nature(HttpServer, somehelp):
    url = 'https://www.nature.com'
    search = 'https://www.nature.com/search/ajax'
    nextpage = None

    def __init__(self):
        super(Nature, self).__init__()  # 父类初始化
        self.param = None  # 针对web格式化的查询词
        self.payload = None  # 外部查询词
        self.filter_table = None  # 标题过滤表

    def format_param(self):
        if 'keyword' in self.payload or 'author' in self.payload or 'title' in self.payload:  # 保证查询有效
            self.param = {}
            if 'keyword' in self.payload:  # 查询词存在全文关键词
                self.param['q'] = self.payload['keyword']
            if 'author' in self.payload:  # 查询词存在作者关键词
                self.param['author'] = self.payload['author']
            if 'title' in self.payload:  # 查询词存在标题关键词
                self.param['title'] = self.payload['title']
            if 'dateSt' in self.payload and 'dateEnd' in self.payload:  # 日期范围
                self.param['date_range'] = super().year(
                    self.payload['dateSt']) + '-' + super().year(
                        self.payload['dateEnd'])
            if 'order' in self.payload:  # 数据顺序
                if self.payload['order'] == 'relevance':
                    self.param['order'] = 'relevance'
                elif self.payload['order'] == 'oldest':
                    self.param['order'] = 'date_asc '
                elif self.payload['order'] == 'newest':
                    self.param['order'] = 'date_desc'
            # super().json_print(self.param)
        else:
            self.param = None

    def Search(self, payload, filter_table=[]):
        """
        发送请求爬取数据，包括标题，作者，出版时间，url
        :param payload: 搜索传入参数(必须)
        :param filter_table: 标题过滤表
        :return: 本次搜索结果
        """

        # 更新请求参数
        self.payload = payload
        self.format_param()
        if filter_table:  # 更新过滤表
            self.filter_table = filter_table

        data = {}  # 本次查询最终数据
        log = {}  # 从全文中整理出的一条数据
        if self.param:  # 查询参数传入正常
            # step1:send
            response = None
            if self.nextpage:  # 访问下一页
                response = super().GET(url=self.nextpage)
            else:  # 访问第一页
                response = super().GET(url=self.search, payload=self.param)
            response.encoding = 'utf-8'
            # step2:format_response
            soup = BeautifulSoup(response.text, 'lxml')
            ## 截取信息（不返回）
            if soup.find('h1', attrs={'data-test':
                                      'no-results'}):  # 本次访问没有数据，在第一次访问无数据时触发
                self.nextpage = None
                return data
            self.nextpage = soup.find('li', attrs={'data-page': 'next'})
            if 'disabled' in self.nextpage.attrs['class']:  # 没有下一页，在不断访问下一页时触发
                self.nextpage = None
            self.nextpage = self.url + self.nextpage.find('a').get('href')
            ## 截取返回数据
            article = soup.findAll('li', attrs={'class': 'mb20 pb20 cleared'})
            for one in article:
                log['title'] = one.find('a',
                                        attrs={
                                            'data-track-action':
                                            'search result'
                                        }).text.strip()
                if {
                        'title': log['title']
                } in self.filter_table:  # 该文章在过滤表或者结果表中就跳过
                    continue
                log['date'] = one.find('time',
                                       attrs={
                                           'itemprop': 'datePublished'
                                       }).text.strip()
                date_format = datetime.datetime.strptime(
                    log['date'], '%d %B %Y')  # '9 March 2021'
                log['date'] = datetime.datetime.strftime(
                    date_format, '%Y-%m-%d')  # '2021-03-09'
                log['url'] = self.url + str(
                    one.find('a', attrs={
                        'data-track-action': 'search result'
                    }).get('href'))
                log['author'] = ''
                if one.find(
                        'ul',
                        attrs=
                    {
                        'class':
                        'clean-list extra-tight-line-height inline-list text13 text-gray-light js-list-authors-3 mt4 mr0 mb1 ml0'
                    }) != None:
                    log['author'] = one.find(
                        'ul',
                        attrs={
                            'class':
                            'clean-list extra-tight-line-height inline-list text13 text-gray-light js-list-authors-3 mt4 mr0 mb1 ml0'
                        }).text.strip()
                data = super().AddOneData(data, log)  # 在原来结果上添加
                log = {}
            print('from {}'.format(self.url))
        return data

    def testparam(self, payl):
        self.payload = payl
        self.format_param()
        print('from {}'.format(self.url))
        super().json_print(self.param)


# n = Nature()
# _data = n.Search(
#     payload={'keyword': 'protein', 'page': 1, 'psize': 100, 'date': ['2021/01/28', '2021/03/28'], 'order': 'relevance'})
# outfile = json_data('nature_result.json')
# outfile.write(_data)


class Science(HttpServer, somehelp):
    url = 'https://www.sciencemag.org/'
    search = 'https://w35slb9cf3.execute-api.us-west-1.amazonaws.com/prod/search'

    def __init__(self):
        super(Science, self).__init__()  # 父类初始化
        self.param = None  # 针对web格式化的查询词
        self.payload = None  # 外部查询词
        self.filter_table = None  # 标题过滤表

    def format_param(self):
        if 'keyword' in self.payload or 'author' in self.payload or 'title' in self.payload:  # 保证查询有效
            self.param = {}
            if 'page' in self.payload:  # 请求页数
                self.param['page'] = self.payload['page']
            if 'psize' in self.payload:  # 请求单页数据量
                self.param['pagesize'] = self.payload['psize']
            if 'order' in self.payload:  # 数据顺序
                if self.payload['order'] == 'relevance':
                    self.param['orderby'] = 'tfidf'
                elif self.payload['order'] == 'oldest':
                    self.param['orderby'] = 'oldest  '
                elif self.payload['order'] == 'newest':
                    self.param['orderby'] = 'newest  '
            self.param['rules'] = []
            if 'keyword' in self.payload:  # 查询词存在全文关键词
                self.param['rules'].append({
                    'field': 'q',
                    'value': self.payload['keyword']
                })
            if 'author' in self.payload:  # 查询词存在作者关键词
                self.param['rules'].append({
                    'field': 'author_surnames',
                    'value': self.payload['author']
                })
            if 'title' in self.payload:  # 查询词存在标题关键词
                self.param['rules'].append({
                    'field': 'title',
                    'value': self.payload['title']
                })
            if 'dateSt' in self.payload and 'dateEnd' in self.payload:  # 日期范围
                self.param['rules'].append({
                    'field':
                    'pubdate',
                    'value': [
                        self.payload['dateSt'].replace('/', '-'),
                        self.payload['dateEnd'].replace('/', '-')
                    ]
                })
            # super().json_print(self.param)
        else:
            self.param = None

    def Search(self, payload, filter_table=[]):
        # '''
        # 发送请求爬取数据，包括标题，作者，出版时间，url，并保存到结果表
        # :param: 请求词，爬取结果表，过滤表
        # :return: 更新后的结果表
        # '''
        data = {}  # 本次查询最终数据
        log = {}  # 从全文中整理出的一条数据
        # 更新请求参数
        self.payload = payload
        self.format_param()
        if filter_table:  # 更新过滤表
            self.filter_table = filter_table
        if self.param:  # 查询参数传入正常
            # step1:send
            response = super().POST(url=self.search, _json=self.param)
            # step2:format_response
            data = json.loads(response.text)
            if data['found'] == 0:  # 访问下一页没有数据
                self.param = None
                return data
            self.param['page'] += 1
            article = data['hitlist']
            for one in article:
                log['title'] = one['title'][0]
                if {'title': log['title']} in self.filter_table:  # 该文章在过滤表中就跳过
                    continue
                log['date'] = one['pubdate'][0][:10]
                log['author'] = ''
                if 'authors' in one:
                    log['author'] = ', '.join(one['authors'])
                log['url'] = 'https:' + one['canonical_url'][0]
                # print(log)
                data = super().AddOneData(data, log)  # 在原来结果上添加
                log = {}
            print('from {}'.format(self.url))
        return data

    def testparam(self, payl):
        self.payload = payl
        self.format_param()
        print('from {}'.format(self.url))
        super().json_print(self.param)


# s = Science()
# data = s.Search(payload={'keyword': 'protein', 'page': 1, 'psize': 100, 'date': ['2021/01/28', '2021/03/28'], 'order': 'relevance'})
# outfile = json_data('science_result.json')
# outfile.write(data)


# 暂时不管
class Science2(HttpServer, somehelp):
    url = 'https://www.sciencedirect.com/'
    search = 'https://www.sciencedirect.com/search/'
    api = 'https://www.sciencedirect.com/search/api/'

    def __init__(self, filter_table=[]):
        super(Science2, self).__init__()  # 父类初始化
        self.param = None  # 针对web格式化的查询词
        self.payload = None  # 外部查询词
        self.havenext = True
        self.filter_table = filter_table
        # get token
        req = super().GET(url=self.search)
        req.encoding = 'utf-8'
        soup = BeautifulSoup(req.text, 'lxml')
        token = 'a'

    def format_param1(self):
        if self.payload:
            self.param = {}
            if 'page' in self.payload:  # 请求页数
                self.param['page'] = self.payload['page']
            if 'psize' in self.payload:  # 请求单页数据量
                self.param['pagesize'] = self.payload['psize']
            if 'order' in self.payload:  # 数据顺序
                if self.payload['order'] == 'newest':
                    self.param['sortBy'] = 'date'
            if 'keyword' in self.payload:  # 查询词存在全文关键词
                self.param['qs'] = self.payload['keyword']
            if 'author' in self.payload:  # 查询词存在作者关键词
                self.param['authors'] = self.payload['author']
            if 'title' in self.payload:  # 查询词存在标题关键词
                self.param['title'] = self.payload['title']
            if 'date' in self.payload:  # 日期范围
                self.param['date'] = super().year(
                    self.payload['date'][0]) + '-' + super().year(
                        self.payload['date'][1])
            print(self.param)

    def format_param2(self, token):
        self.param['t'] = token
        self.param['hostname'] = 'www.sciencedirect.com'

    def Search(self, payload={}, filter_table=[], search_result={}):
        # '''
        # 发送请求爬取数据，包括标题，作者，出版时间，url，并保存到结果表
        # :param: 请求词，爬取结果表，过滤表
        # :return: 更新后的结果表
        # '''
        data = {}  # 本次查询最终数据
        log = {}  # 从全文中整理出的一条数据

        if search_result == {}:  # 新的一次搜索
            self.havenext = True
        if self.havenext:
            if payload:  # 更新请求参数
                self.payload = payload
                self.format_param1()
            if filter_table:  # 更新过滤表
                self.filter_table = filter_table
            if self.param:  # 查询参数传入正常
                if search_result:  # 存在历史查询数据
                    self.filter_table = super().Generate_exist(
                        self.filter_table,
                        search_result['title'])  # 把历史查询数据加入到过滤表中
                # step1:send
                response = super().GET(url=self.search, _json=self.param)
                # step2:format_response
                data = json.loads(response.text)

                print('from {}'.format(self.url))
        return data


# s = Science2()
# data = s.Search(payload={'keyword': 'protein',"psize":100})
# outfile = json_data('science_result.json')
# outfile.write(data)


class Pubs(HttpServer, somehelp):
    url = 'https://pubs.acs.org/'
    search = 'https://pubs.acs.org/action/doSearch'
    nextpage = None

    def __init__(self):
        super(Pubs, self).__init__()  # 父类初始化
        self.param = None  # 针对web格式化的查询词
        self.payload = None  # 外部查询词
        self.filter_table = None  # 标题过滤表

    def format_param(self):
        if 'keyword' in self.payload or 'author' in self.payload or 'title' in self.payload:  # 保证查询有效
            self.param = {}
            i = 0
            # if 'page' in self.payload:  # 请求页数
            #     self.param['startPage'] = self.payload['page'] - 1
            if 'psize' in self.payload:  # 请求单页数据量
                self.param['pageSize'] = self.payload['psize']
            if 'keyword' in self.payload:  # 查询词存在全文关键词
                self.param['field' + str(i + 1)] = 'AllField'
                self.param['text' + str(i + 1)] = self.payload['keyword']
                i += 1
            if 'author' in self.payload:  # 查询词存在作者关键词
                self.param['field' + str(i + 1)] = 'Contrib'
                self.param['text' + str(i + 1)] = self.payload['author']
                i += 1
            if 'title' in self.payload:  # 查询词存在标题关键词
                self.param['field' + str(i + 1)] = 'Title'
                self.param['text' + str(i + 1)] = self.payload['title']
                i += 1
            if 'dateSt' in self.payload and 'dateEnd' in self.payload:  # 日期范围
                self.param['AfterMonth'] = super().month(
                    self.payload['dateSt'])
                self.param['AfterYear'] = super().year(self.payload['dateSt'])
                self.param['BeforeMonth'] = super().month(
                    self.payload['dateEnd'])
                self.param['BeforeYear'] = super().year(
                    self.payload['dateEnd'])
            if 'order' in self.payload:  # 数据顺序
                if self.payload['order'] == 'newest':
                    self.param['sortBy'] = 'Earliest'
                elif self.payload['order'] == 'oldest':
                    self.param['sortBy'] = 'Earliest_asc'
            self.param['accessType'] = 'allContent'
            # super().json_print(self.param)
        else:
            self.param = None

    def Search(self, payload, filter_table=[]):
        # '''
        # 发送请求爬取数据，包括标题，作者，出版时间，url，并保存到结果表
        # :param: 请求词，爬取结果表，过滤表
        # :return: 更新后的结果表
        # '''
        data = {}  # 本次查询最终数据
        log = {}  # 从全文中整理出的一条数据

        # 更新请求参数
        self.payload = payload
        self.format_param()
        if filter_table:  # 更新过滤表
            self.filter_table = filter_table
        if self.param:  # 查询参数传入正常
            # step1:send
            response = None
            if self.nextpage:  # 访问下一页
                response = super().GET(url=self.nextpage)
            else:  # 访问第一页
                response = super().GET(url=self.search, payload=self.param)
            response.encoding = 'utf-8'
            # step2:format_response
            soup = BeautifulSoup(response.text, 'lxml')
            ## 截取信息（不返回）
            if soup.find('div', attrs={'class': 'search-result__no-result'
                                       }):  # 没有数据，下一页同样无效，在访问第一页或不断访问下一页时触发
                self.nextpage = None
            self.nextpage = soup.find('a', title={
                'title': 'Next Page'
            }).get('href')
            ## 截取返回数据
            article = soup.findAll('div',
                                   attrs={'class': 'issue-item clearfix'})
            for one in article:
                log['title'] = one.find('span', attrs={
                    'class': 'hlFld-Title'
                }).text.strip()
                if {
                        'title': log['title']
                } in self.filter_table:  # 该文章在过滤表或者结果表中就跳过
                    continue
                log['date'] = one.find('span',
                                       attrs={
                                           'class': 'pub-date-value'
                                       }).text.strip()
                date_format = datetime.datetime.strptime(
                    log['date'], '%B %d, %Y')  # 'March 9, 2021'
                log['date'] = datetime.datetime.strftime(
                    date_format, '%Y-%m-%d')  # '2021-03-09'
                log['url'] = self.url + 'doi/' + one.find(
                    'span', attrs={
                        'class': 'issue-item_doi'
                    }).text.strip()[5:]
                log['author'] = one.find('ul', attrs={
                    'aria-label': 'author'
                }).text.strip()
                data = super().AddOneData(data, log)  # 在原来结果上添加
                log = {}
            print('from {}'.format(self.url))
        return data

    def testparam(self, payl):
        self.payload = payl
        self.format_param()
        print('from {}'.format(self.url))
        super().json_print(self.param)


# s = Pubs()
# data = s.Search(payload={'keyword': 'protein', 'page': 1, 'psize': 100, 'date': ['2021/01/28', '2021/03/28'], 'order': 'relevance'})
# outfile = json_data('pubs_result.json')
# outfile.write(data)


class SpLink(HttpServer, somehelp):
    url = 'https://link.springer.com/'
    search = 'https://link.springer.com/search/'
    nextpage = None

    def __init__(self):
        super(SpLink, self).__init__()
        self.param = None  # 针对web格式化的查询词
        self.payload = None  # 外部查询词
        self.filter_table = None  # 标题过滤表

    def format_param(self):
        if 'keyword' in self.payload or 'author' in self.payload or 'title' in self.payload:  # 保证查询有效
            self.param = {}
            if 'keyword' in self.payload:  # 查询词存在全文关键词
                self.param['query'] = self.payload['keyword']
            if 'author' in self.payload:  # 查询词存在作者关键词
                self.param['dc.creator'] = self.payload['author']
            if 'title' in self.payload:  # 查询词存在标题关键词
                self.param['dc.title'] = self.payload['title']
            if 'dateSt' in self.payload and 'dateEnd' in self.payload:  # 日期范围
                self.param['date-facet-mode'] = 'between'
                self.param['facet-start-year'] = super().year(
                    self.payload['dateSt'])
                self.param['facet-end-year'] = super().year(
                    self.payload['dateEnd'])
            if 'order' in self.payload:  # 数据顺序
                if self.payload['order'] == 'newest':
                    self.param['sortOrder'] = 'newestFirst'
                elif self.payload['order'] == 'oldest':
                    self.param['sortOrder'] = 'oldestFirst'
            self.param['showAll'] = 'true'
            # super().json_print(self.param)
        else:
            self.param = None

    def Search(self, payload, filter_table=[]):
        # '''
        # 发送请求爬取数据，包括标题，作者，出版时间，url，并保存到结果表
        # :param: 请求词，爬取结果表，过滤表
        # :return: 更新后的结果表
        # '''
        data = {}  # 本次查询最终数据
        log = {}  # 从全文中整理出的一条数据

        # 更新请求参数
        self.payload = payload
        self.format_param()
        if filter_table:  # 更新过滤表
            self.filter_table = filter_table
        if self.param:  # 查询参数传入正常
            # step1:send
            response = None
            if self.nextpage:  # 已知下一页链接，直接访问
                response = super().GET(url=self.nextpage)
                if response.status_code == 410:  # 访问下一页可能会出现网页被删除的提示
                    self.nextpage = None
                    self.havenext = False
                    return data
            else:  # 访问第一页，不知道下一页链接
                response = super().GET(url=self.search, payload=self.param)
            response.encoding = 'utf-8'
            # step2:format_response
            soup = BeautifulSoup(response.text, 'lxml')
            ## 截取信息（不返回）
            if soup.find('div', attrs={'id': 'no-results-message'
                                       }):  # 本次访问没有数据，在第一次访问无数据时触发
                self.nextpage = None
                return data
            self.nextpage = self.url + soup.find('link', attrs={
                'rel': 'next'
            }).get('href')
            ## 截取返回数据
            article = soup.find('ol', attrs={'id': 'results-list'})
            article = article.findAll('li')
            for one in article:
                log['title'] = one.find('a', attrs={'class': 'title'}).text
                if {
                        'title': log['title']
                } in self.filter_table:  # 该文章在过滤表或者结果表中就跳过
                    continue
                log['date'] = one.find('span', attrs={
                    'class': 'year'
                }).text[1:5]
                log['url'] = self.url + one.find('a', attrs={
                    'class': 'title'
                }).get('href')
                if one.find('span', attrs={'class': 'authors'}):
                    log['author'] = one.find('span',
                                             attrs={
                                                 'class': 'authors'
                                             }).text
                else:
                    log['author'] = ''
                data = super().AddOneData(data, log)  # 在原来结果上添加
                log = {}
            print('from {}'.format(self.url))
        return data

    def testparam(self, payl):
        self.payload = payl
        self.format_param()
        print('from {}'.format(self.url))
        super().json_print(self.param)


# s = SpLink()
# data = s.Search(payload={'keyword': 'protein', 'page': 1, 'psize': 100, 'date': ['2021/01/28', '2021/03/28'], 'order': 'relevance'})
# outfile = json_data('spLink_result.json')
# outfile.write(data)


class Tandf(HttpServer, somehelp):
    url = 'https://www.tandfonline.com/'
    search = 'https://www.tandfonline.com/action/doSearch/'
    nextpage = None

    def __init__(self):
        super(Tandf, self).__init__()
        self.param = None  # 针对web格式化的查询词
        self.payload = None  # 外部查询词
        self.filter_table = None  # 标题过滤表

    def format_param(self):
        if 'keyword' in self.payload or 'author' in self.payload or 'title' in self.payload:  # 保证查询有效
            self.param = {}
            i = 0
            if 'keyword' in self.payload:  # 查询词存在全文关键词
                self.param['field' + str(i + 1)] = 'Keyword'
                self.param['text' + str(i + 1)] = self.payload['keyword']
                i += 1
            if 'author' in self.payload:  # 查询词存在作者关键词
                self.param['field' + str(i + 1)] = 'Contrib'
                self.param['text' + str(i + 1)] = self.payload['author']
                i += 1
            if 'title' in self.payload:  # 查询词存在标题关键词
                self.param['field' + str(i + 1)] = 'Title'
                self.param['text' + str(i + 1)] = self.payload['title']
                i += 1
            if 'dateSt' in self.payload and 'dateEnd' in self.payload:  # 日期范围
                self.param['AfterYear'] = super().year(self.payload['dateSt'])
                self.param['BeforeYear'] = super().year(
                    self.payload['dateEnd'])
            if 'psize' in self.payload:
                self.param['pageSize'] = self.payload['psize']
            # super().json_print(self.param)
        else:
            self.param = None

    def Search(self, payload, filter_table=[]):
        # '''
        # 发送请求爬取数据，包括标题，作者，出版时间，url，并保存到结果表
        # :param: 请求词，爬取结果表，过滤表
        # :return: 更新后的结果表
        # '''
        data = {}  # 本次查询最终数据
        log = {}  # 从全文中整理出的一条数据

        # 更新请求参数
        self.payload = payload
        self.format_param()
        if filter_table:  # 更新过滤表
            self.filter_table = filter_table
        if self.param:  # 查询参数传入正常
            # step1:send
            response = None
            if self.nextpage:  # 已知下一页链接，直接访问
                response = super().GET(url=self.nextpage)
                if response.status_code == 410:  # 访问下一页可能会出现网页被删除的提示
                    self.nextpage = None
                    self.havenext = False
                    return data
            else:  # 访问第一页，不知道下一页链接
                response = super().GET(url=self.search, payload=self.param)
            response.encoding = 'utf-8'
            # step2:format_response
            soup = BeautifulSoup(response.text, 'lxml')
            ## 截取信息（不返回）
            if soup.find('div', attrs={'class': 'noSearchResultsDropZone'
                                       }):  # 本次访问没有数据，在第一次访问无数据时触发
                self.nextpage = None
                return data
            self.nextpage = self.url + soup.find('a',
                                                 attrs={
                                                     'class': 'nextPage'
                                                 }).get('href')
            ## 截取返回数据
            article = soup.findAll('article',
                                   attrs={'class': 'searchResultItem'})
            for one in article:
                log['title'] = one.get('data-title')
                if {
                        'title': log['title']
                } in self.filter_table:  # 该文章在过滤表或者结果表中就跳过
                    continue
                log['url'] = self.url + one.find('a',
                                                 attrs={
                                                     'class': 'ref nowrap'
                                                 }).get('href')
                aud = one.find('div', attrs={'class': 'searchentryright'})
                log['author'] = aud.find('div', attrs={'class': 'author'}).text
                log['date'] = aud.find('span',
                                       attrs={
                                           'class': 'publication-year'
                                       }).text[-11:]
                date_format = datetime.datetime.strptime(
                    log['date'], '%d %b %Y')  # '9 March 2021'
                log['date'] = datetime.datetime.strftime(
                    date_format, '%Y-%m-%d')  # '2021-03-09'
                data = super().AddOneData(data, log)  # 在原来结果上添加
                log = {}
            print('from {}'.format(self.url))
        return data

    def testparam(self, payl):
        self.payload = payl
        self.format_param()
        print('from {}'.format(self.url))
        super().json_print(self.param)


# s = Tandf()
# data = s.Search(
#     payload={'keyword': 'protein', 'psize': 100, 'date': ['2021/01/28', '2021/03/28'], 'order': 'relevance'})
# outfile = json_data('spLink_result.json')
# outfile.write(data)
