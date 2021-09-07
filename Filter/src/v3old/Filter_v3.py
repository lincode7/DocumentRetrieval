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
        self.source = []
        if _config:
            for source,status in _config.items():
                i = document_source_names.index(source)
                if not status:
                    self.source.append(document_source[i])
        print("-SearchThread init")


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
            self.Data = {'old': {}, 'new': {'flag': False, 'logic': [], 'conf': []}}
            self.ftable = []
            if _data:
                self.Data = {'old': _data, 'new': {'flag': False, 'logic': [], 'conf': []}}
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
        self.Data['new']['conf'].append({'logic': logic, 'conf': data})

    # 待完善
    def _finallData(self):
        """
        整合Data中的new与old
        :return:
        """
        if self.Data['new']['flag']:
            for i in range(len(self.Data['new']['conf'])):
                # 执行数据的and or not
                logic = self.Data['new']['logic'][i]
                data = self.Data['new']['conf'][i]
                print(1)
        else:
            # 简单尾部追加
            # 在self.Data['old']上追加self.Data['new'],然后发出
            for _data in self.Data['new']['conf']:
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

    def run(self):
        if self.mode == 1:  # 设置文本
            self._set_text()
        elif self.mode == 2:  # 隐藏控件
            self._hide_show()

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


class MainApp(QMainWindow):
    config = {}
    work = {}

    def __init__(self):
        super().__init__()
        self.__importResource()  # 加载界面资源,ui,img,font, 初始化self.AppWin成员, 从配置文件加载基本数据
        self.__widgetInit()  # 隐藏部分初始不需要显示的控件
        self.__workPrepare()  # 工作准备初始化
        self.__threadInit()  # 初始化工作线程
        self.__signalInit()  # 信号与槽


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
        if not mainwin.open(QIODevice.ReadOnly):  # 出现ui资源路径异常
            print("Cannot open {}: {}".format("rcc:/widget/MainWin", mainwin.errorString()))
            pass
        self.AppWin = QUiLoader().load(mainwin)  # 导入ui
        mainwin.close()
        print("ui:", True, '\n*****')
        self.AppWin.setWindowIcon(QIcon(":/img/icon"))  # 窗口图标
        # 导入qss,后续可以换肤
        stylesheet = QFile(":/qss/stylesheet")
        if not stylesheet.open(QIODevice.ReadOnly):  # 出现qss资源路径异常
            print("Cannot open {}: {}".format("rcc:/qss/stylesheet", stylesheet.errorString()))
            pass
        self.AppWin.setStyleSheet(str(stylesheet.readAll(), 'utf-8'))
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
        self.AppWin.buttonresult.hide()
        self.AppWin.right.hide()
        self.AppWin.dateStart.setDate(QDate.currentDate())  # 设置日期控件为当前时间
        self.AppWin.dateEnd.setDate(QDate.currentDate())  # 设置日期控件为当前时间
        print('widgetInit success')

    def __signalInit(self):
        self.AppWin.check_add.clicked.connect(self.ClickEvent)
        self.AppWin.buttonSend.clicked.connect(self.ClickEvent)
        self.AppWin.buttonSetting.clicked.connect(self.ClickEvent)
        self.AppWin.buttonFtable.clicked.connect(self.ClickEvent)
        self.AppWin.buttonresult.clicked.connect(self.ClickEvent)
        self.AppWin.buttonback.clicked.connect(self.ClickEvent)
        self.AppWin.buttonNext.clicked.connect(self.ClickEvent)
        self.AppWin.buttonLast.clicked.connect(self.ClickEvent)
        self.search_thread.update_data.connect(self.get_data)
        print('signalInit success')

    def __workPrepare(self):
        # 导入配置参数
        config = QFile(":/config")
        if not config.open(QIODevice.ReadOnly):  # 出现font资源路径异常
            print("Cannot open {}: {}".format(f"rcc:/config", config.errorString()))
            pass
        self.config = json.loads(str(config.readAll(), 'utf-8'))  # 读取配置json文件
        print("config:", True, '\n*****')
        # 提取控件模板
        for win, status in self.config["conf"]["window"].items():
            if status:
                widget = QFile(f":/widget/{win}")
                if not widget.open(QIODevice.ReadOnly):
                    print("Cannot open {}: {}".format(f"rcc:/widget/{win}", widget.errorString()))
                    pass
                self.config["module"][win] = QUiLoader().load(widget)


        # 程序过程中需要的数据
        self.work["filter_table"] = json_data('filter.json')  # 初始过滤表文件
        self.work["search_data"] = []  # 查询结果
        # left, 辅助控件响应
        self.work["checkBtn_add"] = [self.AppWin.check_add]  # 分类-添加一行搜索栏
        self.work["search_info"] = [self.AppWin.simple_search]  # 控件数量动态变化的检索信息：1+的检索词
        # self.static_search_info = [
        #     self.AppWin.dateStart, self.AppWin.dateEnd, self.AppWin.order
        # ]  # 控件固定的检索信息：1起始日期，1截止日期，1数据顺序
        # right, 结果展示参数
        self.work["count"] = 0  # 爬取条数
        self.work["countpage"] = 0  # 数据总共可以分成多少页，count/onepagemax
        self.work["seen"] = 0  # 查看过的数据量
        self.work["alreadypage"] = 0  # 准备显示的页面
        self.work["onepage"] = self.config["conf"]["onepagemax"]  # 当前一页能显示数量
        print('workPrepare success')

    def __threadInit(self):
        self.search_thread = SearchThread(self.config["conf"]["search_rsources"])
        self.ui_thread = UIThread()
        print('threadInit success')

    @Slot()  # @Slot()是一个装饰器，标志着这个函数是一个slot(槽)
    def ClickEvent(self):
        bt = self.AppWin.sender()
        if bt in self.work["checkBtn_add"]:  # 按键属于checkBtn_add类
            self._addcheckline(bt)
        elif bt == self.AppWin.buttonSend:  # 处理查询请求
            self._send(bt)
            print('s')
        elif bt == self.AppWin.buttonSetting:  # 打开设置面板
            print('se')
        elif bt == self.AppWin.buttonFtable:  # 打开过滤表面板
            print('f')
        elif bt == self.AppWin.buttonresult:  # 打开上一查询结果
            self.AppWin.left.setVisible(False)
            self.AppWin.right.setVisible(True)
        elif bt == self.AppWin.buttonback:  # 打开左侧查询面板
            self.AppWin.left.setVisible(True)
            self.AppWin.right.setVisible(False)
            print('back')
        elif bt == self.AppWin.buttonNext:  # 查看下一页数据
            print('next')
        elif bt == self.AppWin.buttonLast:  # 查看上一页数据
            print('last')

    def _addcheckline(self, bt):
        if bt.text() == '+':  # 准备增加一行
            parent = self.AppWin.search  # search：widget
            index = 1  # 默认搜索栏在垂直布局中的下标，在search中的第1项
            offset = len(self.checkBtn_add)  # 存在的额外搜索栏
            index = offset  # 该行插入到上一行后面的位置
            if offset <= self.AppData["maxsearch"]:  # 最大额外搜索栏数量

                # 开始增加一行
                search_widget = QUiLoader().load(QFile(":/widget/SearchWin"))  # 找到一行搜索栏的模板
                st = time.time()
                # search_widget = QUiLoader().load(QFile(":/widget/SearchWin"))  # 找到一行搜索栏的模板
                widget = search_widget
                end = time.time()
                print("spend:", end - st)
                search_widget.setParent(parent)  # 父控件指向search
                parent.layout().insertWidget(index, search_widget)  # 在search布局的上一个搜索框后加入
                search_widget.check_add.clicked.connect(self.ClickEvent)  # 配置按键信号

                # 配置数据变量
                self.checkBtn_add.append(search_widget.check_add)  # 按键归类于checkBtn_add
                self.search_info.append(search_widget)  # 动态增加检索信息框

                # 处理按键stylesheet
                if offset == self.maxtextnum:  # 增加的搜索栏为最后一栏
                    search_widget.check_add.setText('-')  # 按键：+ → 红-
                    # search_widget.check_add.setProperty('bc', 'red')
                    search_widget.check_add.setStyleSheet(
                        '''border-radius: 8px;
                    color: #ffffff;
                    background-color: rgb(218, 121, 123);''')
                if bt == self.AppWin.check_add:  # 默认搜索栏的按键隐藏,该栏不可删除
                    bt.setVisible(False)
                else:  # 上一行额外搜索栏可以删除，按键：+ → 红-
                    bt.setText('-')
                    bt.setStyleSheet('''border-radius: 8px;
                    color: #ffffff;
                    background-color: rgb(218, 121, 123);''')
        elif bt.text() == '-' and bt.parent().objectName(
        ) == 'search_widget':  # 准备删该行，只有额外搜索栏会触发一下，其父控件是search_widget
            i = self.checkBtn_add.index(bt)  # 当前按键所在搜索栏是哪一个
            # 删除该搜索栏
            self.checkBtn_add.remove(bt)  # 从按键类checkBtn_add里删除该按键
            parent = bt.parent()  # 父控件，找到这一行搜索栏
            parent.deleteLater()  # 删除这一行搜罗栏
            # 额外处理
            offset = len(self.checkBtn_add)  # 存在的额外搜索栏数量
            if offset == 1:  # 没有额外搜索栏了
                self.AppWin.check_add.setVisible(True)  # 显示增加搜索栏的按钮

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
                self.AppWin.dateStart.date().toString(
                    'yyyy/MM/dd')) and somehelp.compare_date(
            self.AppWin.dateEnd.date().toString('yyyy/MM/dd'),
            today):  # date range正常
            payload['dateSt'] = self.AppWin.dateStart.date().toString('yyyy/MM/dd')
            payload['dateEnd'] = self.AppWin.dateEnd.date().toString('yyyy/MM/dd')
        # payload['order'] = self.AppWin.order.currentText()

        payload['page'] = 0
        payload['psize'] = 50

        print(payload)
        if payload['rules']:  # 如果搜索规则不空，进行搜索
            self.search_thread.update(_payload=payload, filter_table=self.filter_table)
            self.search_thread.start()
        else:  # 取消此次搜索
            self.buttonSend.setEnabled(True)

    @Slot()
    def get_data(self, data):
        self.result = data

    def showpage(self):
        pass


if __name__ == '__main__':
    st = time.time()  # 程序启动时间戳
    try:
        app = QApplication(sys.argv)
        App = MainApp()
        print('窗口初始化耗时：', time.time() - st)
        App.AppWin.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(traceback.format_exc())
