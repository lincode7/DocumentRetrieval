# -*- coding: utf-8 -*-
import glob
import sys
import threading
import traceback

from PySide2.QtCore import QThread, Signal, Slot, QDate, QResource, QFile, QIODevice
from PySide2.QtGui import QFontDatabase, QIcon, QImage, QPixmap
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import *
from src.function import *


# 搜索功能线程
class SearchThread(QThread, somehelp):
    update_data = Signal(object)  # 搜索结束返回数据信号

    # 待优化
    def __init__(self, _config=None):
        """
        初始化子线程限制，搜索源
        :param _config: {'maxthread'，'source'}
        """
        super(SearchThread, self).__init__()
        self.mode = None  # 功能
        # 功能1
        self.detect_data = None  # 待检查数据
        # 功能2
        self.payload = None
        self.Data = None  # 待返回数据
        self.ftable = None  # 过滤表
        # 搜索源
        if _config:
            with open(_config, mode='r', encoding='utf-8') as f:
                conf = json.load(f)

        else:
            self.source = [Nature(), Science(), Pubs(), SpLink(), Tandf()]

    def update(self,
               _detect_data=None,
               _payload=None,
               _data=None,
               filter_table=None):
        """
        传入_detect_data执行数据量检测功能；
        传入_payload(必要)和_data(非必要)，filter_table(非必要)执行搜索功能；
        :param _detect_data:待检测数据
        :param _payload:搜索信息
        :param _data:已有的搜多数据，增加同一次搜索的数据量时需要
        :param filter_table:标题过滤表
        :return: None
        """

        # 清空成员，避免update出错
        self.mode = None
        self.Data = None
        self.ftable = None
        self.payload = None
        self.detect_data = None

        if _detect_data:
            self.mode = 1
            self.detect_data = _detect_data
        elif _payload:
            self.mode = 2
            self.payload = _payload
            self.Data = {'old': {}, 'new': {'flag': False, 'logic': [], 'data': []}}
            self.ftable = []
            if _data:
                self.Data = {'old': _data, 'new': {'flag': False, 'logic': [], 'data': []}}
                # old存放相关搜索已有的记录，new存放新的搜索数据，flag标志是否需要高级整合new数据
            if filter_table:
                self.ftable = filter_table
            # 处理一下payload减少不必要的搜索线程（次数），例同时存在一个keyword，author，title
            # efield = []
            # for rule in _payload['rules']:
            #     if 'logic' not in rule and rule['field'] not in efield:
            #         efield.append((rule['field'], _payload['rules'].index(rule)))
            #     elif rule['logic'] == 'AND' and rule['field'] not in efield:
            #         efield.append((rule['field'], _payload['rules'].index(rule)))
            #     else

    def _clear_rules(self):
        '''
        清理搜索规则
        '''
        rules = self.payload['rules']
        key, a, t = ([], [], [])
        for i in rules:
            k = rules[i]['field']
            v = rules[i]['text']

    def _start_search(self, sc, i):
        """
        执行搜索，补充self.Data
        :param sc: 当前搜索指定的搜索源
        :param i: 当前搜索执行payload['rules']中的第i条rule,同时表示第几行有效搜索栏
        :return:
        """
        payl = {}
        k = self.payload['rules'][i]['field']
        v = self.payload['rules'][i]['text']
        payl[k] = v
        payl['dateSt'] = self.payload['dateSt']
        payl['dateEnd'] = self.payload['dateEnd']
        payl['order'] = self.payload['order']
        logic = None
        data = None
        data = sc.search(payload=payl, filter_table=self.ftable)
        # sc.testparam(payl=payl)  # 测试执行效果
        if i > 0:  # 第2行开始搜索栏存在logic字段
            if not self.Data['new']['flag']:
                self.Data['new']['flag'] = True  # 高级数据整合标志
            logic = self.payload['rules'][i]['logic']
        self.Data['new']['logic'].append(logic)
        self.Data['new']['data'].append({'logic': logic, 'data': data})

    # 待完善
    def _finallData(self):
        """
        整合Data中的new与old
        :return:
        """
        if self.Data['new']['flag']:
            for i in range(len(self.Data['new']['data'])):
                # 执行数据的and or not
                logic = self.Data['new']['logic'][i]
                data = self.Data['new']['data'][i]
                print(1)
        else:
            # 简单尾部追加
            # 在self.Data['old']上追加self.Data['new'],然后发出
            for _data in self.Data['new']['data']:
                for one in _data:
                    data = super().AddOneData(self.Data['old'], _data)
        self.update_data.emit(data)  # 返回数据，本次线程工作结束

    # 待优化,判断rules中同时出现1个keyword，1个author，1个title只需要进行一次search而不是3次
    def _search(self):
        # step1
        stlist = []  # search thread list
        for one in self.source:
            for i in range(len(self.payload['rules'])):
                st = threading.Thread(target=self._start_search(one, i))  # 在one中执行第i行搜索栏的搜索
                st.setDaemon(True)  # 守护线程，后台线程，搜索结果数据不保留本地，主程序关闭后强制关闭搜索线程
                st.start()
                stlist.append(st)
                # maxthread -= 1
        for st in stlist:  # 等待所有搜索线程搜索结束
            st.join()
            # maxthread += 1
        # step2
        self._finallData()  # 搜索结束整合self.Data并发送到主线程

    # 待完善
    def _detect(self):
        """
        detect_data = {
            'data_len',     # 主线程还未被查看的数据量
            'onepagemax',   # 主线程一页显示上限
            'search_data',  # 主线程已有数据
            'filter_table'  # 过滤表
        }
        """
        if self.detect_data['data_len'] - (
                2 * self.detect_data['onepagemax']) < 0:  # 未查看数据量不足2页,需要补充数据
            # 增加数据
            print(1)

    def run(self):
        if self.mode == 1:
            self._detect()
        elif self.mode == 2:
            self._search()


# ui刷新线程
class UIThread(QThread):
    set_text = Signal(object, object)  # LineEdite或TextEdit等widget的文本设置
    add_items = Signal(object, object)  # Combox的文本设置
    clear_text = Signal(object)  # 文本内容清空
    # update_page = Signal()            # 页面刷新
    show_hide = Signal(object, bool)  # 隐藏\显示widget

    def __init__(self):
        super(UIThread, self).__init__()
        self.mode = None  # 功能模块选择
        self.ui = None  # widget或widget列表
        self.isshow = None  # 是否显示 bool
        self.msg = None  # 数据 data

    def update(self, uilist=None, data=None, isshow=None):
        self.ui = uilist
        self.isshow = isshow
        self.msg = data
        if self.ui and self.msg:  # 两者不空有成员，功能1启动
            self.mode = 1  # 功能1
        elif self.ui and self.isshow:  # 两者不空有成员，功能2启动
            self.mode = 2  # 功能2

    def run(self):
        if self.mode == 1:  # 设置文本
            self._set_text()
        elif self.mode == 2:  # 隐藏控件
            self._hide_show()

    # 待完善
    def _set_text(self):

        ui_title = self.ui[0]
        ui_date = self.ui[1]
        ui_author = self.ui[2]
        ui_url = self.ui[3]
        ui_info_widget = self.ui[4]

        text_title = self.msg[0]
        text_date = self.msg[1]
        text_author = self.msg[2]
        text_url = self.msg[3]
        # 隐藏信息框，等待信息刷新
        self.show_hide.emit(ui_info_widget, False)
        # 清除旧文本信息
        self.clear_text.emit(ui_title)
        self.clear_text.emit(ui_date)
        self.clear_text.emit(ui_author)
        self.clear_text.emit(ui_url)
        # 设置文本信息
        for i in range(len(self.msg[0])):
            self.set_text.emit(ui_title[i], text_title[i])
            self.set_text.emit(ui_date[i], text_date[i])
            self.set_text.emit(ui_author[i], text_author[i])
            self.add_items.emit(ui_url[i], text_url[i])
            # 显示信息框
            self.show_hide.emit(ui_info_widget[i], True)
            time.sleep(0.01)
        # 清空成员，避免下一次update出错
        self.ui = None
        self.msg = None

    def _hide_show(self):
        if isinstance(self.ui, list):
            for one in self.ui:
                self.show_hide.emit(one, self.isshow)
                time.sleep(0.01)
        else:
            self.show_hide.emit(self.ui, self.isshow)
            time.sleep(0.01)


class MainApp(QMainWindow):
    def __init__(self):
        super(MainApp, self).__init__()
        # self.__setup()  # 从配置文件加载基本数据
        self.__importResource()  # 加载界面资源,ui,img,font
        # self.__widgetInit()  # 隐藏部分初始不需要显示的控件
        # self.__signalInit()  # 信号与槽
        # self.__workprepare()  # 工作准备初始化
        # self.__threadInit()  # 初始化工作线程

    def __setup(self):
        self.info = None
        self.ui = None
        self.data = None
        self.work = None

    def __importResource(self):
        # 注册rcc资源 -> true表示成功, 涵盖了ui，图片，字体，qss本地资源
        rcc_path = os.path.join(os.getcwd(), r"resources\v3.rcc")
        # rcc = QResource(rcc_path)
        rcc = QResource.registerResource(rcc_path)
        print("rcc:", rcc, '\n*****')
        if not rcc:
            # 出现rcc注册异常
            pass
        # 导入ui资源
        mainwin = QFile(":/widget/MainWin")
        if not mainwin.open(QIODevice.ReadOnly):
            # 出现ui资源路径异常
            print("Cannot open {}: {}".format("rcc:/widget/MainWin", mainwin.errorString()))
            pass
        self.ui = QUiLoader().load(mainwin, self)  # 导入ui
        mainwin.close()
        print("ui:", True, '\n*****')
        # 导入qss,后续可以换肤
        stylesheet = QFile(":/qss/stylesheet")
        if not stylesheet.open(QIODevice.ReadOnly):
            # 出现qss资源路径异常
            print("Cannot open {}: {}".format("rcc:/qss/stylesheet", stylesheet.errorString()))
            pass
        self.ui.setStyleSheet(str(stylesheet.readAll(), 'utf-8'))
        stylesheet.close()
        print("stylesheet:", True, '\n*****')
        # 导入字体
        fonts = QResource(":/font/font").children()
        for one in fonts:
            font = QFile(f":/font/font/{one}")
            if not font.open(QIODevice.ReadOnly):
                # 出现font资源路径异常
                print("Cannot open {}: {}".format(f"rcc:/font/font/{one}", font.errorString()))
                pass
            i = QFontDatabase.addApplicationFontFromData(font.readAll())
            font.close()
        print("font:", True, '\n*****')
        self.ui.setWindowIcon(QIcon(":/img/ico"))  # 窗口图标
        self.ui.buttonSetting.setIcon(QIcon(":/img/settingBtn"))  # 按键图标
        self.ui.buttonFtable.setIcon(QIcon(":/img/tableBtn"))  # 按键图标
        print('importResource success')

    def __widgetInit(self):
        self.ui.buttonresult.hide()
        self.ui.right.hide()

        self.ui.dateStart.setDate(QDate.currentDate())  # 设置日期控件为当前时间
        self.ui.dateEnd.setDate(QDate.currentDate())  # 设置日期控件为当前时间
        print('_widgetInit')

    def __signalInit(self):
        self.ui.check_add.clicked.connect(self.ClickEvent)
        self.ui.buttonSend.clicked.connect(self.ClickEvent)
        self.ui.buttonSetting.clicked.connect(self.ClickEvent)
        self.ui.buttonFtable.clicked.connect(self.ClickEvent)
        self.ui.buttonresult.clicked.connect(self.ClickEvent)
        self.ui.buttonback.clicked.connect(self.ClickEvent)
        self.ui.buttonNext.clicked.connect(self.ClickEvent)
        self.ui.buttonLast.clicked.connect(self.ClickEvent)
        print('_signalInit')

    def __workprepare(self):
        # 程序过程中需要的数据
        self.filter_table = json_data('filter.json')  # 初始过滤表文件
        self.search_data = []  # 查询结果

        # left
        self.maxtextnum = 10  # 搜索栏上限，默认10个
        self.check_add = [self.ui.check_add]  # 分类-添加一行搜索栏
        self.search_info = [self.ui.simple_search]  # 控件数量动态变化的检索信息：1+的检索词
        # self.static_search_info = [
        #     self.ui.dateStart, self.ui.dateEnd, self.ui.order
        # ]  # 控件固定的检索信息：1起始日期，1截止日期，1数据顺序
        # right
        self.onepagemax = 25  # 一页显示容量

        # self.count = None  # 爬取条数
        # self.countpage = None  # 数据总共可以分成多少页，count/onepagemax
        # self.seen = None  # 查看过的数据量
        # self.alreadypage = None  # 准备显示的页面
        # self.onepage = None  # 当前一页能显示数量

    def __threadInit(self):
        self.search_thread = SearchThread()
        self.search_thread.update_data.connect(self.get_data)
        print('_threadInit')

    @Slot()  # @Slot()是一个装饰器，标志着这个函数是一个slot(槽)
    def ClickEvent(self):
        bt = self.sender()
        if bt in self.check_add:  # 按键属于check_add类
            self._addcheckline(bt)
        elif bt == self.ui.buttonSend:  # 处理查询请求
            self._send(bt)
            print('s')
        elif bt == self.ui.buttonSetting:  # 打开设置面板
            print('se')
        elif bt == self.ui.buttonFtable:  # 打开过滤表面板
            print('f')
        elif bt == self.ui.buttonresult:  # 打开上一查询结果
            self.ui.left.setVisible(False)
            self.ui.right.setVisible(True)
        elif bt == self.ui.buttonback:  # 打开左侧查询面板
            self.ui.left.setVisible(True)
            self.ui.right.setVisible(False)
            print('back')
        elif bt == self.ui.buttonNext:  # 查看下一页数据
            print('next')
        elif bt == self.ui.buttonLast:  # 查看上一页数据
            print('last')

    def _addcheckline(self, bt):
        if bt.text() == '+':  # 准备增加一行
            parent = self.ui.search  # search：widget
            index = 1  # 默认搜索栏在垂直布局中的下标，在search中的第1项
            offset = len(self.check_add)  # 存在的额外搜索栏
            index = offset  # 该行插入到上一行后面的位置
            if offset <= self.maxtextnum:  # 最大额外搜索栏数量

                # 开始增加一行
                search_widget = QUiLoader().load(QFile(":/widget/ui/search_widget.ui"))  # 找到一行搜索栏的模板
                search_widget.setParent(parent)  # 父控件指向search
                parent.layout().insertWidget(
                    index, search_widget)  # 在search布局的上一个搜索框后加入

                # 配置按键信号
                search_widget.check_add.clicked.connect(
                    self.ClickEvent)  # 配置按键信号

                # 配置数据变量
                self.check_add.append(
                    search_widget.check_add)  # 按键归类于check_add
                self.search_info.append(search_widget)  # 动态增加检索信息框

                # 处理按键stylesheet
                if offset == self.maxtextnum:  # 增加的搜索栏为最后一栏
                    search_widget.check_add.setText('-')  # 按键：+ → 红-
                    # search_widget.check_add.setProperty('bc', 'red')
                    search_widget.check_add.setStyleSheet(
                        '''border-radius: 8px;
                    color: #ffffff;
                    background-color: rgb(218, 121, 123);''')
                if bt == self.ui.check_add:  # 默认搜索栏的按键隐藏,该栏不可删除
                    bt.setVisible(False)
                else:  # 上一行额外搜索栏可以删除，按键：+ → 红-
                    bt.setText('-')
                    bt.setStyleSheet('''border-radius: 8px;
                    color: #ffffff;
                    background-color: rgb(218, 121, 123);''')
        elif bt.text() == '-' and bt.parent().objectName(
        ) == 'search_widget':  # 准备删该行，只有额外搜索栏会触发一下，其父控件是search_widget
            i = self.check_add.index(bt)  # 当前按键所在搜索栏是哪一个
            # 删除该搜索栏
            self.check_add.remove(bt)  # 从按键类check_add里删除该按键
            parent = bt.parent()  # 父控件，找到这一行搜索栏
            parent.deleteLater()  # 删除这一行搜罗栏
            # 额外处理
            offset = len(self.check_add)  # 存在的额外搜索栏数量
            if offset == 1:  # 没有额外搜索栏了
                self.ui.check_add.setVisible(True)  # 显示增加搜索栏的按钮

    def _send(self, bt):
        bt.setEnabled(False)  # 禁用按钮，避免查询冲突，本次查询结束后恢复
        payload = {}
        payload['rules'] = []  # 搜索规则列表
        for sw in self.search_info:
            lgoic = sw.findChild(QComboBox, 'logic_box')
            field = sw.findChild(QComboBox, 'range_box')
            text = sw.findChild(QLineEdit, 'textsearch')
            if field and text:
                if text.text():  # 搜索框内有字符
                    log = {}
                    if lgoic:  # 是否复杂查询
                        log['logic'] = lgoic.currentText()
                    log['field'] = field.currentText()
                    log['text'] = text.text()
                    payload['rules'].append(log)
        today = QDate.currentDate().toString('yyyy/MM/dd')
        if somehelp.compare_date(
                today,
                self.ui.dateStart.date().toString(
                    'yyyy/MM/dd')) and somehelp.compare_date(
            self.ui.dateEnd.date().toString('yyyy/MM/dd'),
            today):  # date range正常
            payload['dateSt'] = self.ui.dateStart.date().toString('yyyy/MM/dd')
            payload['dateEnd'] = self.ui.dateEnd.date().toString('yyyy/MM/dd')
        # payload['order'] = self.ui.order.currentText()

        payload['page'] = 0
        payload['psize'] = 50

        print(payload)
        if payload['rules']:  # 如果搜索规则不空，进行搜索
            self.search_thread.update(_payload=payload, filter_table=self.filter_table)
            self.search_thread.start()
        else:  # 取消此次搜索
            self.buttonSend.setEnabled(True)

    @Slot()
    def get_data(self):
        print(1)


if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        App = MainApp()
        App.ui.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(traceback.format_exc())
