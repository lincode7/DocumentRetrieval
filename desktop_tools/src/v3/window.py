#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : window.py
# @Author: 胡煊林
# @Date  : 2021/8/26
# @Desc  : QT界面的控件隐藏、添加、删除、文本更改等

import os,sys,time,glob,json,re
from v3.data import *
from v3.search import *
from PyQt5.uic import loadUi
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class UIThread(QThread):
    """ui刷新线程（常驻）
        description：处理控件的隐藏、文本更改、

        members：
            - set_text : LinEdite和TextEdit的文本更改信号
            - add_items : Combox的选项更改信号
            - clear_text : 控件的文本清空信号
            - update_page : 结果展示控件的页面数据刷新信号
            - show_hide : 控件的显示、隐藏切换信号

            - mode : 功能指示变量
            - pWidget : 父控件
            - cWidget : 控件
            - hWidget : 被隐藏控件
            - isshow : 显示、隐藏指标
            - text : 更新文本

        functions：
            - update : 更新mode
            - setText :
            - hideshow :
    """
    set_text = pyqtSignal(object, object)  # LineEdite或TextEdit等widget的文本设置
    add_items = pyqtSignal(object, object)  # Combox的文本设置
    clear_text = pyqtSignal(object)  # 文本内容清空
    update_page = pyqtSignal()  # 页面刷新
    show_hide = pyqtSignal(object, bool)  # 隐藏\显示widget

    def __init__(self):
        super(UIThread, self).__init__()
        self.mode = None  # 功能模块选择
        self.parentWidget = None  # 父控件
        self.childWidget = None  # 待添加的子控件
        self.hideWidget = None
        self.isshow = None  # 是否显示 bool
        self.data = None  # 数据 conf
        print("-UIThread init")

    def update(self, parentWidget=None, childWidget=None, hideWidget=None, data=None, isshow=None):
        '''
        更新ui刷新子线程的工作模式
        :param parentWidget: 父控件对象
        :param childWidget: 子控件对象
        :param hideWidget: 待隐藏控件对象
        :param data: 待设置文本字典
        :param isshow: 待设置控件隐藏状态
        :return:
        '''
        if parentWidget and data and childWidget:  # 两者不空有成员，功能1启动
            self.mode = 1  # 功能1
            self.data = data
            self.parentWidget = parentWidget
            self.childWidget = childWidget
        elif self.hideWidget and self.isshow:  # 两者不空有成员，功能2启动
            self.mode = 2  # 功能2
            self.hideWidget = hideWidget
            self.isshow = isshow

    def _set_text(self):
        for one in self.data:
            info_widget = self.childWidget

        ui_title = self.parentWidget[0]
        ui_date = self.parentWidget[1]
        ui_author = self.parentWidget[2]
        ui_url = self.parentWidget[3]
        ui_info_widget = self.parentWidget[4]

        text_title = self.data[0]
        text_date = self.data[1]
        text_author = self.data[2]
        text_url = self.data[3]
        # 隐藏信息框，等待信息刷新
        self.show_hide.emit(ui_info_widget, False)
        # 清除旧文本信息
        self.clear_text.emit(ui_title)
        self.clear_text.emit(ui_date)
        self.clear_text.emit(ui_author)
        self.clear_text.emit(ui_url)
        # 设置文本信息
        for i in range(len(self.data[0])):
            self.set_text.emit(ui_title[i], text_title[i])
            self.set_text.emit(ui_date[i], text_date[i])
            self.set_text.emit(ui_author[i], text_author[i])
            self.add_items.emit(ui_url[i], text_url[i])
            # 显示信息框
            self.show_hide.emit(ui_info_widget[i], True)
            time.sleep(0.01)
        # 工作结束恢复
        self.parentWidget = None
        self.childWidget = None
        self.data = None

    def _hide_show(self):
        if isinstance(self.hideWidget, list):
            for one in self.hideWidget:
                self.show_hide.emit(one, self.isshow)
                time.sleep(0.01)
        else:
            self.show_hide.emit(self.hideWidget, self.isshow)
            time.sleep(0.01)
        # 工作结束恢复
        self.hideWidget = None
        self.isshow = None

    def run(self):
        if self.mode == 1:  # 设置文本
            self._set_text()
        elif self.mode == 2:  # 隐藏控件
            self._hide_show()


class MainApp(QMainWindow):
    """主窗口"""
    config = None

    def __init__(self):

        super().__init__()
        self.__importResource()  # 加载界面资源,ui,img,font, 初始化self.AppWin成员, 从配置文件加载基本数据
        self.__widgetInit()  # 隐藏部分初始不需要显示的控件
        self.__workPrepare()  # 工作准备初始化
        self.__threadInit()  # 初始化工作线程
        self.__signalInit()  # 信号与槽

    def __importResource(self):
        # 注册rcc资源 -> true表示成功, 涵盖了ui，图片，字体，qss本地资源
        # rcc_path = "resources/v3old.rcc"
        reg = '(.+desktop_tools)\\.*'
        cwd = re.findall(reg, os.getcwd())[0]
        rcc_path = os.path.join(cwd,r"resources\v3.rcc")
        rcc = QResource.registerResource(rcc_path)
        if not rcc:
            # 出现rcc注册异常
            pass
        print("rcc:", rcc, '\n*****')
        # 导入ui资源
        mainwin = QFile(":/widget/MainWin")
        if not mainwin.open(QIODevice.ReadOnly):  # 出现ui资源路径异常
            print("Cannot open {}: {}".format("rcc:/widget/MainWin", mainwin.errorString()))
            pass
        loadUi(mainwin, self)  # 导入ui
        mainwin.close()
        print("ui:", True, '\n*****')
        self.setWindowIcon(QIcon(":/img/icon"))  # 窗口图标
        # 导入qss,后续可以换肤
        stylesheet = QFile(":/qss/stylesheet")
        if not stylesheet.open(QIODevice.ReadOnly):  # 出现qss资源路径异常
            print("Cannot open {}: {}".format("rcc:/qss/stylesheet", stylesheet.errorString()))
            pass
        self.setStyleSheet(str(stylesheet.readAll(), 'utf-8'))
        stylesheet.close()
        print("stylesheet:", True, '\n*****')
        # 导入字体
        fonts = QResource(":/font/font").children()
        for one in fonts:
            font = QFile(f":/font/font/{one}")
            if not font.open(QIODevice.ReadOnly):  # 出现font资源路径异常
                print("Cannot open {}: {}".format(f"rcc:/font/font/{one}", font.errorString()))
                pass
            i = QFontDatabase.addApplicationFontFromData(font.readAll())
            font.close()
        print("font:", True, '\n*****')
        print('importResource success', '\n------')

    def __widgetInit(self):
        # 隐藏控件
        self.buttonresult.hide()
        self.right.hide()
        # 添加控件
        # f = QFile(":/widget/AllSearchWin")
        # if not f.open(QIODevice.ReadOnly):
        #     pass
        # search_widget = loadUi(f,self.left)
        # f.close()
        # 配置控件
        self.dateStart.setDate(QDate.currentDate())  # 设置日期控件为当前时间
        self.dateEnd.setDate(QDate.currentDate())  # 设置日期控件为当前时间
        print('widgetInit success', '\n------')

    def __signalInit(self):
        # search
        self.check_add.clicked.connect(self.ClickEvent)
        self.buttonSend.clicked.connect(self.ClickEvent)
        # left widget
        self.buttonSetting.clicked.connect(self.ClickEvent)
        self.buttonFtable.clicked.connect(self.ClickEvent)
        self.buttonresult.clicked.connect(self.ClickEvent)
        # right widget
        self.buttonback.clicked.connect(self.ClickEvent)
        self.buttonNext.clicked.connect(self.ClickEvent)
        self.buttonLast.clicked.connect(self.ClickEvent)
        # 自定义信号
        # self.search_thread.update_data.connect(self.get_data)  # 搜索数据返回信号
        # self.ui_thread.update_page.connect(self._updatePage)  # 刷新页面信号
        # self.ui_thread.set_text.connect()  # 设置控件文本信号
        # self.ui_thread.add_items.connect()  # 设置控件文本
        # self.ui_thread.clear_text.connect()  # 情况控件文本信号
        # self.ui_thread.show_hide.connect()  # 隐藏控件文本信号
        print('signalInit success', '\n------')

    def __workPrepare(self):
        # 导入配置参数
        config = QFile(":/config")
        if not config.open(QIODevice.ReadOnly):  # 出现font资源路径异常
            print("Cannot open {}: {}".format(f"rcc:/config", config.errorString()))
            pass
        self.config = json.loads(str(config.readAll(), 'utf-8'))  # 读取配置json文件
        print("config:", True, '\n*****')

        # 程序过程中需要的数据
        self.filter_table = JSONIF('filter.json')  # 初始过滤表文件，自动创建
        self.search_data = []  # 查询结果
        # left, 辅助控件响应
        self.checkBtn_add = [self.check_add]  # 搜索栏添加/删除的按键集合
        self.search_info = [self.simple_search]  # 搜索栏集合
        # right, 结果展示参数
        self.data_offset = 0  # 页面数据起始偏移量，刷新页面时应该显示的第一条数据在结果数据中的位置
        print('workPrepare success', '\n------')

    def __threadInit(self):
        # self.search_thread = SearchThread(self.config["conf"]["search_rsources"])
        # self.ui_thread = UIThread()
        print('threadInit success', '\n------')

    @pyqtSlot()  # @pyqtSlot()()是一个装饰器，标志着这个函数是一个slot(槽)
    def ClickEvent(self):
        bt = self.sender()
        if bt in self.checkBtn_add:  # 按键属于checkBtn_add类
            self._addcheckline(bt)
            # print("add one check line")
        elif bt == self.buttonSend:  # 处理查询请求
            self._send(bt)
            # print("search")
        elif bt == self.buttonSetting:  # 打开设置面板
            print('setting window')
        elif bt == self.buttonFtable:  # 打开过滤表面板
            print('filter table window')
        elif bt == self.buttonresult:  # 打开上一查询结果
            self.left.setVisible(False)
            self.right.setVisible(True)
        elif bt == self.buttonback:  # 打开左侧查询面板
            self.left.setVisible(True)
            self.right.setVisible(False)
            print('back')
        elif bt == self.buttonNext:  # 查看下一页数据
            if self.data_offset >= len(self.result):
                self.ui_thread.update_page.emit()  # 发送更新页面信号
            else:
                print('数据不足，等待新的请求···')
        elif bt == self.buttonLast:  # 查看上一页数据
            if self.data_offset > self.config["conf"]["onepagemax"]:  # 当前页面不是第一页，存在上一页
                if (self.data_offset - self.config["conf"]["onepagemax"]) < 0:
                    self.data_offset = 0;
                self.data_offset -= 1
                self.ui_thread.update_page.emit()  # 发送更新页面信号
            else:
                print('当前页面为第一页，没有前页')

    def _addcheckline(self, bt):
        '''
        动态添加搜索栏，按钮的动态属性切换刷新需要解决
        :param bt:
        :return:
        '''
        if bt.text() == '+':  # 准备增加一行
            parent = self.search  # search：widget
            index = 1  # 默认搜索栏在垂直布局中的下标，在search中的第1项
            offset = len(self.checkBtn_add)  # 存在的额外搜索栏
            index = offset  # 该行插入到上一行后面的位置
            if offset <= self.config["conf"]["maxsearch"]:  # 最大额外搜索栏数量
                # 开始增加一行
                f = QFile(":/widget/SearchWin")
                if not f.open(QIODevice.ReadOnly):
                    pass
                search_widget = loadUi(f)  # 找到一行搜索栏的模板
                f.close()
                self.update()
                search_widget.setParent(parent)  # 父控件指向search
                parent.layout().insertWidget(index, search_widget)  # 在search布局的上一个搜索框后加入
                search_widget.check_add.clicked.connect(self.ClickEvent)  # 配置按键信号

                # 配置数据变量
                self.checkBtn_add.append(search_widget.check_add)  # 按键归类于checkBtn_add
                self.search_info.append(search_widget)  # 动态增加检索信息框

                # 最后一行处理添加按键
                if offset == self.config["conf"]["maxsearch"]:  # 增加的搜索栏为最后一栏
                    search_widget.check_add.setText('X')  # 按键：+ → 红X
                    # search_widget.check_add.setProperty('bc', 'red')
                if bt == self.check_add:  # 默认搜索栏的按键隐藏,该栏不可删除
                    bt.setVisible(False)
                else:  # 上一行额外搜索栏可以删除，按键：+ → 红-
                    bt.setText('X')
                    # bt.setProperty('bc', 'red')
        elif bt.text() == 'X' and bt.parent().objectName(
        ) == 'search_widget':  # 准备删该行，只有额外搜索栏会触发一下，其父控件是search_widget
            # 删除该搜索栏
            self.checkBtn_add.remove(bt)  # 从按键类checkBtn_add里删除该按键
            parent = bt.parent()  # 父控件，找到这一行搜索栏
            parent.deleteLater()  # 界面上删除这一行搜罗栏
            self.search_info.remove(parent)  # 从widget类search_info里删除该搜索栏
            # 额外处理
            offset = len(self.checkBtn_add)  # 存在的额外搜索栏数量
            if offset == 1:  # 没有额外搜索栏了
                self.check_add.setVisible(True)  # 显示增加搜索栏的按钮

    def _send(self, bt):
        bt.setEnabled(False)  # 禁用按钮，避免查询冲突，本次查询结束后恢复
        payload = {}
        payload['rules'] = []  # 搜索规则列表
        for sw in self.search_info:
            logic = sw.findChild(QComboBox, 'logic_box')  # 第一栏没有logic控件，结果为None
            field = sw.findChild(QComboBox, 'range_box')
            text = sw.findChild(QLineEdit, 'textsearch')
            if text.text():  # 搜索框内有字符
                log = {}
                log['logic'] = logic.currentText() if logic else None
                log['field'] = field.currentText()
                log['text'] = text.text()
                payload['rules'].append(log)
        payload['dateSt'] = self.dateStart.date().toString('yyyy/MM/dd')
        payload['dateEnd'] = self.dateEnd.date().toString('yyyy/MM/dd')
        payload['order'] = self.order.currentText()
        payload['page'] = 0
        payload['pagesize'] = self.config["conf"]["search_pagesize"]

        # if payload['rules']:  # 如果搜索规则不空，进行搜索
        #     self.search_thread.update(_payload=payload, filter_table=self.filter_table.read())
        #     self.search_thread.start()
        # else:  # 取消此次搜索
        #     self.buttonSend.setEnabled(True)

        print(payload)
        self.buttonSend.setEnabled(True)

    def _updatePage(self):
        pass
        # data = self.search_data
        #
        # len = len(data)  # 当前搜索结果列表长度
        # onepage = len - self.data_offset  # 列表待查看长度
        # onepage = min(onepage, self.work["conf"]["onepagemax"])  # 当前页面合理显示数据长度
        # if self.onepage > 0:
        #     parentWidget = self.info
        #
        #     _data = []  # 可修改
        #     _data.append(data['title'][self.data_offset:self.data_offset + onepage])
        #     _data.append(data['date'][self.data_offset:self.data_offset + onepage])
        #     _data.append(data['author'][self.data_offset:self.data_offset + onepage])
        #     _data.append(data['url'][self.data_offset:self.data_offset + onepage])
        #
        #     if _data[0]:
        #         self.ui_thread.show_hide.emit(self.next, True)
        #         # 移动到页面顶部
        #         self.right.verticalScrollBar().setValue(0)
        #         self.ui_thread.update(parentWidget=parentWidget, data=_data)
        #         self.ui_thread.start()
        #         # 向搜索线程发送检查数据量请求
        #         self.ui_thread.join()
        #         self.search_thread.update(dect_data={})
        #         print(f'现在显示：{self.data_offset}到{self.data_offset + onepage}条，共显示{len}条')
        #         self.data_offset += onepage
        #         # 在倒数第3页的时候更新查询
        #     else:
        #         print('conf error')

    @pyqtSlot()
    def get_data(self, data:list):
        self.result += data
