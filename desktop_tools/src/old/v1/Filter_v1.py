# -*- coding: utf-8 -*-
import os, sys, traceback, json, datetime, time, glob, requests
from bs4 import BeautifulSoup
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QApplication, QMainWindow, QComboBox
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QFontDatabase


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
        i = cwd.find('desktop_tools')
        cwd = cwd[:i]
        self.file_path = os.path.join(cwd, r'desktop_tools\json', FName)
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
        # :param: conf 覆盖数据，list或dict格式数据
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


# 功能类1，搜索
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
            self.param['q'] = self.payload['keyword']
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
                    log['title'] = one.find('a', attrs={'conf-track-action': 'search result'}).text.strip()
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
                        self.url + str(one.find('a', attrs={'conf-track-action': 'search result'}).get('href')))
                    # print(log)
                    # 在原来结果上添加
                    search_result = self.EMergedict(search_result, log)
                    # print(len(search_result['url']), search_result)
                    # outfile = json_data('11.json')
                    # outfile.write(search_result)
                    log = {}

        return search_result


# 搜索功能线程
class SearchThread(QThread):
    update_date = pyqtSignal(object, bool)  # 定义信号，传出处理数据

    # 初始化，已有搜索结果和过滤表是必要参数
    def __init__(self, payload=None, search_result=None, filter_table=None):
        super(SearchThread, self).__init__()
        self.nature = Nature(payload, filter_table)
        self.search_result = search_result
        self.staue = True  # 线程状态
        self.detect = True  # 是否待机
        self.detect_data = None

    def firstsend(self, payload):
        # 请求新页面，新关键词
        self.detect = False
        self.newsearch = True
        self.payload = payload

    def Nextsend(self, search_result, filter_table):
        # 请求下一页，仅page参数变化
        self.detect = False
        self.newsearch = False
        self.filter_table = filter_table
        self.search_result = search_result
        self.payload['page'] += 1

    def datadetect(self, data=[]):
        # 检查参数，让该线程进行检查，判断是否需要补充数据
        self.detect_data = data

    def run(self):
        while self.staue:
            # 是否待机
            if self.detect:
                # 如果有检查需求，就检查
                if self.detect_data:
                    # data_remaining = self.detect_data[0]
                    # onepagemax = self.detect_data[1]  # 默认20
                    # search_result = self.detect_data[2]
                    # filter_table = self.detect_data[3]
                    # 剩余数据量少于40，就进行数据补充请求
                    if self.detect_data[0] - (2 * self.detect_data[1]) < 0:
                        self.Nextsend(search_result=self.detect_data[2], filter_table=self.detect_data[3])
                    self.detect_data = None
                else:
                    print('搜索线程待机中···')
                    time.sleep(0.5)
            # 请求需求正常
            elif self.payload:
                print('搜索线程工作中···')
                try:
                    if self.newsearch:
                        data = self.nature.Search(payload=self.payload, search_result=self.search_result)
                        time.sleep(0.01)
                        self.update_date.emit(data, True)  # 发出爬取数据
                    else:
                        data = self.nature.Search(payload=self.payload, search_result=self.search_result,
                                                  filter_table=self.filter_table)
                        time.sleep(0.01)
                        self.update_date.emit(data, False)  # 发出爬取数据
                    print('从 nature 获取到数据···')
                    time.sleep(0.01)
                    self.detect = True
                except Exception:
                    print(traceback.format_exc())
                    time.sleep(0.01)
                    self.detect = True
            else:
                print('缺少查询参数！')


# ui刷新线程
class UIThread(QThread):
    update_settext = pyqtSignal(object, object)
    update_additems = pyqtSignal(object, object)
    clear_text = pyqtSignal(object)
    update_page = pyqtSignal()
    show_hide = pyqtSignal(object, bool)

    def __init__(self, parent=None, uilist=None, data=None, isshow=None):
        super().__init__(parent)
        self.ui = uilist
        self.isshow = isshow
        self.msg = data

    def update(self, uilist=None, data=None, isshow=None):
        self.ui = uilist
        self.isshow = isshow
        self.msg = data

    def run(self):  # 重写run方法
        # 设置文本
        if self.msg != None:
            if self.ui and self.msg:
                ui_title = self.ui[0]
                ui_date = self.ui[1]
                ui_author = self.ui[2]
                ui_url = self.ui[3]
                ui_info_frame = self.ui[4]

                text_title = self.msg[0]
                text_date = self.msg[1]
                text_author = self.msg[2]
                text_url = self.msg[3]
                # 隐藏信息框，等待信息刷新
                self.show_hide.emit(ui_info_frame, False)
                # 清除旧文本信息
                self.clear_text.emit(ui_title)
                self.clear_text.emit(ui_date)
                self.clear_text.emit(ui_author)
                self.clear_text.emit(ui_url)
                # 刷新文本信息
                for i in range(len(self.msg[0])):
                    self.update_settext.emit(ui_title[i], text_title[i])
                    self.update_settext.emit(ui_date[i], text_date[i])
                    self.update_additems.emit(ui_author[i], text_author[i])
                    self.update_additems.emit(ui_url[i], text_url[i])
                    # 显示信息框
                    self.show_hide.emit(ui_info_frame[i], True)
                    time.sleep(0.01)
        # 隐藏控件
        elif isinstance(self.isshow, bool) and isinstance(self.ui, list):
            for one in self.ui:
                self.show_hide.emit(one, self.isshow)
                time.sleep(0.01)
        elif isinstance(self.isshow, bool):
            self.show_hide.emit(self.ui, self.isshow)
            time.sleep(0.01)


# GUI
class MainWindow(QMainWindow):
    def __init__(self):
        # """
        # 初始化ui，log.json过滤表文件，准备各个论文网站的会话请求
        # :param: 添加数据项
        # :return: none
        # """
        super(MainWindow, self).__init__()
        # 导入ui、图标、字体
        self.cwd = os.getcwd()
        i = self.cwd.find('desktop_tools')
        self.cwd = self.cwd[:i]
        resrc_path = os.path.join(self.cwd, r'desktop_tools\resources')  # 打包实际路径
        ui_path = os.path.join(resrc_path, r'ui\UI_Filter_v1.ui')
        img = os.path.join(resrc_path, r'img\filter.png')
        fonts = glob.glob(os.path.join(resrc_path, r'font\*.ttf'))
        loadUi(ui_path, self)
        self.setWindowIcon(QIcon(img))
        for one in fonts:
            QFontDatabase.addApplicationFont(os.path.join(resrc_path, one))
        self.setui()
        self.actionlink()

    def setui(self):

        # 需要动态变化的控件列表
        self.title = [self.title_1, self.title_2, self.title_3, self.title_4, self.title_5,
                      self.title_6, self.title_7, self.title_8, self.title_9, self.title_10,
                      self.title_11, self.title_12, self.title_13, self.title_14, self.title_15,
                      self.title_16, self.title_17, self.title_18, self.title_19, self.title_20]
        self.date = [self.date_1, self.date_2, self.date_3, self.date_4, self.date_5, self.date_6,
                     self.date_7, self.date_8, self.date_9, self.date_10, self.date_11, self.date_12,
                     self.date_13, self.date_14, self.date_15, self.date_16, self.date_17,
                     self.date_18, self.date_19, self.date_20]
        self.author = [self.author_1, self.author_2, self.author_3, self.author_4, self.author_5,
                       self.author_6, self.author_7, self.author_8, self.author_9, self.author_10,
                       self.author_11, self.author_12, self.author_13, self.author_14, self.author_15,
                       self.author_16, self.author_17, self.author_18, self.author_19, self.author_20]
        self.url = [self.url_1, self.url_2, self.url_3, self.url_4, self.url_5, self.url_6,
                    self.url_7, self.url_8, self.url_9, self.url_10, self.url_11, self.url_12,
                    self.url_13, self.url_14, self.url_15, self.url_16, self.url_17, self.url_18,
                    self.url_19, self.url_20]
        self.info_frame = [self.frame_1, self.frame_2, self.frame_3, self.frame_4, self.frame_5,
                           self.frame_6,
                           self.frame_7, self.frame_8, self.frame_9, self.frame_10, self.frame_11,
                           self.frame_12, self.frame_13,
                           self.frame_14, self.frame_15, self.frame_16, self.frame_17, self.frame_18,
                           self.frame_19, self.frame_20]
        # 控件初始化
        # 启动默认隐藏控件
        self.show_hiden(self.buttonresult, False)
        self.show_hiden(self.right, False)
        self.show_hiden(self.next, False)
        self.show_hiden(self.info_frame, False)
        # 控件获取默认值
        today = datetime.datetime.today()
        year = today.year
        self.textyearst.setText(str(year))
        self.textyearend.setText(str(year))

        # ui更新线程
        self.ui_thread = UIThread()
        # 定义ui隐藏/显示，数据显示信号
        self.ui_thread.update_settext.connect(self.updatesetText)
        self.ui_thread.update_additems.connect(self.updateaddItems)
        self.ui_thread.clear_text.connect(self.clearText)
        self.ui_thread.update_page.connect(self.updatePage)
        self.ui_thread.show_hide.connect(self.show_hiden)

        # 相关数据
        # 初始过滤表文件
        self.filter_data = json_data('filter.json')
        # 查询结果
        self.search_data = {}
        # 数据格式化参数
        self.count = 0  # 爬取条数
        self.countpage = 0  # 数据总共可以分成多少页，count/onepagemax
        self.seen = 0
        self.alreadypage = 0  # 准备显示的页面
        self.onepagemax = 20  # 一页显示容量
        self.onepage = 20  # 当前一页能显示数量

        # 搜索线程
        self.search_thread = SearchThread(search_result=self.search_data, filter_table=self.filter_data.read())
        self.search_thread.start()
        # 定义搜索数据更新信号
        self.search_thread.update_date.connect(self.update_search_data)

    def actionlink(self):
        # button
        self.buttonSend.clicked.connect(self.newsearch)
        self.buttonresult.clicked.connect(self.showright)
        # self.buttonSetting.clicked.connect(self.showsetting)
        # self.buttonFilter.clicked.connect(self.showfilter)
        self.buttonback.clicked.connect(self.backsearch)
        self.buttonLast.clicked.connect(self.previouspage)
        self.buttonNext.clicked.connect(self.nextpage)

        self.buttonAdd_1.clicked.connect(self.addToFiltertable_1)
        self.buttonAdd_2.clicked.connect(self.addToFiltertable_2)
        self.buttonAdd_3.clicked.connect(self.addToFiltertable_3)
        self.buttonAdd_4.clicked.connect(self.addToFiltertable_4)
        self.buttonAdd_5.clicked.connect(self.addToFiltertable_5)
        self.buttonAdd_6.clicked.connect(self.addToFiltertable_6)
        self.buttonAdd_7.clicked.connect(self.addToFiltertable_7)
        self.buttonAdd_8.clicked.connect(self.addToFiltertable_8)
        self.buttonAdd_9.clicked.connect(self.addToFiltertable_9)
        self.buttonAdd_10.clicked.connect(self.addToFiltertable_10)
        self.buttonAdd_11.clicked.connect(self.addToFiltertable_11)
        self.buttonAdd_12.clicked.connect(self.addToFiltertable_12)
        self.buttonAdd_13.clicked.connect(self.addToFiltertable_13)
        self.buttonAdd_14.clicked.connect(self.addToFiltertable_14)
        self.buttonAdd_15.clicked.connect(self.addToFiltertable_15)
        self.buttonAdd_16.clicked.connect(self.addToFiltertable_16)
        self.buttonAdd_17.clicked.connect(self.addToFiltertable_17)
        self.buttonAdd_18.clicked.connect(self.addToFiltertable_18)
        self.buttonAdd_19.clicked.connect(self.addToFiltertable_19)
        self.buttonAdd_20.clicked.connect(self.addToFiltertable_20)
        self.buttonGo_1.clicked.connect(self.seeEssay_1)
        self.buttonGo_2.clicked.connect(self.seeEssay_2)
        self.buttonGo_3.clicked.connect(self.seeEssay_3)
        self.buttonGo_4.clicked.connect(self.seeEssay_4)
        self.buttonGo_5.clicked.connect(self.seeEssay_5)
        self.buttonGo_6.clicked.connect(self.seeEssay_6)
        self.buttonGo_7.clicked.connect(self.seeEssay_7)
        self.buttonGo_8.clicked.connect(self.seeEssay_8)
        self.buttonGo_9.clicked.connect(self.seeEssay_9)
        self.buttonGo_10.clicked.connect(self.seeEssay_10)
        self.buttonGo_11.clicked.connect(self.seeEssay_11)
        self.buttonGo_12.clicked.connect(self.seeEssay_12)
        self.buttonGo_13.clicked.connect(self.seeEssay_13)
        self.buttonGo_14.clicked.connect(self.seeEssay_14)
        self.buttonGo_15.clicked.connect(self.seeEssay_15)
        self.buttonGo_16.clicked.connect(self.seeEssay_16)
        self.buttonGo_17.clicked.connect(self.seeEssay_17)
        self.buttonGo_18.clicked.connect(self.seeEssay_18)
        self.buttonGo_19.clicked.connect(self.seeEssay_19)
        self.buttonGo_20.clicked.connect(self.seeEssay_20)
        # textedit

        # ↑，ui加载完毕

    # 自定义信号响应
    def updatePage(self):
        data = self.search_data

        data_len = self.count - self.seen  # 还没看过多少条
        self.onepage = min(data_len, self.onepagemax)
        if self.onepage > 0:
            uilist = []
            uilist.append(self.title[0:self.onepage])
            uilist.append(self.date[0:self.onepage])
            uilist.append(self.author[0:self.onepage])
            uilist.append(self.url[0:self.onepage])
            uilist.append(self.info_frame)

            _data = []  # 需要修改
            _data.append(data['title'][self.seen:self.seen + self.onepage])
            _data.append(data['date'][self.seen:self.seen + self.onepage])
            _data.append(data['author'][self.seen:self.seen + self.onepage])
            _data.append(data['url'][self.seen:self.seen + self.onepage])

            if _data[0]:
                self.ui_thread.show_hide.emit(self.next, True)
                self.right.verticalScrollBar().setValue(0);

                self.ui_thread.update(uilist=uilist, data=_data)
                self.ui_thread.start()
                # 向搜索线程发送检查数据量请求
                self.search_thread.datadetect([data_len, self.onepagemax, self.search_data, self.filter_data.read()])
                print('现在显示：{}到{}条，共显示{}条'.format(self.seen, self.seen + self.onepage, len(_data[0])))
                self.seen += self.onepage
                # 在倒数第3页的时候更新查询
            else:
                print('conf error')

    def updatesetText(self, ui, text):
        if isinstance(ui, list):
            for i in range(len(text)):
                ui[i].setText(text[i])
                ui[i].setCursorPosition(0)
        else:
            ui.setText(text)
            ui.setCursorPosition(0)

    def updateaddItems(self, ui, text):
        if isinstance(ui, list):
            for i in range(len(text)):
                ui[i].clear()
                ui[i].addItems(text[i])
        else:
            ui.clear()
            ui.addItems(text)

    def show_hiden(self, ui, flag=True):
        if isinstance(ui, list):
            for one in ui:
                one.setVisible(flag)
        else:
            ui.setVisible(flag)

    def clearText(self, ui):
        if isinstance(ui, list):
            for one in ui:
                one.clear()
        else:
            ui.clear()

    def update_search_data(self, data, canshow=True):
        # self.buttonSend.setEnabled(True)
        # file = json_data('test_search.json')
        # _data = file.read()
        self.search_data = data
        if self.search_data:
            self.count = len(self.search_data['title'])
        self.countpage = self.count // self.onepagemax
        self.buttonSend.setEnabled(True)
        # 新关键词搜索结果，需要刷新界面
        if canshow:
            if self.left.isVisible():
                self.ui_thread.show_hide.emit(self.left, False)
            if self.right.isHidden():
                self.ui_thread.show_hide.emit(self.right, True)
            print('请求结束，共计获取{}条数据···即将更新界面···'.format(len(data['title'])))
            self.ui_thread.update_page.emit()
        else:
            print('请求结束，共计获取{}条数据···'.format(len(data['title'])))

    # 普通控件信号响应
    def newsearch(self):
        self.buttonSend.setEnabled(False)
        # 开始新的搜索
        self.search_data = {}
        self.count = 0  # 爬取条数
        self.countpage = 0  # 数据总共可以分成多少页，count/onepagemax
        self.seen = 0
        self.alreadypage = 0  # 当前页面
        self.onepagemax = 20  # 一页显示容量
        self.onepage = 20  # 当前一页能显示数量

        payload = {}
        payload['keyword'] = self.textkeywords.text()
        payload['title'] = self.texttitle.text()
        payload['author'] = self.textauthor.text()
        payload['date_st'] = self.textyearst.text()
        payload['date_end'] = self.textyearend.text()
        payload['page'] = 1

        self.search_thread.firstsend(payload=payload)

    def showright(self):
        self.ui_thread.show_hide.emit(self.buttonresult, False)
        self.ui_thread.show_hide.emit(self.left, False)
        self.ui_thread.show_hide.emit(self.right, True)

    # def showsetting(self):
    #     print(1)
    #
    # def showfilter(self):
    #     print(1)

    def backsearch(self):
        self.ui_thread.show_hide.emit(self.buttonresult, True)
        self.ui_thread.show_hide.emit(self.right, False)
        self.ui_thread.show_hide.emit(self.left, True)

    def previouspage(self):
        if self.alreadypage > 0:
            self.seen = self.seen - self.onepage - self.onepagemax
            if self.seen < 0:
                self.seen = 0
            self.ui_thread.update_page.emit()
            self.alreadypage -= 1
        else:
            print('当前页面为第一页，没有前页')

    def nextpage(self):
        if self.alreadypage < self.countpage:
            self.alreadypage += 1
            self.ui_thread.update_page.emit()
        else:
            print('数据不足，等待新的请求···')

    def addToFiltertable_1(self):
        # 加入到过滤列表
        # 存在自动跳过
        self.buttonAdd_1.setEnabled(False)
        self.log = {
            'title': self.title_1.text(),  # 标题
        }
        self.filter_data.pich(self.log)
        self.buttonAdd_1.setEnabled(True)

    def addToFiltertable_2(self):
        # 加入到过滤列表
        # 存在自动跳过
        self.buttonAdd_2.setEnabled(False)
        self.log = {
            'title': self.title_2.text(),  # 标题
        }
        self.filter_data.pich(self.log)
        self.buttonAdd_2.setEnabled(True)

    def addToFiltertable_3(self):
        # 加入到过滤列表
        # 存在自动跳过
        self.buttonAdd_3.setEnabled(False)
        self.log = {
            'title': self.title_3.text(),  # 标题
        }
        self.filter_data.pich(self.log)
        self.buttonAdd_3.setEnabled(True)

    def addToFiltertable_4(self):
        # 加入到过滤列表
        # 存在自动跳过
        self.buttonAdd_4.setEnabled(False)
        self.log = {
            'title': self.title_4.text(),  # 标题
        }
        self.filter_data.pich(self.log)
        self.buttonAdd_4.setEnabled(True)

    def addToFiltertable_5(self):
        # 加入到过滤列表
        # 存在自动跳过
        self.buttonAdd_5.setEnabled(False)
        self.log = {
            'title': self.title_5.text(),  # 标题
        }
        self.filter_data.pich(self.log)
        self.buttonAdd_5.setEnabled(True)

    def addToFiltertable_6(self):
        # 加入到过滤列表
        # 存在自动跳过
        self.buttonAdd_6.setEnabled(False)
        self.log = {
            'title': self.title_6.text(),  # 标题
        }
        self.filter_data.pich(self.log)
        self.buttonAdd_6.setEnabled(True)

    def addToFiltertable_7(self):
        # 加入到过滤列表
        # 存在自动跳过
        self.buttonAdd_7.setEnabled(False)
        self.log = {
            'title': self.title_7.text(),  # 标题
        }
        self.filter_data.pich(self.log)
        self.buttonAdd_7.setEnabled(True)

    def addToFiltertable_8(self):
        # 加入到过滤列表
        # 存在自动跳过
        self.buttonAdd_8.setEnabled(False)
        self.log = {
            'title': self.title_8.text(),  # 标题
        }
        self.filter_data.pich(self.log)
        self.buttonAdd_8.setEnabled(True)

    def addToFiltertable_9(self):
        # 加入到过滤列表
        # 存在自动跳过
        self.buttonAdd_9.setEnabled(False)
        self.log = {
            'title': self.title_9.text(),  # 标题
        }
        self.filter_data.pich(self.log)
        self.buttonAdd_9.setEnabled(True)

    def addToFiltertable_10(self):
        # 加入到过滤列表
        # 存在自动跳过
        self.buttonAdd_10.setEnabled(False)
        self.log = {
            'title': self.title_10.text(),  # 标题
        }
        self.filter_data.pich(self.log)
        self.buttonAdd_10.setEnabled(True)

    def addToFiltertable_11(self):
        # 加入到过滤列表
        # 存在自动跳过
        self.buttonAdd_11.setEnabled(False)
        self.log = {
            'title': self.title_11.text(),  # 标题
        }
        self.filter_data.pich(self.log)
        self.buttonAdd_11.setEnabled(True)

    def addToFiltertable_12(self):
        # 加入到过滤列表
        # 存在自动跳过
        self.buttonAdd_12.setEnabled(False)
        self.log = {
            'title': self.title_12.text(),  # 标题
        }
        self.filter_data.pich(self.log)
        self.buttonAdd_12.setEnabled(True)

    def addToFiltertable_13(self):
        # 加入到过滤列表
        # 存在自动跳过
        self.buttonAdd_13.setEnabled(False)
        self.log = {
            'title': self.title_13.text(),  # 标题
        }
        self.filter_data.pich(self.log)
        self.buttonAdd_13.setEnabled(True)

    def addToFiltertable_14(self):
        # 加入到过滤列表
        # 存在自动跳过
        self.buttonAdd_14.setEnabled(False)
        self.log = {
            'title': self.title_14.text(),  # 标题
        }
        self.filter_data.pich(self.log)
        self.buttonAdd_14.setEnabled(True)

    def addToFiltertable_15(self):
        # 加入到过滤列表
        # 存在自动跳过
        self.buttonAdd_15.setEnabled(False)
        self.log = {
            'title': self.title_15.text(),  # 标题
        }
        self.filter_data.pich(self.log)
        self.buttonAdd_15.setEnabled(True)

    def addToFiltertable_16(self):
        # 加入到过滤列表
        # 存在自动跳过
        self.buttonAdd_6.setEnabled(False)
        self.log = {
            'title': self.title_16.text(),  # 标题
        }
        self.filter_data.pich(self.log)
        self.buttonAdd_16.setEnabled(True)

    def addToFiltertable_17(self):
        # 加入到过滤列表
        # 存在自动跳过
        self.buttonAdd_17.setEnabled(False)
        self.log = {
            'title': self.title_17.text(),  # 标题
        }
        self.filter_data.pich(self.log)
        self.buttonAdd_17.setEnabled(True)

    def addToFiltertable_18(self):
        # 加入到过滤列表
        # 存在自动跳过
        self.buttonAdd_18.setEnabled(False)
        self.log = {
            'title': self.title_18.text(),  # 标题
        }
        self.filter_data.pich(self.log)
        self.buttonAdd_18.setEnabled(True)

    def addToFiltertable_19(self):
        # 加入到过滤列表
        # 存在自动跳过
        self.buttonAdd_19.setEnabled(False)
        self.log = {
            'title': self.title_19.text(),  # 标题
        }
        self.filter_data.pich(self.log)
        self.buttonAdd_19.setEnabled(True)

    def addToFiltertable_20(self):
        # 加入到过滤列表
        # 存在自动跳过
        self.buttonAdd_20.setEnabled(False)
        self.log = {
            'title': self.title_20.text(),  # 标题
        }
        self.filter_data.pich(self.log)
        self.buttonAdd_20.setEnabled(True)

    def seeEssay_1(self):
        # '''
        # 在浏览器中查看文章
        # '''
        self.buttonGo_1.setEnabled(False)
        if self.url_1.currentText().strip() != '':
            st = 'start ' + self.url_1.currentText()
            os.system(st)
        self.buttonGo_1.setEnabled(True)

    def seeEssay_2(self):
        # '''
        # 在浏览器中查看文章
        # '''
        self.buttonGo_2.setEnabled(False)
        if self.url_2.currentText().strip() != '':
            st = 'start ' + self.url_2.currentText()
            os.system(st)
        self.buttonGo_2.setEnabled(True)

    def seeEssay_3(self):
        # '''
        # 在浏览器中查看文章
        # '''
        self.buttonGo_3.setEnabled(False)
        if self.url_3.currentText().strip() != '':
            st = 'start ' + self.url_3.currentText()
            os.system(st)
        self.buttonGo_3.setEnabled(True)

    def seeEssay_4(self):
        # '''
        # 在浏览器中查看文章
        # '''
        self.buttonGo_4.setEnabled(False)
        if self.url_4.currentText().strip() != '':
            st = 'start ' + self.url_4.currentText()
            os.system(st)
        self.buttonGo_4.setEnabled(True)

    def seeEssay_5(self):
        # '''
        # 在浏览器中查看文章
        # '''
        self.buttonGo_5.setEnabled(False)
        if self.url_5.currentText().strip() != '':
            st = 'start ' + self.url_5.currentText()
            os.system(st)
        self.buttonGo_5.setEnabled(True)

    def seeEssay_6(self):
        # '''
        # 在浏览器中查看文章
        # '''
        self.buttonGo_6.setEnabled(False)
        if self.url_6.currentText().strip() != '':
            st = 'start ' + self.url_6.currentText()
            os.system(st)
        self.buttonGo_6.setEnabled(True)

    def seeEssay_7(self):
        # '''
        # 在浏览器中查看文章
        # '''
        self.buttonGo_7.setEnabled(False)
        if self.url_7.currentText().strip() != '':
            st = 'start ' + self.url_7.currentText()
            os.system(st)
        self.buttonGo_7.setEnabled(True)

    def seeEssay_8(self):
        # '''
        # 在浏览器中查看文章
        # '''
        self.buttonGo_8.setEnabled(False)
        if self.url_8.currentText().strip() != '':
            st = 'start ' + self.url_8.currentText()
            os.system(st)
        self.buttonGo_8.setEnabled(True)

    def seeEssay_9(self):
        # '''
        # 在浏览器中查看文章
        # '''
        self.buttonGo_9.setEnabled(False)
        if self.url_9.currentText().strip() != '':
            st = 'start ' + self.url_9.currentText()
            os.system(st)
        self.buttonGo_9.setEnabled(True)

    def seeEssay_10(self):
        # '''
        # 在浏览器中查看文章
        # '''
        self.buttonGo_10.setEnabled(False)
        if self.url_10.currentText().strip() != '':
            st = 'start ' + self.url_10.currentText()
            os.system(st)
        self.buttonGo_10.setEnabled(True)

    def seeEssay_11(self):
        # '''
        # 在浏览器中查看文章
        # '''
        self.buttonGo_11.setEnabled(False)
        if self.url_11.currentText().strip() != '':
            st = 'start ' + self.url_11.currentText()
            os.system(st)
        self.buttonGo_11.setEnabled(True)

    def seeEssay_12(self):
        # '''
        # 在浏览器中查看文章
        # '''
        self.buttonGo_12.setEnabled(False)
        if self.url_12.currentText().strip() != '':
            st = 'start ' + self.url_12.currentText()
            os.system(st)
        self.buttonGo_12.setEnabled(True)

    def seeEssay_13(self):
        # '''
        # 在浏览器中查看文章
        # '''
        self.buttonGo_13.setEnabled(False)
        if self.url_13.currentText().strip() != '':
            st = 'start ' + self.url_13.currentText()
            os.system(st)
        self.buttonGo_13.setEnabled(True)

    def seeEssay_14(self):
        # '''
        # 在浏览器中查看文章
        # '''
        self.buttonGo_14.setEnabled(False)
        if self.url_14.currentText().strip() != '':
            st = 'start ' + self.url_14.currentText()
            os.system(st)
        self.buttonGo_14.setEnabled(True)

    def seeEssay_15(self):
        # '''
        # 在浏览器中查看文章
        # '''
        self.buttonGo_15.setEnabled(False)
        if self.url_15.currentText().strip() != '':
            st = 'start ' + self.url_15.currentText()
            os.system(st)
        self.buttonGo_15.setEnabled(True)

    def seeEssay_16(self):
        # '''
        # 在浏览器中查看文章
        # '''
        self.buttonGo_16.setEnabled(False)
        if self.url_16.currentText().strip() != '':
            st = 'start ' + self.url_16.currentText()
            os.system(st)
        self.buttonGo_16.setEnabled(True)

    def seeEssay_17(self):
        # '''
        # 在浏览器中查看文章
        # '''
        self.buttonGo_17.setEnabled(False)
        if self.url_17.currentText().strip() != '':
            st = 'start ' + self.url_17.currentText()
            os.system(st)
        self.buttonGo_17.setEnabled(True)

    def seeEssay_18(self):
        # '''
        # 在浏览器中查看文章
        # '''
        self.buttonGo_18.setEnabled(False)
        if self.url_18.currentText().strip() != '':
            st = 'start ' + self.url_18.currentText()
            os.system(st)
        self.buttonGo_18.setEnabled(True)

    def seeEssay_19(self):
        # '''
        # 在浏览器中查看文章
        # '''
        self.buttonGo_19.setEnabled(False)
        if self.url_19.currentText().strip() != '':
            st = 'start ' + self.url_19.currentText()
            os.system(st)
        self.buttonGo_19.setEnabled(True)

    def seeEssay_20(self):
        # '''
        # 在浏览器中查看文章
        # '''
        self.buttonGo_20.setEnabled(False)
        if self.url_20.currentText().strip() != '':
            st = 'start ' + self.url_20.currentText()
            os.system(st)
        self.buttonGo_20.setEnabled(True)


# Main
if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        mainWindow = MainWindow()
        mainWindow.show()
        sys.exit(app.exec_())
    except Exception:
        print(traceback.format_exc())
