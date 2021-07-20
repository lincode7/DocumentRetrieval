# -*- coding: utf-8 -*-
import sys, traceback, time, glob, threading, random, os
from Filter.src.function import *
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import pyqtSignal, QThread, Qt, QDate
from PyQt5.QtGui import QIcon, QFontDatabase


# 搜索功能线程
class SearchThread(QThread, somehelp):
    update_date = pyqtSignal(object)  # 定义信号，传出处理数据

    # 初始化，已有搜索结果和过滤表是必要参数
    def __init__(self, filter_table=[]):
        super(SearchThread, self).__init__()
        self.staue = True  # 线程状态，默认永动机（随主线程一直运行）

        self.detect = True  # 是否待机
        self.detect_data = None  # 待检查数据

        self.Data = None  # 总数据
        self.filter_table = filter_table  # 过滤表
        self.nature = Nature()
        self.science = Science()

    def firstsend(self, payload):
        """
            请求新页面，新关键词
        """
        self.Data = {}
        self.detect = False  # 进入工作状态
        self.payload = payload

    def Nextsend(self, search_result, filter_table):
        """
            请求下一页，仅page参数变化
        """
        self.detect = False
        self.payload['page'] += 1
        self.Data = search_result
        self.filter_table = filter_table

    def prepare_search(self, payloads):
        """
            准备搜索
        """
        slist = []  # 子线程列表
        payl = payloads['first']
        payl['type'] = None
        payl['page'] = payloads['page']
        payl['psize'] = payloads['psize']
        payl['date'] = payloads['date']
        payl['order'] = payloads['order']
        slist.append(threading.Thread(target=self.start_search(payl)))

        if payloads['others']:  # advance search
            if 'keyword' in payl:
                del payl['keyword']
            if 'author' in payl:
                del payl['author']
            if 'title' in payl:
                del payl['title']
            for i in payloads['others']:
                payl['type'] = i['logic']
                if 'keyword' in i:
                    payl['keyword'] = i['keyword']
                if 'author' in i:
                    payl['author'] = i['author']
                if 'title' in i:
                    payl['title'] = i['title']
                slist.append(threading.Thread(target=self.start_search(payl)))

            print('advance search')
        else:
            print('one search only')

        for i in slist:
            i.setDaemon(True)
            i.start()
        for i in slist:
            i.join()
        print(self.Data)
        # self.update_date.emit(self.Data)  # 发出爬取数据

    def start_search(self, payl):
        """
            执行搜索
        """
        data = []
        f1 = json_data('nature_result.json')
        data.append(f1.read())
        f1 = json_data('science_result.json')
        data.append(f1.read())
        f1 = json_data('pubs_result.json')
        data.append(f1.read())
        if payl['type'] == 'and':
            super()._andData(data)
        else:
            super()._roughData(data)
        # self.Data.append(self.nature.Search(payload=payl, filter_table=self.filter_table, search_result=self.Data))
        # self.Data.append(self.science.Search(payload=payl, filter_table=self.filter_table, search_result=self.Data))

    def datadetect(self, data=None):
        """
            检查参数，让该线程进行检查，判断是否需要补充数据
        """
        self.detect_data = data

    def run(self):
        while self.staue:
            if self.detect:  # 是否待机
                if self.detect_data:  # 如果有检查需求，就检查
                    '''
                    self.detect_data = [
                        data_len, # 主线程还未被查看的数据量
                        self.onepagemax, # 主线程一页显示上限 
                        self.search_data, # 主线程已有数据
                        self.filter_data.read() # 更新后的过滤表
                    ]
                    '''
                    if self.detect_data[0] - (2 * self.detect_data[1]) < 0:  # 未查看数据量不足2页
                        self.Nextsend(search_result=self.detect_data[2],
                                      filter_table=self.detect_data[3])  # 增加数据
                    self.detect_data = None
                else:
                    print('搜索线程待机中···')
                    time.sleep(0.5)
            elif self.payload:  # 请求需求正常
                print('搜索线程工作中···')
                try:
                    self.prepare_search(self.payload)
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

    def __init__(self):
        super(UIThread, self).__init__()
        self.ui = None
        self.isshow = None
        self.msg = None

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
                    self.update_settext.emit(ui_author[i], text_author[i])
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
        cwd = os.getcwd()
        cwd = cwd[:cwd.find('Filter')]
        ui_path = os.path.join(cwd, r'Filter\resources\ui\UI_Filter_v2.ui')
        img_path = os.path.join(cwd, r'Filter\resources\img\filter.png')
        fonts_path = glob.glob(os.path.join(cwd, r'Filter\resources\font\*.ttf'))
        loadUi(ui_path, self)
        self.setWindowIcon(QIcon(img_path))
        for one in fonts_path:
            QFontDatabase.addApplicationFont(one)

        self.setui()  # ui控件初始化准备
        self.actionlink()  # 控件信号响应

    def setui(self):
        """
            ui控件初始化
        """

        self.check_widget = [
            self.search_1, self.search_2, self.search_3, self.search_4,
            self.search_5, self.search_6, self.search_7, self.search_8,
            self.search_9
        ]  # 搜索栏
        self.check_frame_isshow = []  # 当前显示搜索栏
        self.box_logi = [
            self.logi_1, self.logi_2, self.logi_3, self.logi_4, self.logi_5,
            self.logi_6, self.logi_7, self.logi_8, self.logi_9
        ]  # and or not 选择器
        self.box_key = [
            self.key_1, self.key_2, self.key_3, self.key_4, self.key_5,
            self.key_6, self.key_7, self.key_8, self.key_9
        ]  # 查询词选择器
        self.text_search = [
            self.textsearch_1, self.textsearch_2, self.textsearch_3,
            self.textsearch_4, self.textsearch_5, self.textsearch_6,
            self.textsearch_7, self.textsearch_8, self.textsearch_9
        ]  # 查询字文本输入框

        # right
        self.info_frame = [
            self.frame_1, self.frame_2, self.frame_3, self.frame_4,
            self.frame_5, self.frame_6, self.frame_7, self.frame_8,
            self.frame_9, self.frame_10, self.frame_11, self.frame_12,
            self.frame_13, self.frame_14, self.frame_15
        ]  # 结果显示框
        self.title = [
            self.title_1, self.title_2, self.title_3, self.title_4,
            self.title_5, self.title_6, self.title_7, self.title_8,
            self.title_9, self.title_10, self.title_11, self.title_12,
            self.title_13, self.title_14, self.title_15
        ]  # 每个框的标题显示栏
        self.date = [
            self.date_1, self.date_2, self.date_3, self.date_4, self.date_5,
            self.date_6, self.date_7, self.date_8, self.date_9, self.date_10,
            self.date_11, self.date_12, self.date_13, self.date_14,
            self.date_15
        ]  # 每个框的出版日期显示栏
        self.author = [
            self.author_1, self.author_2, self.author_3, self.author_4,
            self.author_5, self.author_6, self.author_7, self.author_8,
            self.author_9, self.author_10, self.author_11, self.author_12,
            self.author_13, self.author_14, self.author_15
        ]  # 每个框的作者显示栏
        self.url = [
            self.url_1, self.url_2, self.url_3, self.url_4, self.url_5,
            self.url_6, self.url_7, self.url_8, self.url_9, self.url_10,
            self.url_11, self.url_12, self.url_13, self.url_14, self.url_15
        ]  # 每个框的url选择器

        self.dateStart.setDate(QDate.currentDate())  # 设置日期控件为当前时间
        self.dateEnd.setDate(QDate.currentDate())  # 设置日期控件为当前时间

        # 启动默认隐藏控件
        uilist = [
            self.buttonresult,
            self.advance_w, self.search_2, self.search_3,
            self.search_4, self.search_5, self.search_6, self.search_7,
            self.search_8, self.search_9,
            self.right, self.frame_1, self.frame_2, self.frame_3, self.frame_4,
            self.frame_5, self.frame_6, self.frame_7, self.frame_8,
            self.frame_9, self.frame_10, self.frame_11, self.frame_12,
            self.frame_13, self.frame_14, self.frame_15, self.next
        ]
        self.show_hiden(uilist, False)

        # ui更新线程
        self.ui_thread = UIThread()
        # 定义ui隐藏/显示，数据显示信号
        self.ui_thread.update_settext.connect(self.updatesetText)
        self.ui_thread.update_additems.connect(self.updateaddItems)
        self.ui_thread.clear_text.connect(self.clearText)
        self.ui_thread.update_page.connect(self.updatePage)
        self.ui_thread.show_hide.connect(self.show_hiden)

        self.curdate = self.dateStart.date().toString('yyyy/MM/dd')
        self.filter_data = json_data('filter.json')  # 初始过滤表文件

        # 数据格式化参数
        self.count = 0  # 爬取条数
        self.countpage = 0  # 数据总共可以分成多少页，count/onepagemax
        self.seen = 0
        self.alreadypage = 0  # 准备显示的页面
        self.onepagemax = 15  # 一页显示容量
        self.onepage = 0  # 当前一页能显示数量
        self.search_data = {}  # 查询结果

        # 搜索线程
        self.search_thread = SearchThread(filter_table=self.filter_data.read())
        self.search_thread.start()
        # 定义搜索数据更新信号
        self.search_thread.update_date.connect(self.update_search_data)

    def actionlink(self):
        # left
        self.buttonSend.clicked.connect(self.newsearch)
        self.buttonresult.clicked.connect(self.showright)
        self.buttonSetting.clicked.connect(self.showsetting)
        self.buttonFilter.clicked.connect(self.showfilter)
        # advance
        self.buttonExpland.clicked.connect(self.Explanding)
        self.check_add.clicked.connect(self.add_check)
        self.check_dec.clicked.connect(self.dec_check)
        # right
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

    # 普通控件信号响应
    def Explanding(self):
        self.buttonExpland.setEnabled(False)
        if self.advance_w.isHidden():
            if self.check_frame_isshow == []:
                self.check_frame_isshow = [0]
                self.textsearch_1.clear()
                self.search_1.setVisible(True)
            self.advance_w.setVisible(True)
            self.buttonExpland.setText('Advance -')
        else:
            self.ui_thread.show_hide.emit(self.advance_w, False)
            self.buttonExpland.setText('Advance +')
        self.buttonExpland.setEnabled(True)

    def newsearch(self):
        self.buttonSend.setEnabled(False)
        # 开始新的搜索
        self.search_data = {}
        self.count = 0  # 爬取条数
        self.countpage = 0  # 数据总共可以分成多少页，count/onepagemax
        self.seen = 0
        self.alreadypage = 0  # 当前页面
        self.onepagemax = 15  # 一页显示容量
        self.onepage = 0  # 当前一页能显示数量
        '''
payload = {
    'first': {
    'keyword':'',
    'author':'',
    'title':''}, 
    'others': [
     {
        'logic':and\or\not, 
        'key_1':value_1
     },
     ...,
     {
        'logic':and\or\not, 
        'key_9':value_9
     },
    ],
    'page' : 1,
    'psize' : 100,
    'date' : [st, end],
    'order' : 'relevance'
} 
'''
        # 固定搜索栏信息获取 first
        payload = {'first': {
        }, 'others': [], 'page': 1, 'psize': 100, 'date': [], 'order': ''}
        # 基本搜索框
        if self.textsearch_k.text():
            payload['first']['keyword'] = self.textsearch_k.text()
        if self.textsearch_a.text():
            payload['first']['author'] = self.textsearch_a.text()
        if self.textsearch_t.text():
            payload['first']['title'] = self.self.textsearch_t.text()
        # 额外搜索栏信息获取 others
        if self.check_frame_isshow:
            for i in self.check_frame_isshow:
                if self.text_search[i].text():
                    payload['others'].append({
                        'logic':
                            self.box_logi[i].currentText(),
                        self.box_key[i].currentText():
                            self.text_search[i].text()
                    })
        help = somehelp()
        if help.compare_date(self.curdate, self.dateStart.date().toString('yyyy/MM/dd')):
            payload['date'].append(self.dateStart.date().toString('yyyy/MM/dd'))
        if payload['date'] and help.compare_date(self.dateEnd.date().toString('yyyy/MM/dd'),
                                                 self.curdate):  # dateSt正常并且End也正常
            payload['date'].append(self.dateEnd.date().toString('yyyy/MM/dd'))
        payload['order'] = self.order.currentText()
        print(payload)
        if payload['first'] or payload['others']:  # 如果搜索内容不空，进行搜索
            self.search_thread.firstsend(payload=payload)
        else:  # 取消此次搜索
            self.buttonSend.setEnabled(True)

    def showright(self):
        self.ui_thread.show_hide.emit(self.buttonresult, False)
        self.ui_thread.show_hide.emit(self.left, False)
        self.ui_thread.show_hide.emit(self.right, True)

    def showsetting(self):
        self.child1.setWindowModality(Qt.ApplicationModal)  # 子窗口未关闭，父窗口不可点击
        self.child1.show()

    def showfilter(self):
        self.child2.setWindowModality(Qt.ApplicationModal)  # 子窗口未关闭，父窗口不可点击
        self.child2.show()

    def add_check(self):
        self.check_add.setEnabled(False)
        for i in set(range(9)) ^ set(self.check_frame_isshow):  # 对称差集
            self.check_frame_isshow.append(i)
            self.check_widget[i].setVisible(True)
            break
        self.check_add.setEnabled(True)

    def dec_check(self):
        self.check_dec.setEnabled(False)
        if len(self.check_frame_isshow) == 1:
            self.ui_thread.show_hide.emit(self.advance_w, False)
            self.buttonExpland.setText('Advance +')
        else:
            t = list(set(range(9)) & set(self.check_frame_isshow))
            t.reverse()  # 逆序
            for i in t:  # 交集
                self.check_frame_isshow.remove(i)
                self.text_search[i].clear()
                self.check_widget[i].setVisible(False)
                break
        self.check_dec.setEnabled(True)

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
                # 移动到页面顶部
                self.right.verticalScrollBar().setValue(0)
                self.ui_thread.update(uilist=uilist, data=_data)
                self.ui_thread.start()
                # 向搜索线程发送检查数据量请求
                self.search_thread.datadetect([
                    data_len, self.onepagemax, self.search_data,
                    self.filter_data.read()
                ])
                print('现在显示：{}到{}条，共显示{}条'.format(self.seen,
                                                  self.seen + self.onepage,
                                                  len(_data[0])))
                self.seen += self.onepage
                # 在倒数第3页的时候更新查询
            else:
                print('data error')

    def updatesetText(self, ui, text):
        if isinstance(ui, list):
            for i in range(len(text)):
                ui[i].setText(text[i])
                ui[i].adjustSize()
                ui[i].setCursorPosition(0)
        else:
            ui.setText(text)
            ui.adjustSize()
            ui.setCursorPosition(0)

    def updateaddItems(self, ui, text):
        if isinstance(ui, list):
            for i in range(len(text)):
                ui[i].clear()
                ui[i].adjustSize()
                if isinstance(text[i], str):
                    ui.addItem(text[i])
                if isinstance(text[i], list):
                    ui.addItems(text[i])
        else:
            ui.clear()
            ui.adjustSize()
            if isinstance(text, str):
                ui.addItem(text)
            if isinstance(text, list):
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

    def update_search_data(self, data):
        # self.buttonSend.setEnabled(True)
        # file = json_data('test_search.json')
        # _data = file.read()
        canshow = False
        if self.search_data == {}:
            canshow = True
        self.search_data = data
        if self.search_data:
            self.count = len(self.search_data['title'])
        self.countpage = self.count // self.onepagemax
        self.buttonSend.setEnabled(True)
        # 新关键词搜索结果，需要刷新界面
        if canshow:
            if self.left.isVisible():
                self.ui_thread.show_hide.emit(self.left, False)
            if self.advance_w.isVisible():
                self.ui_thread.show_hide.emit(self.advance_w, False)
            if self.right.isHidden():
                self.ui_thread.show_hide.emit(self.right, True)
            print('请求结束，共计获取{}条数据···即将更新界面···'.format(len(data['title'])))
            self.ui_thread.update_page.emit()
        else:
            print('请求结束，共计获取{}条数据···'.format(len(data['title'])))


if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        mw = MainWindow()
        mw.show()
        sys.exit(app.exec_())
    except Exception:
        print(traceback.format_exc())
