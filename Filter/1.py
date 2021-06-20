# -*- coding: utf-8 -*-
import sys, glob, os
from PySide2.QtCore import QFile, QIODevice
from PySide2.QtGui import QFontDatabase, QIcon
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QMainWindow, QApplication


class MainApp(QMainWindow):
    def __init__(self):
        super(MainApp, self).__init__()
        self.importResource()
        self.hideWidget()
        self.actions()
        self.datainit()

    # 动态加载ui
    def importResource(self):
        ui_path = r'.\resources\ui\untitled.ui'
        img = r'.\resources\img\filter.png'
        fonts = glob.glob(r'.\resources\font\*.ttf')
        # 导入ui
        ui_file = QFile(ui_path)
        if not ui_file.open(QIODevice.ReadOnly):
            print("Cannot open {}: {}".format(ui_path, ui_file.errorString()))
            sys.exit(-1)
        loader = QUiLoader()
        self.ui = loader.load(ui_file,self)
        ui_file.close()
        if not self:
            print(loader.errorString())
            sys.exit(-1)
        # 导入图标
        self.setWindowIcon(QIcon(img))
        # 导入字体
        for one in fonts:
            QFontDatabase.addApplicationFont(one)

    def hideWidget(self):
        self.ui.search.setVisible(False)
        print('h')

    def actions(self):
        self.ui.ASbutton.clicked.connect(self.ExpendAS)
        print('a')

    def datainit(self):
        print('d')

    def ExpendAS(self):
        bt = self.sender()
        if bt == self.ui.ASbutton:
            if bt.text() == '+':
                bt.setText('-')
                self.ui.search.setVisible(True)
            elif bt.text() == '-':
                bt.setText('+')
                self.ui.search.setVisible(False)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = MainApp()
    gui.ui.show()
    sys.exit(app.exec_())