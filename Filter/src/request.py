# -*- coding: utf-8 -*-
import os, json, requests, time, datetime
from bs4 import BeautifulSoup
from Filter.src.otherfuc import *
from Filter.src.data import *

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
class Nature(HttpServer):
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


class Science(HttpServer):
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
class Science2(HttpServer):
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


class Pubs(HttpServer):
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


class SpLink(HttpServer):
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


class Tandf(HttpServer):
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
