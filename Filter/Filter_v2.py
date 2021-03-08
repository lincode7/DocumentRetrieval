# -*- coding: utf-8 -*-
import sys, traceback, time, datetime
from function import *

from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import pyqtSignal, QThread, Qt, QDate
from PyQt5.QtGui import QIcon, QFontDatabase


# 搜索功能线程
class SearchThread(QThread):
    update_date = pyqtSignal(object, bool)  # 定义信号，传出处理数据

    # 初始化，已有搜索结果和过滤表是必要参数
    def __init__(self, payload=None, search_result=None, filter_table=None):
        super(SearchThread, self).__init__()
        self.nature = Nature(payload, filter_table)
        self.science = Science(payload, filter_table)
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

    def datadetect(self, data=None):
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
                        # time.sleep(0.01)
                        # data = self.science.Search(payload=self.payload, search_result=self.search_result)
                        time.sleep(0.01)
                        self.update_date.emit(data, True)  # 发出爬取数据
                    else:
                        data = self.nature.Search(payload=self.payload, search_result=self.search_result,
                                                  filter_table=self.filter_table)
                        # time.sleep(0.01)
                        # data = self.science.Search(payload=self.payload, search_result=data,
                        #                           filter_table=self.filter_table)
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
        self.ui = loadUi('./resources/ui/UI_Filter_v2.ui', self)
        self.setWindowIcon(QIcon('./resources/img/filter.png'))
        QFontDatabase.addApplicationFont('./resources/font/*.ttf')

        # 定义子窗口，filter表查看与设置
        self.child1 = SettingWindow()
        self.child2 = FilterWindow()

        # 需要动态变化的控件列表
        # left
        self.check_frame = [self.ui.search_1, self.ui.search_2, self.ui.search_3,
                            self.ui.search_4, self.ui.search_5, self.ui.search_6,
                            self.ui.search_7, self.ui.search_8, self.ui.search_9]
        self.check_frame_isshow = 0
        # right
        self.title = [self.ui.title_1, self.ui.title_2, self.ui.title_3, self.ui.title_4, self.ui.title_5,
                      self.ui.title_6, self.ui.title_7, self.ui.title_8, self.ui.title_9, self.ui.title_10,
                      self.ui.title_11, self.ui.title_12, self.ui.title_13, self.ui.title_14, self.ui.title_15]
        self.date = [self.ui.date_1, self.ui.date_2, self.ui.date_3, self.ui.date_4, self.ui.date_5, self.ui.date_6,
                     self.ui.date_7, self.ui.date_8, self.ui.date_9, self.ui.date_10, self.ui.date_11, self.ui.date_12,
                     self.ui.date_13, self.ui.date_14, self.ui.date_15]
        self.author = [self.ui.author_1, self.ui.author_2, self.ui.author_3, self.ui.author_4, self.ui.author_5,
                       self.ui.author_6, self.ui.author_7, self.ui.author_8, self.ui.author_9, self.ui.author_10,
                       self.ui.author_11, self.ui.author_12, self.ui.author_13, self.ui.author_14, self.ui.author_15]
        self.url = [self.ui.url_1, self.ui.url_2, self.ui.url_3, self.ui.url_4, self.ui.url_5, self.ui.url_6,
                    self.ui.url_7, self.ui.url_8, self.ui.url_9, self.ui.url_10, self.ui.url_11, self.ui.url_12,
                    self.ui.url_13, self.ui.url_14, self.ui.url_15]
        self.info_frame = [self.ui.frame_1, self.ui.frame_2, self.ui.frame_3, self.ui.frame_4, self.ui.frame_5,
                           self.ui.frame_6, self.ui.frame_7, self.ui.frame_8, self.ui.frame_9, self.ui.frame_10,
                           self.ui.frame_11, self.ui.frame_12, self.ui.frame_13, self.ui.frame_14, self.ui.frame_15]
        # 控件初始化
        # 启动默认隐藏控件
        self.show_hiden(self.check_frame, False)  # left
        self.show_hiden(self.ui.buttonsdec, False)  # left
        self.show_hiden(self.ui.buttonresult, False)  # left
        self.show_hiden(self.ui.right, False)  # right
        self.show_hiden(self.ui.next, False)  # right
        self.show_hiden(self.info_frame, False)  # right
        # 设置日期控件默认时间
        today = datetime.datetime.today()
        year = today.year
        month = today.month
        day = today.day
        self.ui.dateStart.setDate(QDate(year, month, day))  # 设置日期
        self.ui.dateEnd.setDate(QDate(year, month, day))  # 设置日期
        # 控件信号响应
        self.actionlink()

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
        # left
        self.ui.buttonSend.clicked.connect(self.newsearch)
        self.ui.buttonsadd.clicked.connect(self.addonesearchcheck)
        self.ui.buttonsdec.clicked.connect(self.deconesearchcheck)
        self.ui.buttonresult.clicked.connect(self.showright)
        self.ui.buttonSetting.clicked.connect(self.showsetting)
        self.ui.buttonFilter.clicked.connect(self.showfilter)
        # right
        self.ui.buttonback.clicked.connect(self.backsearch)
        self.ui.buttonLast.clicked.connect(self.previouspage)
        self.ui.buttonNext.clicked.connect(self.nextpage)
        self.ui.buttonAdd_1.clicked.connect(self.addToFiltertable_1)
        self.ui.buttonAdd_2.clicked.connect(self.addToFiltertable_2)
        self.ui.buttonAdd_3.clicked.connect(self.addToFiltertable_3)
        self.ui.buttonAdd_4.clicked.connect(self.addToFiltertable_4)
        self.ui.buttonAdd_5.clicked.connect(self.addToFiltertable_5)
        self.ui.buttonAdd_6.clicked.connect(self.addToFiltertable_6)
        self.ui.buttonAdd_7.clicked.connect(self.addToFiltertable_7)
        self.ui.buttonAdd_8.clicked.connect(self.addToFiltertable_8)
        self.ui.buttonAdd_9.clicked.connect(self.addToFiltertable_9)
        self.ui.buttonAdd_10.clicked.connect(self.addToFiltertable_10)
        self.ui.buttonAdd_11.clicked.connect(self.addToFiltertable_11)
        self.ui.buttonAdd_12.clicked.connect(self.addToFiltertable_12)
        self.ui.buttonAdd_13.clicked.connect(self.addToFiltertable_13)
        self.ui.buttonAdd_14.clicked.connect(self.addToFiltertable_14)
        self.ui.buttonAdd_15.clicked.connect(self.addToFiltertable_15)
        self.ui.buttonGo_1.clicked.connect(self.seeEssay_1)
        self.ui.buttonGo_2.clicked.connect(self.seeEssay_2)
        self.ui.buttonGo_3.clicked.connect(self.seeEssay_3)
        self.ui.buttonGo_4.clicked.connect(self.seeEssay_4)
        self.ui.buttonGo_5.clicked.connect(self.seeEssay_5)
        self.ui.buttonGo_6.clicked.connect(self.seeEssay_6)
        self.ui.buttonGo_7.clicked.connect(self.seeEssay_7)
        self.ui.buttonGo_8.clicked.connect(self.seeEssay_8)
        self.ui.buttonGo_9.clicked.connect(self.seeEssay_9)
        self.ui.buttonGo_10.clicked.connect(self.seeEssay_10)
        self.ui.buttonGo_11.clicked.connect(self.seeEssay_11)
        self.ui.buttonGo_12.clicked.connect(self.seeEssay_12)
        self.ui.buttonGo_13.clicked.connect(self.seeEssay_13)
        self.ui.buttonGo_14.clicked.connect(self.seeEssay_14)

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
                self.ui_thread.show_hide.emit(self.ui.next, True)
                # 移动到页面顶部
                self.ui.right.verticalScrollBar().setValue(0)
                self.ui_thread.update(uilist=uilist, data=_data)
                self.ui_thread.start()
                # 向搜索线程发送检查数据量请求
                self.search_thread.datadetect([data_len, self.onepagemax, self.search_data, self.filter_data.read()])
                print('现在显示：{}到{}条，共显示{}条'.format(self.seen, self.seen + self.onepage, len(_data[0])))
                self.seen += self.onepage
                # 在倒数第3页的时候更新查询
            else:
                print('data error')

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
        # self.ui.buttonSend.setEnabled(True)
        # file = json_data('test_search.json')
        # _data = file.read()
        self.search_data = data
        if self.search_data:
            self.count = len(self.search_data['title'])
        self.countpage = self.count // self.onepagemax
        self.ui.buttonSend.setEnabled(True)
        # 新关键词搜索结果，需要刷新界面
        if canshow:
            if self.ui.left.isVisible():
                self.ui_thread.show_hide.emit(self.ui.left, False)
            if self.ui.right.isHidden():
                self.ui_thread.show_hide.emit(self.ui.right, True)
            print('请求结束，共计获取{}条数据···即将更新界面···'.format(len(data['title'])))
            self.ui_thread.update_page.emit()
        else:
            print('请求结束，共计获取{}条数据···'.format(len(data['title'])))

    # 普通控件信号响应
    def newsearch(self):
        self.ui.buttonSend.setEnabled(False)
        # 开始新的搜索
        self.search_data = {}
        self.count = 0  # 爬取条数
        self.countpage = 0  # 数据总共可以分成多少页，count/onepagemax
        self.seen = 0
        self.alreadypage = 0  # 当前页面
        self.onepagemax = 20  # 一页显示容量
        self.onepage = 20  # 当前一页能显示数量

        payload = {}
        # if self.ui.textkeywords.text():
        #     payload['key'] = self.ui.textkeywords.text()
        # if self.ui.texttitle.text():
        #     payload['title'] = self.ui.texttitle.text()
        # if self.ui.textauthor.text():
        #     payload['author'] = self.ui.textauthor.text()
        # if self.ui.textyearst.text():
        #     payload['date_st'] = self.ui.textyearst.text()
        # if self.ui.textyearend.text():
        #     payload['date_end'] = self.ui.textyearend.text()
        payload['key'] = self.ui.textkeywords.text()
        payload['title'] = self.ui.texttitle.text()
        payload['author'] = self.ui.textauthor.text()
        payload['date_st'] = self.ui.textyearst.text()
        payload['date_end'] = self.ui.textyearend.text()
        payload['page'] = 1

        # self.search_thread.firstsend(payload=payload)
        print(payload)

    def addonesearchcheck(self):
        if self.check_frame_isshow < 9:
            self.ui_thread.show_hide.emit(self.check_frame[self.check_frame_isshow], True)
            if self.check_frame_isshow == 0:
                self.ui_thread.show_hide.emit(self.ui.buttonsdec, True)
            self.check_frame_isshow += 1
        if self.check_frame_isshow == 9:
            self.ui_thread.show_hide.emit(self.ui.buttonsadd, False)

    def deconesearchcheck(self):
        if self.check_frame_isshow > 0:
            self.check_frame_isshow -= 1
            self.ui_thread.show_hide.emit(self.check_frame[self.check_frame_isshow], False)
        if self.check_frame_isshow == 0:
                self.ui_thread.show_hide.emit(self.ui.buttonsdec, False)

    def showright(self):
        self.ui_thread.show_hide.emit(self.ui.buttonresult, False)
        self.ui_thread.show_hide.emit(self.ui.left, False)
        self.ui_thread.show_hide.emit(self.ui.right, True)

    def showsetting(self):
        self.child1.setWindowModality(Qt.ApplicationModal)  # 子窗口未关闭，父窗口不可点击
        self.child1.show()

    def showfilter(self):
        self.child2.setWindowModality(Qt.ApplicationModal)  # 子窗口未关闭，父窗口不可点击
        self.child2.show()

    def backsearch(self):
        self.ui_thread.show_hide.emit(self.ui.buttonresult, True)
        self.ui_thread.show_hide.emit(self.ui.right, False)
        self.ui_thread.show_hide.emit(self.ui.left, True)

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
        self.ui.buttonAdd_1.setEnabled(False)
        self.log = {
            'title': self.ui.title_1.text(),  # 标题
        }
        self.filter_data.pich(self.log)
        self.ui.buttonAdd_1.setEnabled(True)

    def addToFiltertable_2(self):
        # 加入到过滤列表
        # 存在自动跳过
        self.ui.buttonAdd_2.setEnabled(False)
        self.log = {
            'title': self.ui.title_2.text(),  # 标题
        }
        self.filter_data.pich(self.log)
        self.ui.buttonAdd_2.setEnabled(True)

    def addToFiltertable_3(self):
        # 加入到过滤列表
        # 存在自动跳过
        self.ui.buttonAdd_3.setEnabled(False)
        self.log = {
            'title': self.ui.title_3.text(),  # 标题
        }
        self.filter_data.pich(self.log)
        self.ui.buttonAdd_3.setEnabled(True)

    def addToFiltertable_4(self):
        # 加入到过滤列表
        # 存在自动跳过
        self.ui.buttonAdd_4.setEnabled(False)
        self.log = {
            'title': self.ui.title_4.text(),  # 标题
        }
        self.filter_data.pich(self.log)
        self.ui.buttonAdd_4.setEnabled(True)

    def addToFiltertable_5(self):
        # 加入到过滤列表
        # 存在自动跳过
        self.ui.buttonAdd_5.setEnabled(False)
        self.log = {
            'title': self.ui.title_5.text(),  # 标题
        }
        self.filter_data.pich(self.log)
        self.ui.buttonAdd_5.setEnabled(True)

    def addToFiltertable_6(self):
        # 加入到过滤列表
        # 存在自动跳过
        self.ui.buttonAdd_6.setEnabled(False)
        self.log = {
            'title': self.ui.title_6.text(),  # 标题
        }
        self.filter_data.pich(self.log)
        self.ui.buttonAdd_6.setEnabled(True)

    def addToFiltertable_7(self):
        # 加入到过滤列表
        # 存在自动跳过
        self.ui.buttonAdd_7.setEnabled(False)
        self.log = {
            'title': self.ui.title_7.text(),  # 标题
        }
        self.filter_data.pich(self.log)
        self.ui.buttonAdd_7.setEnabled(True)

    def addToFiltertable_8(self):
        # 加入到过滤列表
        # 存在自动跳过
        self.ui.buttonAdd_8.setEnabled(False)
        self.log = {
            'title': self.ui.title_8.text(),  # 标题
        }
        self.filter_data.pich(self.log)
        self.ui.buttonAdd_8.setEnabled(True)

    def addToFiltertable_9(self):
        # 加入到过滤列表
        # 存在自动跳过
        self.ui.buttonAdd_9.setEnabled(False)
        self.log = {
            'title': self.ui.title_9.text(),  # 标题
        }
        self.filter_data.pich(self.log)
        self.ui.buttonAdd_9.setEnabled(True)

    def addToFiltertable_10(self):
        # 加入到过滤列表
        # 存在自动跳过
        self.ui.buttonAdd_10.setEnabled(False)
        self.log = {
            'title': self.ui.title_10.text(),  # 标题
        }
        self.filter_data.pich(self.log)
        self.ui.buttonAdd_10.setEnabled(True)

    def addToFiltertable_11(self):
        # 加入到过滤列表
        # 存在自动跳过
        self.ui.buttonAdd_11.setEnabled(False)
        self.log = {
            'title': self.ui.title_11.text(),  # 标题
        }
        self.filter_data.pich(self.log)
        self.ui.buttonAdd_11.setEnabled(True)

    def addToFiltertable_12(self):
        # 加入到过滤列表
        # 存在自动跳过
        self.ui.buttonAdd_12.setEnabled(False)
        self.log = {
            'title': self.ui.title_12.text(),  # 标题
        }
        self.filter_data.pich(self.log)
        self.ui.buttonAdd_12.setEnabled(True)

    def addToFiltertable_13(self):
        # 加入到过滤列表
        # 存在自动跳过
        self.ui.buttonAdd_13.setEnabled(False)
        self.log = {
            'title': self.ui.title_13.text(),  # 标题
        }
        self.filter_data.pich(self.log)
        self.ui.buttonAdd_13.setEnabled(True)

    def addToFiltertable_14(self):
        # 加入到过滤列表
        # 存在自动跳过
        self.ui.buttonAdd_14.setEnabled(False)
        self.log = {
            'title': self.ui.title_14.text(),  # 标题
        }
        self.filter_data.pich(self.log)
        self.ui.buttonAdd_14.setEnabled(True)

    def addToFiltertable_15(self):
        # 加入到过滤列表
        # 存在自动跳过
        self.ui.buttonAdd_15.setEnabled(False)
        self.log = {
            'title': self.ui.title_15.text(),  # 标题
        }
        self.filter_data.pich(self.log)
        self.ui.buttonAdd_15.setEnabled(True)

    def seeEssay_1(self):
        # '''
        # 在浏览器中查看文章
        # '''
        self.ui.buttonGo_1.setEnabled(False)
        if self.ui.url_1.currentText().strip() != '':
            st = 'start ' + self.ui.url_1.currentText()
            os.system(st)
        self.ui.buttonGo_1.setEnabled(True)

    def seeEssay_2(self):
        # '''
        # 在浏览器中查看文章
        # '''
        self.ui.buttonGo_2.setEnabled(False)
        if self.ui.url_2.currentText().strip() != '':
            st = 'start ' + self.ui.url_2.currentText()
            os.system(st)
        self.ui.buttonGo_2.setEnabled(True)

    def seeEssay_3(self):
        # '''
        # 在浏览器中查看文章
        # '''
        self.ui.buttonGo_3.setEnabled(False)
        if self.ui.url_3.currentText().strip() != '':
            st = 'start ' + self.ui.url_3.currentText()
            os.system(st)
        self.ui.buttonGo_3.setEnabled(True)

    def seeEssay_4(self):
        # '''
        # 在浏览器中查看文章
        # '''
        self.ui.buttonGo_4.setEnabled(False)
        if self.ui.url_4.currentText().strip() != '':
            st = 'start ' + self.ui.url_4.currentText()
            os.system(st)
        self.ui.buttonGo_4.setEnabled(True)

    def seeEssay_5(self):
        # '''
        # 在浏览器中查看文章
        # '''
        self.ui.buttonGo_5.setEnabled(False)
        if self.ui.url_5.currentText().strip() != '':
            st = 'start ' + self.ui.url_5.currentText()
            os.system(st)
        self.ui.buttonGo_5.setEnabled(True)

    def seeEssay_6(self):
        # '''
        # 在浏览器中查看文章
        # '''
        self.ui.buttonGo_6.setEnabled(False)
        if self.ui.url_6.currentText().strip() != '':
            st = 'start ' + self.ui.url_6.currentText()
            os.system(st)
        self.ui.buttonGo_6.setEnabled(True)

    def seeEssay_7(self):
        # '''
        # 在浏览器中查看文章
        # '''
        self.ui.buttonGo_7.setEnabled(False)
        if self.ui.url_7.currentText().strip() != '':
            st = 'start ' + self.ui.url_7.currentText()
            os.system(st)
        self.ui.buttonGo_7.setEnabled(True)

    def seeEssay_8(self):
        # '''
        # 在浏览器中查看文章
        # '''
        self.ui.buttonGo_8.setEnabled(False)
        if self.ui.url_8.currentText().strip() != '':
            st = 'start ' + self.ui.url_8.currentText()
            os.system(st)
        self.ui.buttonGo_8.setEnabled(True)

    def seeEssay_9(self):
        # '''
        # 在浏览器中查看文章
        # '''
        self.ui.buttonGo_9.setEnabled(False)
        if self.ui.url_9.currentText().strip() != '':
            st = 'start ' + self.ui.url_9.currentText()
            os.system(st)
        self.ui.buttonGo_9.setEnabled(True)

    def seeEssay_10(self):
        # '''
        # 在浏览器中查看文章
        # '''
        self.ui.buttonGo_10.setEnabled(False)
        if self.ui.url_10.currentText().strip() != '':
            st = 'start ' + self.ui.url_10.currentText()
            os.system(st)
        self.ui.buttonGo_10.setEnabled(True)

    def seeEssay_11(self):
        # '''
        # 在浏览器中查看文章
        # '''
        self.ui.buttonGo_11.setEnabled(False)
        if self.ui.url_11.currentText().strip() != '':
            st = 'start ' + self.ui.url_11.currentText()
            os.system(st)
        self.ui.buttonGo_11.setEnabled(True)

    def seeEssay_12(self):
        # '''
        # 在浏览器中查看文章
        # '''
        self.ui.buttonGo_12.setEnabled(False)
        if self.ui.url_12.currentText().strip() != '':
            st = 'start ' + self.ui.url_12.currentText()
            os.system(st)
        self.ui.buttonGo_12.setEnabled(True)

    def seeEssay_13(self):
        # '''
        # 在浏览器中查看文章
        # '''
        self.ui.buttonGo_13.setEnabled(False)
        if self.ui.url_13.currentText().strip() != '':
            st = 'start ' + self.ui.url_13.currentText()
            os.system(st)
        self.ui.buttonGo_13.setEnabled(True)

    def seeEssay_14(self):
        # '''
        # 在浏览器中查看文章
        # '''
        self.ui.buttonGo_14.setEnabled(False)
        if self.ui.url_14.currentText().strip() != '':
            st = 'start ' + self.ui.url_14.currentText()
            os.system(st)
        self.ui.buttonGo_14.setEnabled(True)


class SettingWindow(QMainWindow):
    def __init__(self):
        super(SettingWindow, self).__init__()
        self.ui = loadUi('./resources/ui/UI_setting.ui', self)
        self.setWindowIcon(QIcon('./resources/img/setting.png'))
        # QFontDatabase.addApplicationFont('./resources/ *.ttf')
        self.signal_action()

    def signal_action(self):
        self.ui.buttonset.clicked.connect(self.setsetting)
        self.ui.buttoncancle.clicked.connect(self.close)

    def setsetting(self):
        print(2)


class FilterWindow(QMainWindow):
    def __init__(self):
        super(FilterWindow, self).__init__()
        self.ui = loadUi('./resources/ui/UI_table.ui', self)
        self.setWindowIcon(QIcon('./resources/img/table.png'))
        # QFontDatabase.addApplicationFont('./resources/ *.ttf')
        self.signal_action()

    def signal_action(self):
        self.ui.buttondel.clicked.connect(self.del_data)
        self.ui.buttonclose.clicked.connect(self.close)

    def del_data(self):
        file = json_data('filter.json')
        data = file.read()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())
