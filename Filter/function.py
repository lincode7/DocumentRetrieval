# -*- coding: utf-8 -*-
import os, json

import requests
from bs4 import BeautifulSoup


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
        self.file_path = os.path.join(cwd, 'json\\' + FName)

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


# 数据合并,纯功能，无初始化
class Mergedata:
    def tolist(self, variable):
        # """
        # 数据类型转换，转换为list类型数据
        # :params: variable，变量名
        # :return: variable
        # """
        if isinstance(variable, list):
            return variable
        temp = variable
        variable = []
        variable.append(temp)
        return variable

    def Mergelist(self, box, item):
        # """
        # 合并入list，不同项合并为list，带去重判断
        # :params: box，合并结果 item，被并入项
        # :return: box
        # """
        if type(box) != list and item != box:
            box = self.tolist(box)
            box.append(item)
        if isinstance(box, list) and item not in box:
            box.append(item)
        return box

    def Mergedict(self, A, B):
        # """
        # 简单的字典合并，相同保留，不同加入，理想上A，B同k的v数据类型要一致，不一致也能加入就是了
        # :params: A，结果字典，B，被并入的字典
        # :return: A
        # """
        # print('before:',A,'+',B)
        for k, v in B.items():
            if k not in A.keys():
                A[k] = v
            else:
                A[k] = self.Mergelist(A[k], v)
        # print('after:',A)
        return A

    def EMergedict(self, A={}, B={}):
        # """
        # 字典数据合并，B合并进入A
        # dataA_format = {                  dataB_format = {
        #     'title': ['','','',```],          'title': '',
        #     'author': [[],[],[],```],         'author': [],
        #     'date': ['','','',```],           'date': '',
        #     'url': [[],[],[],```],            'url': '',
        # }                                 }
        # :params: 字典A，B
        # """
        if 'title' not in A.keys():
            A = {'title': [],
                 'author': [], 'date': [],
                 'url': []}
        # print('before:',A,'+',B)
        # B在A中没有相同文章数据
        if B['title'] not in A['title']:
            A['title'].append(B['title'])
            A['date'].append(B['date'])
            A['author'].append(B['author'])
            A['url'].append(B['url'])
        # B在A中有相同文章数据，但url不同
        else:
            BinA = A['title'].index(B['title'])
            A['url'][BinA] = self.Mergelist(A['url'][BinA], B['url'])
        # print('after:',A)
        return A

    def replace_char(old_string, char, index):
        '''
        字符串按索引位置替换字符
        '''
        old_string = str(old_string)
        # 新的字符串 = 老字符串[:要替换的索引位置] + 替换成的目标字符 + 老字符串[要替换的索引位置+1:]
        new_string = old_string[:index] + char + old_string[index + 1:]
        return new_string


# 爬虫访问模块
class HttpServer:
    def __init__(self):
        # '''
        # 初始化，建立session
        # :param: none
        # :return: none
        # '''
        self.s = requests.Session()
        self.req = None
        self.prepared = self.prepared = requests.Request(headers=[{
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11'},
            {'Accept-Encoding': 'gzip, deflate'}, {'accept': '*/*'}, {'Connection': 'keep-alive'},
            {'content-type': 'application/json;charset=utf-8'}, ])

    def GET(self, url, payload=None):
        # '''
        # get方法
        # :param: 请求链接，请求头，请求参数
        # :return: 响应信息
        # '''
        return self.s.get(url=url, params=payload)

    def POST(self, url, files=None, data=None, payload=None, json=None):
        # '''
        # post方法
        # :param: 请求链接，请求头，请求体
        # :return: 响应信息
        # '''
        return self.s.post(url=url, files=files, data=data,
                           params=payload, json=json)

    def pretty_print_request(self, request):
        # '''
        # 格式化打印请求头
        # :param: 请求头
        # :return: none
        # '''
        text = '{}\n{}\r\n{}\r\n{}\r\n'.format(
            '-----------Requests-----------',
            'url:' + request.url,
            request,
            '\r\n'.join('{}: {}'.format(k, v) for k, v in request.headers.items()),
        )
        print(text)

    def pretty_print_response(self, request):
        # '''
        # 格式化打印响应
        # :param: 请求头
        # :return: none
        # '''
        text = '{}\n{}\r\n{}\r\n'.format(
            '-----------Response-----------',
            request,
            '\r\n'.join('{}: {}'.format(k, v) for k, v in request.headers.items()),
        ) + '\r\n-----------Body-----------\r\n' + request.content.decode('utf-8')
        print(text)


# 搜索实现
class Nature(HttpServer, Mergedata):
    # web1,从nature获取,一次50条
    url = 'https://www.nature.com'
    search = 'https://www.nature.com/search/ajax'

    # 初始化确定
    def __init__(self, payload={}, filter_table=[]):
        super(Nature, self).__init__()  # 父类初始化
        self.param = {'order': 'relevance'}
        self.payload = payload
        self.format_param()
        self.filter_table = filter_table
        self.cannextpage = True

    def format_param(self):
        if self.payload:
            self.param['q'] = self.payload['key']
            self.param['author'] = self.payload['author']
            self.param['title'] = self.payload['title']
            self.param['date_range'] = self.payload['date_st'] + '-' + self.payload['date_end']
            self.param['page'] = self.payload['page']
            # 去除空键
            for key in list(self.param.keys()):
                if not self.param.get(key):
                    del self.param[key]

    def Search(self, payload={}, search_result={}, filter_table=[]):
        # '''
        # 发送请求爬取数据，包括标题，作者，出版时间，url，并保存到结果表
        # :param: 请求词，爬取结果表，过滤表
        # :return: 更新后的结果表
        # '''

        # cwd = os.getcwd()
        # path = os.path.join(cwd, 'test.html')
        # file = open(path, 'r', encoding='utf-8')
        # html = file.read()
        if self.cannextpage:
            if payload:  # 更新请求参数
                self.payload = payload
                self.format_param()
            if filter_table:  # 更新过滤表
                self.filter_table = filter_table
            # 查询参数传入正常
            if self.param:
                html = self.GET(url=self.search, payload=self.param)
                if html.status_code != 200:
                    self.cannextpage = False
                print(html.url, html.encoding)
                html.encoding = 'utf-8'
                soup = BeautifulSoup(html.text, 'lxml')
                article = soup.findAll('li', attrs={'class': 'mb20 pb20 cleared'})
                log = {}
                for one in article:
                    log['title'] = one.find('a', attrs={'data-track-action': 'search result'}).text.strip()
                    if {'title': log['title']} in self.filter_table:
                        continue
                    alist = one.findAll('li', attrs={'itemprop': 'creator'})
                    log['author'] = []
                    for i in alist:
                        i = i.text.strip(', ')
                        i = i.strip(' & ')
                        log['author'].append(i)
                    log['date'] = one.find('time', attrs={'itemprop': 'datePublished'}).text.strip()
                    log['url'] = self.tolist(
                        self.url + str(one.find('a', attrs={'data-track-action': 'search result'}).get('href')))
                    # print(log)
                    # 在原来结果上添加
                    search_result = self.EMergedict(search_result, log)
                    # print(len(search_result['url']), search_result)
                    # outfile = json_data('11.json')
                    # outfile.write(search_result)
                    log = {}

        return search_result


class Science(HttpServer, Mergedata):
    # web1,从nature获取,一次50条
    search = 'https://w35slb9cf3.execute-api.us-west-1.amazonaws.com/prod/search'

    # 初始化确定
    def __init__(self, payload={}, filter_table=[]):
        super(Science, self).__init__()  # 父类初始化
        self.param = {
            'page': 1,
            'pagesize': 50,
            'orderby': 'tfidf',
            'rules': [
                {
                    'field': 'q', 'value': ''
                },
                {
                    'field': 'title', 'value': ''
                },
                {
                    'field': 'pubdate', 'value': []
                },
                {
                    'field': 'source',
                    'value': '\'sciencemag\' \'Science\' \'Science Advances\' \'Science Signaling\' \'Science Translational Medicine\' \'Science Immunology\' \'Science Robotics\' \'In the Pipeline\' \'Sciencehound\' \'Science Careers Blog\' \'Books, Et Al.\''
                }
            ]
        }
        self.payload = payload
        self.format_param()
        self.filter_table = filter_table
        self.cannextpage = True

    def format_param(self):
        if self.payload:
            self.param['page'] = self.payload['page']
            self.param['rules'] = []
            self.param['rules'].append({
                'field': 'q', 'value': self.payload['key']
            })
            self.param['rules'].append({
                'field': 'title', 'value': self.payload['title']
            })
            self.param['rules'].append({
                'field': 'pubdate', 'value': [self.payload['date_st'], self.payload['date_end']]
            })
            self.param['rules'].append({
                'field': 'author', 'value': [self.payload['date_st'], self.payload['date_end']]
            })
            self.param['rules'].append({
                'field': 'source',
                'value': '\'sciencemag\' \'Science\' \'Science Advances\' \'Science Signaling\' \'Science Translational Medicine\' \'Science Immunology\' \'Science Robotics\' \'In the Pipeline\' \'Sciencehound\' \'Science Careers Blog\' \'Books, Et Al.\''
            })
            # 去除空键
            if self.param['rules']:
                for one in list(self.param['rules']):
                    if not one.get('value'):
                        self.param['rules'].remove(one)
            print(self.param['rules'])

    def Search(self, payload={}, search_result={}, filter_table=[]):
        # '''
        # 发送请求爬取数据，包括标题，作者，出版时间，url，并保存到结果表
        # :param: 请求词，爬取结果表，过滤表
        # :return: 更新后的结果表
        # '''

        # cwd = os.getcwd()
        # path = os.path.join(cwd, 'test.html')
        # file = open(path, 'r', encoding='utf-8')
        # html = file.read()
        if self.cannextpage:
            if payload:  # 更新请求参数
                self.payload = payload
                self.format_param()
            if filter_table:  # 更新过滤表
                self.filter_table = filter_table
            # 查询参数传入正常
            if self.param:
                html = self.POST(url=self.search, json=self.param)
                if html.status_code != 200:
                    self.cannextpage = False
                print(html.url, html.encoding)
                html.encoding = 'utf-8'

                data = json.loads(html.text)
                article = data['hitlist']
                log = {}
                for one in article:
                    if {'title': one['title'][0]} in self.filter_table:
                        continue
                    log['title'] = one['title'][0]
                    log['date'] = one['pubdate'][0]
                    log['author'] = one['authors']
                    log['url'] = 'https:' + one['canonical_url'][0]
                    print(log)
                    # 在原来结果上添加
                    search_result = self.EMergedict(search_result, log)
                    # print(len(search_result['url']), search_result)
                    # outfile = json_data('11.json')
                    # outfile.write(search_result)
                    log = {}

        return search_result
